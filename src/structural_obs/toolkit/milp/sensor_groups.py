#!/usr/bin/env python3
"""URS document sensor groups for MILP engineering rules."""

from __future__ import annotations

from typing import Dict, List

SensorGroups = Dict[str, List[str]]


def sensor_groups_urs_document() -> SensorGroups:
    """Groups used by URS ILP rules (Eq1-Eq19 document model)."""
    return {
        "principais": ["F", "R"],
        "permeados": ["PA", "PB", "PC", "PD", "PE"],
        "Ra": ["Ra_A", "Ra_B", "Ra_C", "Ra_D", "Ra_E"],
        "Rb": ["Rb_A", "Rb_B", "Rb_C", "Rb_D", "Rb_E"],
        "Rc": ["Rc_A", "Rc_B", "Rc_C", "Rc_D", "Rc_E"],
        "Pa": ["Pa_A", "Pa_B", "Pa_C", "Pa_D", "Pa_E"],
        "Pb": ["Pb_A", "Pb_B", "Pb_C", "Pb_D", "Pb_E"],
        "Pc": ["Pc_A", "Pc_B", "Pc_C", "Pc_D", "Pc_E"],
    }
