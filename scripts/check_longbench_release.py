#!/usr/bin/env python3
"""Offline checker for the locked LongBench validation-plan candidate."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from rnaobs.external_validation_lock import current_release_status


if __name__ == "__main__":
    print(json.dumps(current_release_status(), indent=2, sort_keys=True))
