#!/usr/bin/env python3
"""Apply the Backyard Rockets engineering rewrite to the current recovered production IDs."""
from __future__ import annotations

import enhance_backyard_rockets_engineering as enhancement

# Issue 3 was recovered under the PS-prefixed production IDs. Preserve the
# authored page-local changes while targeting the IDs RexPrompt actually loads.
enhancement.PATCHES["S1E03"] = {
    key.replace("BR_S1E03_", "BR_S1E03_PS_", 1): value
    for key, value in enhancement.PATCHES["S1E03"].items()
}

# The recovered Trip Point production sequence has five Act-3 story pages, not
# the older seven-page development sequence. Do not force the obsolete SC07
# recovery beat onto the recovered issue ending; leave that production page intact.
enhancement.PATCHES["S1E04"].pop("BR_S1E04_A03_SC07", None)

if __name__ == "__main__":
    enhancement.main()
