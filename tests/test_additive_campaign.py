#!/usr/bin/env python3
"""Tests for additive campaign input and artifact export."""

from __future__ import annotations

from pathlib import Path

import openpyxl

from structural_obs.tearing.cases.injection_system import (
    load_injection_system,
    load_injection_system_no_ob_dr,
)
from structural_obs.tearing.cases.system_model import (
    StructuralSystemData,
    load_source,
    normalize_declared_duplicates,
)
from structural_obs.toolkit.schemas.campaign_schema import (
    CampaignDefinition,
    CampaignSolverConfig,
    CampaignStage,
    load_campaign,
)
from structural_obs.toolkit.services.additive_campaign import run_additive_campaign
from structural_obs.toolkit.services import additive_campaign as campaign_service
from structural_obs.toolkit.services.campaign_xlsx import write_campaign_artifacts


def _assert_lowest_number_is_kept(source: StructuralSystemData) -> None:
    """The kept equation is the lowest number in each identical group."""

    for canonical, duplicates in source.declared_duplicates:
        numbers = [int(canonical[2:])] + [int(name[2:]) for name in duplicates]
        assert min(numbers) == int(canonical[2:])
        canonical_variables = tuple(sorted(source.equations[canonical]))
        for name in duplicates:
            assert tuple(sorted(source.equations[name])) == canonical_variables


def test_complete_injection_source_and_yaml_are_valid() -> None:
    project_root = Path(__file__).resolve().parents[1]
    source = load_injection_system()
    campaign = load_campaign(project_root / "cases" / "injection_system_additive.yaml")
    assert len(source.equations) == 207
    assert len(source.variables) == 500
    assert len(source.duplicate_equation_groups) == 5
    assert len(campaign.stages) == 20
    assert campaign.default_target_profile == "calculated_outputs"
    full = load_campaign(
        project_root / "cases" / "injection_system_full_observability.yaml"
    )
    assert full.default_target_profile == "all_active_variables"
    assert len(full.stages) == 20
    assert full.campaign_id == "injection_system_full_observability"
    assert full.source_profile == "injection_system"
    assert source.profile == "injection_system"
    assert source.blocks["urs_balances"][0] == "Eq73"
    assert source.blocks["urs_balances"][-1] == "Eq92"
    assert source.declared_duplicates == (
        ("Eq118", ("Eq163",)),
        ("Eq119", ("Eq164",)),
        ("Eq120", ("Eq165",)),
        ("Eq121", ("Eq166",)),
        ("Eq122", ("Eq167",)),
    )
    _assert_lowest_number_is_kept(source)


def test_reduced_injection_profile_partitions_every_equation() -> None:
    project_root = Path(__file__).resolve().parents[1]
    source = load_injection_system_no_ob_dr()
    registered = load_source("injection_system_no_ob_dr")
    assert registered.profile == source.profile
    assert len(source.equations) == 203
    assert len(source.variables) == 408
    covered = [name for block in source.blocks.values() for name in block]
    ordered = sorted(covered, key=lambda name: int(name[2:]))
    assert ordered == [f"Eq{number}" for number in range(1, 204)]
    assert len(covered) == len(set(covered))
    assert source.declared_duplicates == (
        ("Eq114", ("Eq159",)),
        ("Eq115", ("Eq160",)),
        ("Eq116", ("Eq161",)),
        ("Eq117", ("Eq162",)),
        ("Eq118", ("Eq163",)),
    )
    _assert_lowest_number_is_kept(source)
    normalized, removed = normalize_declared_duplicates(source)
    assert removed == ("Eq159", "Eq160", "Eq161", "Eq162", "Eq163")
    assert len(normalized) == 198
    for name, outputs in source.allowed_outputs.items():
        assert outputs == frozenset({source.equations[name][0]})
    assert "F_7_out_SR_DR" in source.variables
    assert "F_8_out_SK_FF_OB" in source.variables
    campaign = load_campaign(
        project_root / "cases" / "injection_system_no_ob_dr_full.yaml"
    )
    assert campaign.source_profile == "injection_system_no_ob_dr"
    assert campaign.campaign_id == "injection_system_no_ob_dr_full"
    assert campaign.default_target_profile == "all_active_variables"
    assert [stage.block_id for stage in campaign.stages] == [
        "urs_balances",
        "stage_kpis",
        "bank_kpis",
        "booster",
        "fine_filters",
        "coarse_filters",
        "biocide",
        "antiscalant",
        "bisulfite",
        "cleaning",
        "deaeration",
        "water_distribution",
        "distribution_filters",
        "heat_exchangers",
        "cooling_water_ac",
        "cooling_water_anc",
        "injection_pumping",
        "hypochlorite_injection",
        "electrochlorination",
        "hypochlorite_tank",
    ]
    approved = {
        name
        for stage in campaign.stages
        for name in stage.approved_candidates
    }
    assert approved <= set(source.variables)


def test_classification_campaign_exports_expected_workbook(tmp_path: Path) -> None:
    project_root = Path(__file__).resolve().parents[1]
    campaign_path = project_root / "cases" / "injection_system_additive.yaml"
    base = load_campaign(campaign_path)
    one_stage = CampaignDefinition(
        schema_version=base.schema_version,
        campaign_id="test_campaign",
        name="Test campaign",
        source_profile=base.source_profile,
        candidate_mode="reviewed",
        default_target_profile=base.default_target_profile,
        stages=(
            CampaignStage(
                stage_id="urs_balances",
                name="URS balances",
                equation_start=73,
                equation_end=92,
            ),
        ),
        sensor_costs={},
        solver=CampaignSolverConfig(time_limit_s=30.0),
        source_path=str(campaign_path),
    )
    result = run_additive_campaign(one_stage, mode="classify")
    written = write_campaign_artifacts(
        result,
        tmp_path,
        campaign_yaml_path=campaign_path,
    )
    workbook = openpyxl.load_workbook(written["xlsx"], read_only=True)
    expected = {
        "resumo_etapas",
        "cobertura_alvos",
        "variaveis",
        "equacoes",
        "fases_solver",
        "candidatos_sugeridos",
        "candidatos_usados",
        "instrumentacao_minima",
        "validacao",
        "componentes_scc_ciclicos",
        "componentes_incidencia",
        "tentativas_solver",
        "retomada",
        "erros_avisos",
    }
    assert expected <= set(workbook.sheetnames)


def test_campaign_records_classifier_timeout(
    monkeypatch,
) -> None:
    project_root = Path(__file__).resolve().parents[1]
    campaign_path = project_root / "cases" / "injection_system_additive.yaml"
    base = load_campaign(campaign_path)
    one_stage = CampaignDefinition(
        schema_version=base.schema_version,
        campaign_id="test_failure",
        name="Test failure",
        source_profile=base.source_profile,
        candidate_mode="reviewed",
        default_target_profile=base.default_target_profile,
        stages=(base.stages[0],),
        sensor_costs={},
        solver=CampaignSolverConfig(time_limit_s=1.0),
        source_path=str(campaign_path),
    )

    def _raise_timeout(*_args: object, **_kwargs: object) -> None:
        raise RuntimeError("phase returned UNKNOWN")

    monkeypatch.setattr(campaign_service, "classify_tearing", _raise_timeout)
    result = run_additive_campaign(one_stage, mode="classify")
    assert result.stages == ()
    assert result.errors
    assert "UNKNOWN" in result.errors[0]
