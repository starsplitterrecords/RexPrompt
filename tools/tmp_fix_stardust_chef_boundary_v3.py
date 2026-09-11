#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import tmp_fix_stardust_chef_boundary as base

ROOT = Path(__file__).resolve().parents[1]
V1 = ROOT / "tools" / "tmp_fix_stardust_chef_boundary.py"
V2 = ROOT / "tools" / "tmp_fix_stardust_chef_boundary_v2.py"

# Reuse the refined v2 definitions, but bind its cleaner to the original v1
# implementation before monkey-patching the base module. This avoids recursion.
original_clean = base.clean_meta_panel
source = V2.read_text(encoding="utf-8")
source = source.split("base.clean_meta_panel = clean_meta_panel", 1)[0]
source = source.replace("text = base.clean_meta_panel(text)", "text = ORIGINAL_CLEAN(text)")
namespace = {
    "ORIGINAL_CLEAN": original_clean,
    "__name__": "stardust_boundary_defs",
    "__file__": str(V2),
}
exec(compile(source, str(V2), "exec"), namespace, namespace)

for name in (
    "clean_meta_panel", "page_props", "visual_clause", "direct_summary",
    "enrich_short_panels", "sanitize_page", "update_validator",
):
    setattr(base, name, namespace[name])

base.SELF = Path(__file__).resolve()
base.main()
for path in (V1, V2):
    if path.exists():
        path.unlink()
