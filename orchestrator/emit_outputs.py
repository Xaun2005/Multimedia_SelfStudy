#!/usr/bin/env python3
"""
emit_outputs.py — 從 05_finalizer.json 產生可交付產物(確定性,不靠 LLM):
  - outputs/subtitles.srt      由每個 scene 的 time_range + subtitle 生成
  - outputs/asset_sources.md   由 asset_sources(+ 固定音樂歸屬)生成

字幕 .srt 由本工具自動產生,Finalizer agent 不需手寫。
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HANDOFF = ROOT / "handoff"
OUTPUTS = ROOT / "outputs"
SKIP_SUBS = {"(無字卡)", "(silence)", "(none)", "(無)", ""}


def srt_time(sec: float) -> str:
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    ms = int(round((sec - int(sec)) * 1000))
    return "%02d:%02d:%02d,%03d" % (h, m, s, ms)


def parse_range(tr: str):
    nums = re.findall(r"\d+(?:\.\d+)?", str(tr))
    return (float(nums[0]), float(nums[1])) if len(nums) >= 2 else None


def main() -> int:
    OUTPUTS.mkdir(exist_ok=True)
    data = json.loads((HANDOFF / "05_finalizer.json").read_text(encoding="utf-8"))

    # --- subtitles.srt ---
    lines = []
    idx = 0
    for sc in data.get("scenes", []):
        sub = str(sc.get("subtitle", "")).strip()
        rng = parse_range(sc.get("time_range", ""))
        if not rng or sub in SKIP_SUBS:
            continue
        idx += 1
        lines += [str(idx), "%s --> %s" % (srt_time(rng[0]), srt_time(rng[1])), sub, ""]
    (OUTPUTS / "subtitles.srt").write_text("\n".join(lines), encoding="utf-8")

    # --- asset_sources.md ---
    md = [
        "# 素材來源與授權 (asset sources)",
        "",
        "## 音樂",
        '- "Voxel Revolution" — Kevin MacLeod (incompetech.com) — CC-BY 4.0',
        '- "Rains Will Fall" — Kevin MacLeod (incompetech.com) — CC-BY 4.0',
        "",
        "## 其他素材(待逐項補上確切來源連結)",
    ]
    for a in data.get("asset_sources", []):
        md.append("- " + str(a))
    (OUTPUTS / "asset_sources.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print("subtitles.srt: %d cues" % idx)
    print("asset_sources.md: %d asset lines" % len(data.get("asset_sources", [])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
