"""Deliver the rendered poster to the grading output folder.

generate.py draws entry.png ahead of time. The grading sandbox has no
network access and no Pillow, so this entrypoint only copies the finished
bytes to the location the harness reads."""
import os
from pathlib import Path


def deliver():
    root = Path(__file__).resolve().parent
    out = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out.mkdir(parents=True, exist_ok=True)
    (out / "entry.png").write_bytes((root / "entry.png").read_bytes())


deliver()
