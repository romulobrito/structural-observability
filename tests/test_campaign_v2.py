#!/usr/bin/env python3
"""Tests for generic automatic and decomposed campaign services."""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path

from structural_obs.tearing.cases.injection_system import load_injection_system
from structural_obs.tearing.cases.system_model import (
    StructuralSystemData,
    normalize_declared_duplicates,
)
from structural_obs.tearing.core import TearingConfig, classify_tearing
from structural_obs.toolkit.schemas.campaign_schema import (
    CampaignDefinition,
    CampaignSolverConfig,
    CampaignStage,
    load_campaign,
)
from structural_obs.toolkit.services import additive_campaign as campaign_service
from structural_obs.toolkit.services.additive_campaign import run_additive_campaign
from structural_obs.toolkit.services.candidate_generation import (
    CandidateSuggestion,
    automatic_candidate_tiers,
)
from structural_obs.toolkit.services.campaign_checkpoint import canonical_sha256
from structural_obs.toolkit.services.campaign_xlsx import (
    load_campaign_report,
    write_campaign_artifacts,
)
from structural_obs.toolkit.services.incidence_components import (
    merge_placement_results,
    merge_tearing_results,
    partition_incidence_components,
)
from structural_obs.toolkit.services.integrated_sensor_placement import (
    solve_integrated_sensor_placement,
)
from structural_obs.toolkit.services.solver_retry import run_with_adaptive_retry


def _synthetic_source() -> StructuralSystemData:
    equations = {
        "Eq1": ["x", "u"],
        "Eq2": ["y", "v"],
    }
    return StructuralSystemData(
        profile="synthetic",
        equations=equations,
        variables=("u", "v", "x", "y"),
        installed_sensors=frozenset(),
        known_constants=frozenset(),
        calculated_outputs=frozenset({"x", "y"}),
        blocks={"all": ("Eq1", "Eq2")},
        allowed_outputs={
            "Eq1": frozenset({"x"}),
            "Eq2": frozenset({"y"}),
        },
        duplicate_equation_groups=(),
    )


def _synthetic_campaign() -> CampaignDefinition:
    return CampaignDefinition(
        schema_version="1.1",
        campaign_id="synthetic",
        name="Synthetic",
        source_profile="synthetic",
        candidate_mode="automatic",
        default_target_profile="calculated_outputs",
        stages=(
            CampaignStage(
                stage_id="all",
                name="All",
                block_id="all",
            ),
        ),
        sensor_costs={},
        solver=CampaignSolverConfig(
            time_limit_s=10.0,
            retry_time_limits_s=(10.0,),
            decompose_components=True,
        ),
        source_path="synthetic.yaml",
    )


def test_declared_duplicate_normalization_is_explicit() -> None:
    source = load_injection_system()
    normalized, removed = normalize_declared_duplicates(source)
    assert len(source.equations) == 207
    assert len(normalized) == 202
    assert removed == ("Eq163", "Eq164", "Eq165", "Eq166", "Eq167")
    assert {
        variable
        for values in normalized.values()
        for variable in values
    } == set(source.variables)


def test_automatic_candidate_tiers_expand_deterministically() -> None:
    suggestions = (
        CandidateSuggestion("near", ("target_dependency",), 1),
        CandidateSuggestion("middle", ("target_dependency",), 2),
        CandidateSuggestion("far", ("open_tear",), 3),
    )
    assert automatic_candidate_tiers(suggestions) == (
        frozenset({"near"}),
        frozenset({"near", "middle"}),
        frozenset({"near", "middle", "far"}),
    )


def test_decomposed_models_match_monolithic_minimum() -> None:
    source = _synthetic_source()
    config = TearingConfig(time_limit_s=10.0, require_optimal=True)
    monolithic_classification = classify_tearing(
        source.equations,
        set(),
        allowed_outputs={
            name: set(values)
            for name, values in source.allowed_outputs.items()
        },
        config=config,
    )
    components = partition_incidence_components(source.equations)
    classification_parts = [
        classify_tearing(
            component.equations,
            set(),
            allowed_outputs={
                name: set(source.allowed_outputs[name])
                for name in component.equations
            },
            config=config,
        )
        for component in components
    ]
    merged_classification = merge_tearing_results(
        "merged",
        classification_parts,
    )
    assert (
        merged_classification.n_closed_coverage
        == monolithic_classification.n_closed_coverage
    )

    monolithic_placement = solve_integrated_sensor_placement(
        source.equations,
        set(),
        {"u", "v"},
        {"x", "y"},
        allowed_outputs={
            name: set(values)
            for name, values in source.allowed_outputs.items()
        },
        config=config,
    )
    placement_parts = [
        solve_integrated_sensor_placement(
            component.equations,
            set(),
            {"u", "v"} & set(component.variables),
            {"x", "y"} & set(component.variables),
            allowed_outputs={
                name: set(source.allowed_outputs[name])
                for name in component.equations
            },
            config=config,
        )
        for component in components
    ]
    merged_placement = merge_placement_results("merged", placement_parts)
    assert merged_placement.minimum_certified
    assert merged_placement.selected_cost == monolithic_placement.selected_cost
    assert set(merged_placement.selected_sensors) == {"u", "v"}


