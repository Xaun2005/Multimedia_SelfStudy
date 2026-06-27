#!/usr/bin/env python3
"""
pipeline.py — 確定性外殼(the deterministic shell)。

職責(全部在這裡,不在 agent):
  1. 固定 pipeline 順序          planner -> script -> visual -> reviewer -> finalizer
  2. 每個 stage 一次性呼叫         讀上游檔 -> 餵 agent -> 解析 -> 合併 -> 驗證 -> 寫檔
  3. 契約重試                     輸出不合契約就重試(技術重試,不算「修正輪」)
  4. timeout                     對 Hermes 子程序設實際 wall-clock
  5. trace                       每一步蓋章寫進 traces/execution_trace.md(誰、用哪個模型、耗時、重試)
  6. 有界的修正輪                 由人/Claude 觸發 --revise(受控,非 autonomous loop)

兩種後端(同一個外殼,換腦袋 -> 這就是可重現性):
  * hermes_runner  —— 真跑 Hermes CLI(有模型/API 的人可重現你的 pipeline)
  * record_stage() —— 離線/手動路徑:外部模型產內容,本檔負責驗證/寫檔/記 trace

用法:
  python pipeline.py --mode hermes          # 用 Hermes 從頭跑一遍(reproducible path)
  python pipeline.py --mode check           # 只驗證現有 handoff/ 的契約完整性
  python pipeline.py --revise script        # 人工指示:重跑單一 stage(有界修正)
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import contracts as C  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
HANDOFF = ROOT / "handoff"
TRACES = ROOT / "traces"
INPUTS = ROOT / "inputs"
TRACE_FILE = TRACES / "execution_trace.md"

HERMES_BIN = os.environ.get("HERMES_BIN", "hermes")
TIMEOUT = int(os.environ.get("HERMES_TIMEOUT_SEC", "120"))
MAX_RETRY = int(os.environ.get("MAX_CONTRACT_RETRY", "2"))


# --------------------------------------------------------------------------
# 檔案 I/O
# --------------------------------------------------------------------------

def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def read_topic_brief() -> dict:
    for name in ("topic_brief.json", "topic_brief.example.json"):
        p = INPUTS / name
        if p.exists():
            return _read_json(p)
    return {}


def read_input(stage: str) -> dict:
    """某 stage 的輸入 = 上一個 stage 的累積快照;planner 的輸入 = topic_brief。"""
    idx = C.STAGES.index(stage)
    if idx == 0:
        return read_topic_brief()
    return _read_json(HANDOFF / C.STAGE_FILE[C.STAGES[idx - 1]])


def latest_doc() -> dict:
    """目前最新的累積文件(給 --revise 用,讓重跑的 stage 看得到 reviewer feedback)。"""
    for stage in reversed(C.STAGES):
        p = HANDOFF / C.STAGE_FILE[stage]
        if p.exists():
            return _read_json(p)
    return read_topic_brief()


def write_handoff(stage: str, merged: dict) -> dict:
    HANDOFF.mkdir(exist_ok=True)
    out = C.canonical(stage, merged)
    (HANDOFF / C.STAGE_FILE[stage]).write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    return out


def stamp_trace(step, stage, model, status, elapsed, retries, note=""):
    TRACES.mkdir(exist_ok=True)
    if not TRACE_FILE.exists():
        TRACE_FILE.write_text(
            "# Execution Trace\n\n"
            "| step | agent | model | status | elapsed(s) | retries | note |\n"
            "|---|---|---|---|---|---|---|\n",
            encoding="utf-8")
    ts = time.strftime("%H:%M:%S")
    with TRACE_FILE.open("a", encoding="utf-8") as fh:
        fh.write("| %s `%s` | %s | %s | %s | %.1f | %s | %s |\n"
                 % (step, ts, stage, model, status, elapsed, retries, str(note)[:140]))


# --------------------------------------------------------------------------
# 離線/手動路徑:把一個 stage 的原始輸出落地
# --------------------------------------------------------------------------

def record_stage(step, stage, raw_text, model="haiku", elapsed=0.0):
    """外部模型產出 raw_text -> 解析/合併上游/驗證/寫檔/記 trace。
    回傳 (ok: bool, merged_or_errors)。驗證失敗不寫檔,讓上層決定重試。"""
    upstream = read_input(stage)
    parsed = C.parse_agent_block(raw_text)
    merged = C.build_merged(upstream, parsed)
    errs = C.validate(stage, merged)
    if errs:
        stamp_trace(step, stage, model, "INVALID", elapsed, 0, "; ".join(errs))
        return False, errs
    write_handoff(stage, merged)
    stamp_trace(step, stage, model, "OK", elapsed, 0,
                "%d scenes" % len(merged.get("scenes", [])))
    return True, merged


# --------------------------------------------------------------------------
# Hermes 路徑(可重現):真跑 hermes CLI
# --------------------------------------------------------------------------

def hermes_runner(stage: str, payload: dict):
    """呼叫 hermes chat --toolsets skills -q '/<stage>-agent <payload_json>'。回傳 (raw_text, elapsed)。"""
    slash = "/%s-agent" % stage
    arg = "%s %s" % (slash, json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    cmd = [HERMES_BIN, "chat", "--toolsets", "skills", "-q", arg]
    t0 = time.time()
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              timeout=TIMEOUT, check=False)
    except FileNotFoundError:
        raise SystemExit("hermes not found in PATH; set $HERMES_BIN or install Hermes Agent.")
    except subprocess.TimeoutExpired:
        return "", time.time() - t0
    return (proc.stdout or ""), time.time() - t0


def _run_one(runner, step, stage, note=""):
    base = read_input(stage)
    last = []
    for attempt in range(MAX_RETRY + 1):
        payload = dict(base)
        if last:  # 重試:把上次的錯誤塞回輸入,讓 agent 知道要改哪裡(不是盲試)
            payload["_fix"] = "前一次輸出不合格,請修正後重新輸出:" + "; ".join(last)
        raw, elapsed = runner(stage, payload)
        merged = C.build_merged(base, C.parse_agent_block(raw))
        errs = C.validate(stage, merged)
        if not errs:
            write_handoff(stage, merged)
            stamp_trace(step, stage, "hermes", "OK", elapsed, attempt,
                        note or "%d scenes" % len(merged.get("scenes", [])))
            return merged
        last = errs
    stamp_trace(step, stage, "hermes", "FAILED", 0.0, MAX_RETRY, "; ".join(last))
    raise SystemExit("[%s] contract failed after %d retries: %s" % (stage, MAX_RETRY, last))


def run_linear(runner):
    """Hermes 模式:固定順序跑完五個 stage(自動修正輪預設關閉,改由 --revise 人工觸發)。"""
    for i, stage in enumerate(C.STAGES, start=1):
        _run_one(runner, i, stage)
    print("pipeline done ->", TRACE_FILE)


def revise(runner, stage):
    """人工指示的有界修正:重跑單一 stage,輸入用最新累積文件(含 reviewer feedback)。"""
    payload = latest_doc()
    merged = C.build_merged(payload, C.parse_agent_block(runner(stage, payload)[0]))
    errs = C.validate(stage, merged)
    if errs:
        raise SystemExit("[revise %s] %s" % (stage, errs))
    write_handoff(stage, merged)
    stamp_trace("R", stage, "hermes", "OK", 0.0, 0, "human-directed revision")
    print("revised:", stage)


def check_only():
    bad = 0
    for stage in C.STAGES:
        p = HANDOFF / C.STAGE_FILE[stage]
        if not p.exists():
            print("  - %-9s : (not produced yet)" % stage)
            continue
        errs = C.validate(stage, _read_json(p))
        mark = "OK" if not errs else "FAIL"
        print("  %s %-9s : %s" % (mark, stage, "; ".join(errs) if errs else "valid"))
        bad += 1 if errs else 0
    return 0 if bad == 0 else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="final-agentic-video deterministic shell")
    ap.add_argument("--mode", choices=["hermes", "check"], default="check")
    ap.add_argument("--revise", choices=C.STAGES, default=None)
    ap.add_argument("--record", choices=C.STAGES, default=None,
                    help="read an agent's raw stdout from stdin and land it as a handoff")
    ap.add_argument("--step", default="?", help="step label for the trace")
    args = ap.parse_args(argv)

    if args.record:
        ok, res = record_stage(args.step, args.record, sys.stdin.read())
        if ok:
            print("OK ->", C.STAGE_FILE[args.record])
            return 0
        print("INVALID:", file=sys.stderr)
        for e in res:
            print("  - " + e, file=sys.stderr)
        return 1
    if args.revise:
        revise(hermes_runner, args.revise)
        return 0
    if args.mode == "hermes":
        run_linear(hermes_runner)
        return 0
    return check_only()


if __name__ == "__main__":
    sys.exit(main())
