#!/usr/bin/env python3
"""Orchestrate additive classification and minimum instrumentation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Mapping, Optional, Set

from structural_obs.tearing.cases.injection_system import (
    InjectionSystemData,
    default_allowed_outputs,
    equations_for_range,
)
from structural_obs.tearing.cases.system_model import (
    StructuralSystemData,
    load_source,
    normalize_declared_duplicates,
    select_block_equations,
)
from structural_obs.tearing.core import TearingConfig, TearingResult, classify_tearing
from structural_obs.toolkit.schemas.campaign_schema import (
    CampaignDefinition,
    CampaignStage,
)
from structural_obs.toolkit.services.candidate_generation import (
    CandidateSuggestion,
    automatic_candidate_tiers,
    generate_sensor_candidates,
)
from structural_obs.toolkit.services.campaign_checkpoint import canonical_sha256
from structural_obs.toolkit.services.incidence_components import (
    IncidenceComponent,
    merge_placement_results,
    merge_tearing_results,
    partition_incidence_components,
    project_allowed_outputs,
)
from structural_obs.toolkit.services.integrated_sensor_placement import (
    IntegratedPlacementResult,
    solve_integrated_sensor_placement,
)
from structural_obs.toolkit.services.solver_retry import (
    SolverAttemptRecord,
    run_with_adaptive_retry,
)

Equations = Dict[str, List[str]]


@dataclass(frozen=True)
class ComponentCertificate:
    """Auditable certificate for one incidence component."""

    component_id: str
    equations: tuple[str, ...]
    variables: tuple[str, ...]
    targets: tuple[str, ...]
    selected_sensors: tuple[str, ...]
    selected_cost: int
    classification_certified: bool
    placement_certified: bool
    validation_ok: bool
    status: str


@dataclass(frozen=True)
class CampaignStageResult:
    """Complete result for one cumulative campaign stage."""

    stage_id: str
    stage_name: str
    stage_index: int
    added_equations: tuple[str, ...]
    cumulative_equations: tuple[str, ...]
    targets: tuple[str, ...]
    base_measured: tuple[str, ...]
    known_constants: tuple[str, ...]
    classification: TearingResult
    candidate_suggestions: tuple[CandidateSuggestion, ...]
    approved_candidates: tuple[str, ...]
    placement: Optional[IntegratedPlacementResult]
    validation: Optional[TearingResult]
    warnings: tuple[str, ...]
    component_count: int
    component_certificates: tuple[ComponentCertificate, ...] = ()
    solver_attempts: tuple[SolverAttemptRecord, ...] = ()
    input_sha256: str = ""
    reused_from_run: Optional[str] = None
    global_certificate: str = "not_applicable"
    candidate_tier: int = 0
    normalized_removed_equations: tuple[str, ...] = ()


@dataclass(frozen=True)
class AdditiveCampaignResult:
    """All cumulative stages from one campaign run."""

    campaign_id: str
    campaign_name: str
    source_path: str
    stages: tuple[CampaignStageResult, ...]
    duplicate_equation_groups: tuple[tuple[str, ...], ...]
    errors: tuple[str, ...]
    semantics_version: str = "additive_campaign_v2"
    candidate_mode: str = "automatic"


def _active_variables(equations: Mapping[str, List[str]]) -> Set[str]:
    return {variable for values in equations.values() for variable in values}


def _variable_component_count(equations: Mapping[str, List[str]]) -> int:
    adjacency: Dict[str, Set[str]] = {}
    for values in equations.values():
        unique = set(values)
        for variable in unique:
            adjacency.setdefault(variable, set()).update(unique - {variable})
    unseen = set(adjacency)
    count = 0
    while unseen:
        count += 1
        stack = [unseen.pop()]
        while stack:
            current = stack.pop()
            neighbors = adjacency.get(current, set()) & unseen
            unseen -= neighbors
            stack.extend(neighbors)
    return count


def _default_targets(
    profile: str,
    calculated_outputs: Set[str],
    active_variables: Set[str],
) -> Set[str]:
    """Return the stage targets implied by the campaign profile.

    ``calculated_outputs`` keeps utilities and KPIs.
    ``all_active_variables`` requires every variable in the accumulated system.
    """

    if profile == "calculated_outputs":
        return set(calculated_outputs) & active_variables
    if profile == "all_active_variables":
        return set(active_variables)
    raise ValueError(f"Unsupported target profile: {profile}")


def _resolve_targets(
    stage: CampaignStage,
    default_targets: Set[str],
) -> Set[str]:
    explicit = set(stage.targets)
    if stage.target_mode == "replace":
        return explicit
    if stage.target_mode == "extend":
        return default_targets | explicit
    return default_targets


def _stage_duplicate_warnings(
    active_equations: Set[str],
    duplicate_groups: tuple[tuple[str, ...], ...],
) -> List[str]:
    warnings = []
    for group in duplicate_groups:
        active = sorted(set(group) & active_equations)
        if len(active) > 1:
            warnings.append(
                f"Duplicate incidence equations active: {', '.join(active)}"
            )
    return warnings


def _all_phases_optimal(result: TearingResult) -> bool:
    return bool(result.status_by_phase) and set(
        result.status_by_phase.values()
    ) == {"OPTIMAL"}


def _select_stage_equations(
    source: StructuralSystemData,
    stage: CampaignStage,
    equations: Equations,
    skipped_equations: Set[str] | None = None,
) -> Equations:
    if stage.block_id is not None:
        return select_block_equations(source, stage.block_id, equations)
    if stage.equation_start is None or stage.equation_end is None:
        raise ValueError(f"Stage has no equation selector: {stage.stage_id}")
    skip = set(skipped_equations or set())
    selected: Equations = {}
    for number in range(stage.equation_start, stage.equation_end + 1):
        name = f"Eq{number}"
        if name in equations:
            selected[name] = list(equations[name])
            continue
        if name in skip:
            continue
        return equations_for_range(
            equations,
            stage.equation_start,
            stage.equation_end,
        )
    return selected


def _stage_fingerprint(
    campaign: CampaignDefinition,
    stage: CampaignStage,
    equations: Equations,
    measured: Set[str],
    constants: Set[str],
    targets: Set[str],
    approved_candidates: Set[str],
    prohibited_candidates: Set[str],
    allowed_outputs: Mapping[str, Set[str]],
    mode: str,
) -> str:
    return canonical_sha256(
        {
            "semantics": "additive_campaign_v2",
            "campaign_id": campaign.campaign_id,
            "stage_id": stage.stage_id,
            "mode": mode,
            "source_profile": campaign.source_profile,
            "equations": {
                name: list(values)
                for name, values in sorted(equations.items())
            },
            "measured": sorted(measured),
            "constants": sorted(constants),
            "targets": sorted(targets),
            "approved_candidates": sorted(approved_candidates),
            "prohibited_candidates": sorted(prohibited_candidates),
            "sensor_costs": {
                variable: cost
                for variable, cost in sorted(campaign.sensor_costs.items())
            },
            "allowed_outputs": {
                name: sorted(values)
                for name, values in sorted(allowed_outputs.items())
            },
            "candidate_mode": campaign.candidate_mode,
            "solver": {
                "random_seed": campaign.solver.random_seed,
                "preprocessing": campaign.solver.use_structural_preprocessing,
                "retry_limits": list(campaign.solver.retry_time_limits_s),
                "decompose": campaign.solver.decompose_components,
                "max_tears": campaign.solver.max_tears,
            },
        }
    )


def _classify_components(
    *,
    campaign: CampaignDefinition,
    stage: CampaignStage,
    components: tuple[IncidenceComponent, ...],
    measured: Set[str],
    constants: Set[str],
    allowed: Mapping[str, Set[str]],
    case_suffix: str,
    extra_measured: Set[str] | None = None,
) -> tuple[
    TearingResult,
    tuple[TearingResult, ...],
    tuple[SolverAttemptRecord, ...],
]:
    base_config = TearingConfig(
        time_limit_s=campaign.solver.time_limit_s,
        random_seed=campaign.solver.random_seed,
        require_optimal=False,
        use_structural_preprocessing=campaign.solver.use_structural_preprocessing,
        max_tears=campaign.solver.max_tears,
        num_search_workers=campaign.solver.num_search_workers,
    )
    results: list[TearingResult] = []
    attempts: list[SolverAttemptRecord] = []
    measured_values = measured | set(extra_measured or set())
    for component in components:
        component_measured = measured_values & set(component.variables)
        component_constants = constants & set(component.variables)
        component_allowed = project_allowed_outputs(allowed, component)
        outcome = run_with_adaptive_retry(
            operation=case_suffix,
            component_id=component.component_id,
            base_config=base_config,
            time_limits_s=campaign.solver.retry_time_limits_s,
            runner=lambda config, current=component: classify_tearing(
                current.equations,
                component_measured,
                known_constants=component_constants,
                allowed_outputs=component_allowed,
                case_name=(
                    f"{campaign.campaign_id}_{stage.stage_id}_"
                    f"{case_suffix}_{current.component_id}"
                ),
                config=config,
            ),
            status_getter=lambda result: result.status_by_phase,
            certificate_getter=_all_phases_optimal,
        )
        results.append(outcome.result)
        attempts.extend(outcome.attempts)
    merged = merge_tearing_results(
        f"{campaign.campaign_id}_{stage.stage_id}_{case_suffix}",
        results,
    )
    return merged, tuple(results), tuple(attempts)


def run_additive_campaign(
    campaign: CampaignDefinition,
    *,
    source: Optional[InjectionSystemData] = None,
    mode: str = "optimize",
    resume_result: Optional[AdditiveCampaignResult] = None,
    resume_label: Optional[str] = None,
    force_from_stage: Optional[str] = None,
    progress_callback: Optional[
        Callable[[AdditiveCampaignResult], None]
    ] = None,
) -> AdditiveCampaignResult:
    """Run all cumulative stages defined by the campaign."""

    if mode not in {"classify", "generate-candidates", "optimize"}:
        raise ValueError(f"Unsupported campaign mode: {mode}")
    source_data: StructuralSystemData = source or load_source(
        campaign.source_profile
    )
    if campaign.normalize_declared_duplicates:
        normalized_equations, normalized_removed = normalize_declared_duplicates(
            source_data
        )
    else:
        normalized_equations = {
            name: list(values)
            for name, values in source_data.equations.items()
        }
        normalized_removed = ()
    cumulative_equations: Equations = {}
    cumulative_approved: Set[str] = set()
    cumulative_prohibited: Set[str] = set()
    stage_results: list[CampaignStageResult] = []
    campaign_errors: List[str] = []
    cached_by_id = {
        stage.stage_id: stage
        for stage in (resume_result.stages if resume_result else ())
    }
    reuse_enabled = resume_result is not None

    def current_result() -> AdditiveCampaignResult:
        return AdditiveCampaignResult(
            campaign_id=campaign.campaign_id,
            campaign_name=campaign.name,
            source_path=campaign.source_path,
            stages=tuple(stage_results),
            duplicate_equation_groups=source_data.duplicate_equation_groups,
            errors=tuple(campaign_errors),
            candidate_mode=campaign.candidate_mode,
        )

    for stage_index, stage in enumerate(campaign.stages, start=1):
        if stage.stage_id == force_from_stage:
            reuse_enabled = False
        added = _select_stage_equations(
            source_data,
            stage,
            normalized_equations,
            skipped_equations=set(normalized_removed),
        )
        overlap = set(cumulative_equations) & set(added)
        if overlap:
            raise ValueError(
                f"Stage {stage.stage_id} repeats equations: {sorted(overlap)}"
            )
        cumulative_equations.update(added)
        active_variables = _active_variables(cumulative_equations)
        measured = set(source_data.installed_sensors) & active_variables
        constants = set(source_data.known_constants) & active_variables
        default_targets = _default_targets(
            campaign.default_target_profile,
            set(source_data.calculated_outputs),
            active_variables,
        )
        targets = _resolve_targets(stage, default_targets)
        unknown_targets = targets - active_variables
        if unknown_targets:
            raise ValueError(
                f"Stage {stage.stage_id} has inactive targets: {sorted(unknown_targets)}"
            )
        allowed = default_allowed_outputs(
            cumulative_equations,
            source_data.allowed_outputs,
        )
        cumulative_approved.update(stage.approved_candidates)
        cumulative_prohibited.update(stage.prohibited_candidates)
        fingerprint = _stage_fingerprint(
            campaign,
            stage,
            cumulative_equations,
            measured,
            constants,
            targets,
            set(cumulative_approved),
            set(cumulative_prohibited),
            allowed,
            mode,
        )
        cached = cached_by_id.get(stage.stage_id)
        if (
            reuse_enabled
            and cached is not None
            and cached.input_sha256 == fingerprint
            and cached.global_certificate == "certified"
        ):
            stage_results.append(
                CampaignStageResult(
                    **{
                        **cached.__dict__,
                        "reused_from_run": resume_label or "resume",
                    }
                )
            )
            if progress_callback is not None:
                progress_callback(current_result())
            continue
        if cached is None or cached.input_sha256 != fingerprint:
            reuse_enabled = False
        use_monolithic = (
            not campaign.solver.decompose_components
            or campaign.solver.max_tears is not None
        )
        if use_monolithic:
            components = (
                IncidenceComponent(
                    component_id="component_001",
                    equations=dict(cumulative_equations),
                    variables=frozenset(active_variables),
                ),
            )
        else:
            components = partition_incidence_components(cumulative_equations)
        try:
            classification, classification_parts, classification_attempts = (
                _classify_components(
                    campaign=campaign,
                    stage=stage,
                    components=components,
                    measured=measured,
                    constants=constants,
                    allowed=allowed,
                    case_suffix="baseline",
                )
            )
        except RuntimeError as error:
            campaign_errors.append(
                f"Stage {stage.stage_id} classification failed: {error}"
            )
            if progress_callback is not None:
                progress_callback(current_result())
            break

        suggestions = (
            generate_sensor_candidates(
                cumulative_equations,
                classification,
                targets,
                calculated_outputs=source_data.calculated_outputs,
                prohibited=cumulative_prohibited,
            )
            if mode != "classify"
            else ()
        )
        if campaign.candidate_mode == "automatic" and suggestions:
            candidate_tiers = [
                set(tier) | set(cumulative_approved)
                for tier in automatic_candidate_tiers(suggestions)
            ]
        elif campaign.candidate_mode == "automatic":
            candidate_tiers = [set(cumulative_approved)]
        else:
            candidate_tiers = [set(cumulative_approved)]
        for candidate_tier in candidate_tiers:
            candidate_tier.intersection_update(active_variables)
            candidate_tier.difference_update(
                measured | constants | cumulative_prohibited
            )
        maximum_candidates = set().union(*candidate_tiers)

        warnings = _stage_duplicate_warnings(
            set(cumulative_equations),
            source_data.duplicate_equation_groups,
        )
        if normalized_removed:
            warnings.append(
                "Declared duplicate equations removed: "
                + ", ".join(normalized_removed)
            )
        if (
            campaign.solver.max_tears is not None
            and campaign.solver.decompose_components
        ):
            warnings.append(
                "Non-separable constraint max_tears: using monolithic fallback"
            )
        component_count = len(components)
        if component_count > 1:
            warnings.append(
                f"Cumulative variable graph has {component_count} components"
            )

        placement: Optional[IntegratedPlacementResult] = None
        validation: Optional[TearingResult] = None
        attempts = list(classification_attempts)
        used_candidates: Set[str] = set()
        used_tier = 0
        component_certificates: list[ComponentCertificate] = []
        if mode == "optimize" and targets:
            for tier_index, candidate_set in enumerate(candidate_tiers, start=1):
                placement_parts: list[IntegratedPlacementResult] = []
                no_target_parts: list[TearingResult] = []
                component_certificates = []
                tier_failed = False
                base_config = TearingConfig(
                    time_limit_s=campaign.solver.time_limit_s,
                    random_seed=campaign.solver.random_seed,
                    require_optimal=False,
                    use_structural_preprocessing=(
                        campaign.solver.use_structural_preprocessing
                    ),
                    max_tears=campaign.solver.max_tears,
                    num_search_workers=campaign.solver.num_search_workers,
                )
                for component, baseline_part in zip(
                    components,
                    classification_parts,
                ):
                    component_targets = targets & set(component.variables)
                    if not component_targets:
                        no_target_parts.append(baseline_part)
                        component_certificates.append(
                            ComponentCertificate(
                                component_id=component.component_id,
                                equations=tuple(component.equations),
                                variables=tuple(sorted(component.variables)),
                                targets=(),
                                selected_sensors=(),
                                selected_cost=0,
                                classification_certified=_all_phases_optimal(
                                    baseline_part
                                ),
                                placement_certified=True,
                                validation_ok=True,
                                status="no_targets",
                            )
                        )
                        continue
                    component_candidates = candidate_set & set(
                        component.variables
                    )
                    component_allowed = project_allowed_outputs(
                        allowed,
                        component,
                    )
                    outcome = run_with_adaptive_retry(
                        operation="placement",
                        component_id=component.component_id,
                        base_config=base_config,
                        time_limits_s=campaign.solver.retry_time_limits_s,
                        runner=lambda config, current=component: (
                            solve_integrated_sensor_placement(
                                current.equations,
                                measured & set(current.variables),
                                component_candidates,
                                component_targets,
                                known_constants=(
                                    constants & set(current.variables)
                                ),
                                allowed_outputs=component_allowed,
                                sensor_costs={
                                    variable: campaign.sensor_costs.get(
                                        variable,
                                        1,
                                    )
                                    for variable in component_candidates
                                },
                                case_name=(
                                    f"{campaign.campaign_id}_{stage.stage_id}_"
                                    f"placement_{current.component_id}"
                                ),
                                config=config,
                            )
                        ),
                        status_getter=lambda result: result.status_by_phase,
                        certificate_getter=lambda result: (
                            result.minimum_certified
                            and result.target_covered
                        ),
                    )
                    attempts.extend(outcome.attempts)
                    placement_parts.append(outcome.result)
                    primary_status = outcome.result.status_by_phase.get(
                        "phase_1_min_sensor_cost",
                        "UNKNOWN",
                    )
                    if not outcome.result.target_covered:
                        tier_failed = True
                    component_certificates.append(
                        ComponentCertificate(
                            component_id=component.component_id,
                            equations=tuple(component.equations),
                            variables=tuple(sorted(component.variables)),
                            targets=tuple(sorted(component_targets)),
                            selected_sensors=outcome.result.selected_sensors,
                            selected_cost=outcome.result.selected_cost,
                            classification_certified=_all_phases_optimal(
                                baseline_part
                            ),
                            placement_certified=(
                                outcome.result.minimum_certified
                            ),
                            validation_ok=False,
                            status=primary_status,
                        )
                    )
                if placement_parts:
                    placement = merge_placement_results(
                        f"{campaign.campaign_id}_{stage.stage_id}_placement",
                        placement_parts,
                        baseline_parts_without_targets=no_target_parts,
                    )
                if not tier_failed and placement is not None:
                    used_candidates = set(candidate_set)
                    used_tier = tier_index
                    break
            if not used_candidates and candidate_tiers:
                used_candidates = set(candidate_tiers[-1])
                used_tier = len(candidate_tiers)
            if placement is not None and placement.target_covered:
                try:
                    validation, validation_parts, validation_attempts = (
                        _classify_components(
                            campaign=campaign,
                            stage=stage,
                            components=components,
                            measured=measured,
                            constants=constants,
                            allowed=allowed,
                            case_suffix="validation",
                            extra_measured=set(placement.selected_sensors),
                        )
                    )
                    attempts.extend(validation_attempts)
                    validation_by_variables = {
                        frozenset(component.variables): result
                        for component, result in zip(
                            components,
                            validation_parts,
                        )
                    }
                    component_certificates = [
                        ComponentCertificate(
                            component_id=certificate.component_id,
                            equations=certificate.equations,
                            variables=certificate.variables,
                            targets=certificate.targets,
                            selected_sensors=certificate.selected_sensors,
                            selected_cost=certificate.selected_cost,
                            classification_certified=(
                                certificate.classification_certified
                            ),
                            placement_certified=(
                                certificate.placement_certified
                            ),
                            validation_ok=(
                                set(certificate.targets)
                                <= validation_by_variables[
                                    frozenset(certificate.variables)
                                ].closed_coverage_variables
                            ),
                            status=certificate.status,
                        )
                        for certificate in component_certificates
                    ]
                except RuntimeError as error:
                    warnings.append(f"Frozen-core validation failed: {error}")
                    validation = None
            elif not maximum_candidates:
                warnings.append(
                    "No automatic candidates available for uncovered targets"
                )

        classification_certified = _all_phases_optimal(classification)
        if mode != "optimize" or not targets:
            global_certificate = (
                "certified" if classification_certified else "partial"
            )
        elif (
            placement is not None
            and placement.minimum_certified
            and placement.target_covered
            and validation is not None
            and targets <= validation.closed_coverage_variables
            and all(
                item.validation_ok
                and item.placement_certified
                for item in component_certificates
                if item.targets
            )
        ):
            global_certificate = "certified"
        else:
            global_certificate = "partial"

        stage_result = CampaignStageResult(
            stage_id=stage.stage_id,
            stage_name=stage.name,
            stage_index=stage_index,
            added_equations=tuple(added),
            cumulative_equations=tuple(cumulative_equations),
            targets=tuple(sorted(targets)),
            base_measured=tuple(sorted(measured)),
            known_constants=tuple(sorted(constants)),
            classification=classification,
            candidate_suggestions=suggestions,
            approved_candidates=tuple(sorted(used_candidates)),
            placement=placement,
            validation=validation,
            warnings=tuple(warnings),
            component_count=component_count,
            component_certificates=tuple(component_certificates),
            solver_attempts=tuple(attempts),
            input_sha256=fingerprint,
            global_certificate=global_certificate,
            candidate_tier=used_tier,
            normalized_removed_equations=normalized_removed,
        )
        stage_results.append(stage_result)
        if progress_callback is not None:
            progress_callback(current_result())

    return current_result()