def test_automatic_campaign_and_signature_resume(monkeypatch) -> None:
    campaign = _synthetic_campaign()
    first = run_additive_campaign(
        campaign,
        source=_synthetic_source(),
        mode="optimize",
    )
    assert first.stages[0].global_certificate == "certified"
    assert set(first.stages[0].placement.selected_sensors) == {"u", "v"}

    def _unexpected_call(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("Certified stage should be reused")

    monkeypatch.setattr(campaign_service, "classify_tearing", _unexpected_call)
    resumed = run_additive_campaign(
        campaign,
        source=_synthetic_source(),
        mode="optimize",
        resume_result=first,
        resume_label="first_run",
    )
    assert resumed.stages[0].reused_from_run == "first_run"


def test_force_from_stage_invalidates_certified_cache() -> None:
    campaign = _synthetic_campaign()
    first = run_additive_campaign(
        campaign,
        source=_synthetic_source(),
        mode="optimize",
    )
    forced = run_additive_campaign(
        campaign,
        source=_synthetic_source(),
        mode="optimize",
        resume_result=first,
        resume_label="first_run",
        force_from_stage="all",
    )
    assert forced.stages[0].reused_from_run is None
    assert forced.stages[0].input_sha256 == first.stages[0].input_sha256


@dataclass(frozen=True)
class _RetryResult:
    statuses: dict[str, str]


def test_adaptive_retry_records_uncertified_attempt() -> None:
    calls = 0

    def runner(_config: TearingConfig) -> _RetryResult:
        nonlocal calls
        calls += 1
        status = "FEASIBLE" if calls == 1 else "OPTIMAL"
        return _RetryResult({"phase": status})

    outcome = run_with_adaptive_retry(
        operation="test",
        component_id="component_001",
        base_config=TearingConfig(),
        time_limits_s=(1.0, 2.0),
        runner=runner,
        status_getter=lambda result: result.statuses,
        certificate_getter=lambda result: (
            set(result.statuses.values()) == {"OPTIMAL"}
        ),
    )
    assert len(outcome.attempts) == 2
    assert outcome.attempts[0].terminal_status == "FEASIBLE"
    assert outcome.attempts[1].certified


def test_fingerprint_is_stable_for_mapping_order() -> None:
    assert canonical_sha256({"a": 1, "b": [2, 3]}) == canonical_sha256(
        {"b": [2, 3], "a": 1}
    )


def test_undeclared_same_incidence_is_not_removed() -> None:
    source = StructuralSystemData(
        profile="same_incidence",
        equations={
            "EqA": ["x", "y"],
            "EqB": ["y", "x"],
        },
        variables=("x", "y"),
        installed_sensors=frozenset(),
        known_constants=frozenset(),
        calculated_outputs=frozenset(),
        blocks={"all": ("EqA", "EqB")},
        allowed_outputs={},
        duplicate_equation_groups=(("EqA", "EqB"),),
        declared_duplicates=(),
    )
    normalized, removed = normalize_declared_duplicates(source)
    assert removed == ()
    assert set(normalized) == {"EqA", "EqB"}


def test_yaml_v10_equation_ranges_remain_valid(tmp_path: Path) -> None:
    path = tmp_path / "legacy.yaml"
    path.write_text(
        "\n".join(
            [
                'schema_version: "1.0"',
                "campaign:",
                "  id: legacy",
                '  name: "Legacy YAML"',
                "  source_profile: injection_system",
                "  stages:",
                "    - id: urs_balances",
                '      name: "URS mass balances"',
                "      equation_start: 73",
                "      equation_end: 92",
            ]
        )
        + "\n",
        encoding="ascii",
    )
    loaded = load_campaign(path)
    assert loaded.schema_version == "1.0"
    assert loaded.candidate_mode == "automatic"
    assert loaded.stages[0].equation_start == 73
    assert loaded.stages[0].block_id is None
    result = run_additive_campaign(loaded, mode="classify")
    assert result.stages[0].stage_id == "urs_balances"
    assert result.stages[0].global_certificate in {"certified", "partial"}


def test_reviewed_mode_keeps_whitelist() -> None:
    campaign = replace(
        _synthetic_campaign(),
        candidate_mode="reviewed",
        stages=(
            CampaignStage(
                stage_id="all",
                name="All",
                block_id="all",
                approved_candidates=("u",),
            ),
        ),
    )
    result = run_additive_campaign(
        campaign,
        source=_synthetic_source(),
        mode="optimize",
    )
    assert result.candidate_mode == "reviewed"
    assert result.stages[0].approved_candidates == ("u",)
    assert result.stages[0].global_certificate == "partial"
    assert result.stages[0].placement is None or (
        not result.stages[0].placement.target_covered
    )


def test_automatic_candidate_expansion_uses_later_tier() -> None:
    source = StructuralSystemData(
        profile="expansion",
        equations={
            "Eq1": ["kpi", "near", "bridge"],
            "Eq2": ["bridge", "sensor"],
        },
        variables=("bridge", "kpi", "near", "sensor"),
        installed_sensors=frozenset(),
        known_constants=frozenset(),
        calculated_outputs=frozenset({"bridge", "kpi"}),
        blocks={"all": ("Eq1", "Eq2")},
        allowed_outputs={
            "Eq1": frozenset({"kpi"}),
            "Eq2": frozenset({"bridge"}),
        },
        duplicate_equation_groups=(),
    )
    campaign = CampaignDefinition(
        schema_version="1.1",
        campaign_id="expansion",
        name="Expansion",
        source_profile="expansion",
        candidate_mode="automatic",
        default_target_profile="calculated_outputs",
        stages=(
            CampaignStage(
                stage_id="all",
                name="All",
                block_id="all",
                targets=("kpi",),
                target_mode="replace",
            ),
        ),
        sensor_costs={},
        solver=CampaignSolverConfig(
            time_limit_s=10.0,
            retry_time_limits_s=(10.0,),
            decompose_components=True,
        ),
        source_path="expansion.yaml",
    )
    result = run_additive_campaign(campaign, source=source, mode="optimize")
    assert result.stages[0].candidate_tier == 2
    assert result.stages[0].placement is not None
    assert result.stages[0].placement.target_covered
    assert set(result.stages[0].placement.selected_sensors) == {"near", "sensor"}


def test_nonsparable_max_tears_uses_monolithic_fallback() -> None:
    campaign = replace(
        _synthetic_campaign(),
        solver=CampaignSolverConfig(
            time_limit_s=10.0,
            retry_time_limits_s=(10.0,),
            decompose_components=True,
            max_tears=1,
        ),
    )
    result = run_additive_campaign(
        campaign,
        source=_synthetic_source(),
        mode="optimize",
    )
    assert result.stages[0].component_count == 1
    assert any(
        "max_tears" in warning
        for warning in result.stages[0].warnings
    )


def test_all_active_variables_closes_every_variable() -> None:
    source = StructuralSystemData(
        profile="full_observability",
        equations={
            "Eq1": ["kpi", "known"],
            "Eq2": ["side", "extra"],
        },
        variables=("extra", "known", "kpi", "side"),
        installed_sensors=frozenset(),
        known_constants=frozenset(),
        calculated_outputs=frozenset({"kpi"}),
        blocks={"all": ("Eq1", "Eq2")},
        allowed_outputs={"Eq1": frozenset({"kpi"})},
        duplicate_equation_groups=(),
    )
    campaign = replace(
        _synthetic_campaign(),
        campaign_id="full_observability",
        default_target_profile="all_active_variables",
        source_path="full.yaml",
    )
    result = run_additive_campaign(campaign, source=source, mode="optimize")
    stage = result.stages[0]
    assert set(stage.targets) == {"extra", "known", "kpi", "side"}
    assert stage.global_certificate == "certified"
    assert stage.placement is not None
    assert stage.validation is not None
    assert "kpi" not in set(stage.placement.selected_sensors)
    assert set(stage.validation.closed_coverage_variables) == set(source.variables)

    outputs_only = replace(
        campaign,
        default_target_profile="calculated_outputs",
    )
    output_result = run_additive_campaign(
        outputs_only,
        source=source,
        mode="optimize",
    )
    output_stage = output_result.stages[0]
    assert set(output_stage.targets) == {"kpi"}
    assert output_stage.validation is not None
    assert "side" not in output_stage.validation.closed_coverage_variables


def test_unknown_target_profile_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "bad_profile.yaml"
    path.write_text(
        "\n".join(
            [
                'schema_version: "1.1"',
                "campaign:",
                "  id: bad",
                '  name: "Bad profile"',
                "  source_profile: injection_system",
                "  default_target_profile: every_output",
                "  stages:",
                "    - id: urs_balances",
                '      name: "URS"',
                "      block_id: urs_balances",
            ]
        )
        + "\n",
        encoding="ascii",
    )
    try:
        load_campaign(path)
    except ValueError as error:
        assert "all_active_variables" in str(error)
    else:
        raise AssertionError("Unknown target profile was accepted")


def test_partial_certificate_when_targets_stay_open() -> None:
    campaign = replace(
        _synthetic_campaign(),
        candidate_mode="reviewed",
        stages=(
            CampaignStage(
                stage_id="all",
                name="All",
                block_id="all",
            ),
        ),
    )
    result = run_additive_campaign(
        campaign,
        source=_synthetic_source(),
        mode="optimize",
    )
    assert result.stages[0].global_certificate == "partial"


def test_urs_stage_kpis_decomposed_matches_monolithic() -> None:
    source = load_injection_system()
    normalized, _removed = normalize_declared_duplicates(source)
    names = list(source.blocks["urs_balances"]) + list(source.blocks["stage_kpis"])
    equations = {
        name: list(normalized[name])
        for name in names
        if name in normalized
    }
    active = {variable for values in equations.values() for variable in values}
    measured = set(source.installed_sensors) & active
    constants = set(source.known_constants) & active
    targets = set(source.calculated_outputs) & active
    allowed = {
        name: set(source.allowed_outputs[name])
        for name in equations
        if name in source.allowed_outputs
    }
    candidates = {
        "PT_1P_A",
        "PT_1P_B",
        "PT_1P_C",
        "PT_1P_D",
        "PT_1P_E",
        "PT_P_A",
        "PT_P_B",
        "PT_P_C",
        "PT_P_D",
        "PT_P_E",
    } & active
    config = TearingConfig(time_limit_s=30.0, require_optimal=True)
    monolithic = solve_integrated_sensor_placement(
        equations,
        measured,
        candidates,
        targets,
        known_constants=constants,
        allowed_outputs=allowed,
        config=config,
    )
    parts = []
    for component in partition_incidence_components(equations):
        component_targets = targets & set(component.variables)
        if not component_targets:
            continue
        parts.append(
            solve_integrated_sensor_placement(
                component.equations,
                measured & set(component.variables),
                candidates & set(component.variables),
                component_targets,
                known_constants=constants & set(component.variables),
                allowed_outputs={
                    name: set(allowed[name])
                    for name in component.equations
                    if name in allowed
                } or None,
                config=config,
            )
        )
    merged = merge_placement_results("urs_stage", parts)
    assert monolithic.minimum_certified
    assert merged.minimum_certified
    assert merged.selected_cost == monolithic.selected_cost
    assert set(merged.selected_sensors) == set(monolithic.selected_sensors)


def test_report_roundtrip_and_signature_invalidation(tmp_path: Path) -> None:
    campaign = _synthetic_campaign()
    first = run_additive_campaign(
        campaign,
        source=_synthetic_source(),
        mode="optimize",
    )
    campaign_path = tmp_path / "campaign.yaml"
    campaign_path.write_text("schema_version: \"1.1\"\n", encoding="ascii")
    written = write_campaign_artifacts(
        first,
        tmp_path / "run",
        campaign_yaml_path=campaign_path,
    )
    loaded = load_campaign_report(written["json"])
    assert loaded.stages[0].input_sha256 == first.stages[0].input_sha256
    assert loaded.stages[0].placement == first.stages[0].placement

    changed = replace(campaign, sensor_costs={"u": 2})
    rerun = run_additive_campaign(
        changed,
        source=_synthetic_source(),
        mode="optimize",
        resume_result=loaded,
        resume_label="first",
    )
    assert rerun.stages[0].reused_from_run is None
    assert rerun.stages[0].input_sha256 != first.stages[0].input_sha256
