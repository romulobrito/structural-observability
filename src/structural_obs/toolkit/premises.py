#!/usr/bin/env python3
"""PDF-aligned measurement bases and candidate pools for URS document cases.

Reference: Instrumentacao Minima da URS (Marilia Caroline C. de Sa, 2024).
Sec. 4.1 ideal (26 measures), Sec. 4.2 real (22 measures), Sec. 4.2.3 repair.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import FrozenSet, List, Set, Tuple

# Sec. 4.1 -- ideal reconciliation set (26 measured variables).
IDEAL_MEASURED_PDF: FrozenSet[str] = frozenset({
    "Pa_A", "Pa_B", "Pa_C", "Pa_D", "Pa_E",
    "Pb_A", "Pb_B", "Pb_C", "Pb_D", "Pb_E",
    "Pc_A", "Pc_B", "Pc_C", "Pc_D", "Pc_E",
    "Rc_A", "Rc_B", "Rc_C", "Rc_D", "Rc_E",
    "Ra_A", "Ra_B", "Ra_C", "Ra_D", "Ra_E",
    "R",
})

# Sec. 4.2 / Table 1 -- failed flow meters removed from ideal.
FAILED_METERS_PDF: FrozenSet[str] = frozenset({"R", "Ra_C", "Ra_D", "Ra_E"})

# Sec. 4.2 -- real operational set (22 measures).
REAL_MEASURED_PDF: FrozenSet[str] = IDEAL_MEASURED_PDF - FAILED_METERS_PDF

# Sec. 4.2.3 -- primary repair candidates (failed meters).
CANDIDATES_FAILED_PDF: Tuple[str, ...] = ("R", "Ra_C", "Ra_D", "Ra_E")

# Extended pool for single-sensor repair sensitivity (optional analysis).
CANDIDATES_EXTENDED_PDF: Tuple[str, ...] = CANDIDATES_FAILED_PDF + (
    "FA", "FB", "FC", "FD", "FE",
    "P", "PA", "PB", "PC", "PD", "PE", "F",
)


@dataclass(frozen=True)
class PdfScenario:
    """Named PDF scenario with fixed base measurements."""

    key: str
    title: str
    base_measured: FrozenSet[str]
    section: str


PDF_SCENARIOS: Tuple[PdfScenario, ...] = (
    PdfScenario(
        key="ideal",
        title="URS ideal (PDF Sec. 4.1)",
        base_measured=IDEAL_MEASURED_PDF,
        section="4.1",
    ),
    PdfScenario(
        key="real",
        title="URS real (PDF Sec. 4.2)",
        base_measured=REAL_MEASURED_PDF,
        section="4.2",
    ),
)


def scenario_by_key(key: str) -> PdfScenario:
    """Return a PDF scenario by key."""
    for scenario in PDF_SCENARIOS:
        if scenario.key == key:
            return scenario
    known = ", ".join(s.key for s in PDF_SCENARIOS)
    raise ValueError(f"Unknown scenario '{key}'. Known: {known}")


def repair_candidates(pool: str) -> List[str]:
    """Return ordered candidate list for repair search."""
    if pool == "failed":
        return list(CANDIDATES_FAILED_PDF)
    if pool == "extended":
        return list(CANDIDATES_EXTENDED_PDF)
    raise ValueError(f"Unknown candidate pool '{pool}'. Use 'failed' or 'extended'.")


def pairs_tested_in_pdf() -> List[Tuple[str, str]]:
    """Return the three pairs explicitly tested in PDF Sec. 4.2.3."""
    return [
        ("Ra_C", "Ra_D"),
        ("Ra_C", "Ra_E"),
        ("Ra_D", "Ra_E"),
    ]
