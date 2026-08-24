#!/usr/bin/env python3
"""Vikings 2026 package entry point.

The original builder reconstructed Vikings from an obsolete recovered export and
rewrote current character, setting, season, and page metadata. That behavior is
retired because the active RexPrompt package now contains approved production
payloads and scoped persistent reference data.

Use this command as an integrity check. Story development and production payloads
must be edited through the current package, then validated with
validate_vikings_2026.py.
"""

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "tools" / "validate_vikings_2026.py"


def main() -> int:
    result = subprocess.run([sys.executable, str(VALIDATOR)], cwd=ROOT)
    if result.returncode:
        return result.returncode
    print("Vikings 2026 package is current; no legacy export rebuild performed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
