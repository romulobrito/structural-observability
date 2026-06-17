#!/usr/bin/env python3
"""Tests for UI presenters (no Streamlit required)."""

from __future__ import annotations

from pathlib import Path

from structural_obs import PROJECT_ROOT
from structural_obs.app.presenters import present_classification, present_repair
from structural_obs.app.ui_labels import SOLVER_CONFIRMED
from structural_obs.toolkit.schemas.loaders import load_case
from structural_obs.toolkit.services.classify_service import run_case

CASES_DIR = PROJECT_ROOT / "cases"


def test_classification_headline_real() -> None:
    case = load_case(CASES_DIR / "urs_pdf_real.yaml")
    run = run_case(case)
    view = present_classification(run)
    assert "22 medidas" in view.headline
    assert "34 de 43" in view.headline
    assert view.calculable == 34
    assert not view.computes_all


def test_classification_headline_ideal() -> None:
    case = load_case(CASES_DIR / "urs_pdf_ideal.yaml")
    run = run_case(case)
    view = present_classification(run)
    assert "todas as 43" in view.headline
    assert view.computes_all


def test_repair_headline_and_options() -> None:
    case = load_case(CASES_DIR / "urs_pdf_repair.yaml")
    run = run_case(case)
    view = present_repair(run)
    assert view.minimum_additions == 2
    assert len(view.options) == 3
    assert view.solver_label == SOLVER_CONFIRMED
    for opt in view.options:
        assert opt.computes_all
        assert len(opt.sensors_to_add) == 2


def test_tags_only_no_descriptions() -> None:
    case = load_case(CASES_DIR / "urs_pdf_real.yaml")
    run = run_case(case)
    view = present_classification(run)
    assert "Ra_C" in view.not_calculable_tags or "Ra_C" in view.open_balance_tags
