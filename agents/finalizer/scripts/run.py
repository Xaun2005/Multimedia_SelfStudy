#!/usr/bin/env python3
"""finalizer/scripts/run.py — Finalizer 的 call tool 封裝器。

agent 輸出扁平 `key: value`(見 SKILL.md);本工具解析 + 驗證 + 印出 JSON。
驗證失敗 -> stderr + exit 1。只依賴 orchestrator/contracts.py。"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "orchestrator"))
import contracts as C  # noqa: E402

STAGE = "finalizer"


def main() -> int:
    raw = sys.stdin.read()
    if not raw.strip():
        print("error: no input on stdin (expected the `key: value` block)", file=sys.stderr)
        return 1
    try:
        out = C.emit(STAGE, raw)
    except ValueError as e:
        print("contract validation failed:", file=sys.stderr)
        for x in e.args[0]:
            print("  - " + x, file=sys.stderr)
        return 1
    print("```json")
    print(json.dumps(out, ensure_ascii=False, indent=2))
    print("```")
    return 0


if __name__ == "__main__":
    sys.exit(main())
