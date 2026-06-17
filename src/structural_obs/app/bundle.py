#!/usr/bin/env python3
"""Build in-memory ZIP bundles for UI download."""

from __future__ import annotations

import io
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory

from structural_obs.toolkit.services.audit_export import write_run_artifacts
from structural_obs.toolkit.services.classify_service import CaseRunResult


def build_audit_zip(run: CaseRunResult) -> bytes:
    """Write audit artifacts to a temporary folder and return ZIP bytes."""
    buffer = io.BytesIO()
    with TemporaryDirectory() as tmp:
        out_dir = Path(tmp) / "export"
        write_run_artifacts(run, out_dir)
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(out_dir.rglob("*")):
                if path.is_file():
                    archive.write(path, arcname=path.relative_to(out_dir).as_posix())
    return buffer.getvalue()
