"""Copy the finished poster into the grading output directory.

The sandbox that grades this entry has no network and no Pillow, so the
poster is rendered ahead of time (generate.py) and this entrypoint only
moves the finished bytes to the location the harness reads.
"""
import os
import shutil
from pathlib import Path


def main():
    here = Path(__file__).resolve().parent
    dest = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(here / "entry.png", dest / "entry.png")


if __name__ == "__main__":
    main()
