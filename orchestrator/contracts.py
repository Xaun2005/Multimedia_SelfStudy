"""
contracts.py — handoff 契約的 single source of truth。

設計重點(對應作業 §5.1 / §5.2、以及「agent 不該手寫 JSON」的痛點):

  * 交接檔案的格式是 structured JSON(handoff/0X_*.json)—— 這是 §5.1 要的。
  * 但「產生 JSON」的責任在『工具』,不在 agent。
    agent 只輸出一段爛不掉的扁平文字:
        ```out
        key: value
        scene.1.purpose: hook
        scene.1.visual_plan: ...
        ```
    本模組負責把它「解析 -> 合併上游 -> 驗證 -> 轉成 canonical dict」,
    再由 pipeline.py 寫成 JSON 檔。agent 全程不碰大括號,壞不了。

  * 每個 stage 的輸出檔都是『累積快照』:上游欄位 + 本 stage 新增欄位。
    所以 05_finalizer.json 自己就是完整的最終文件。

本檔不依賴任何第三方套件(純標準庫),方便在任何環境重現。
"""

from __future__ import annotations

import re
from typing import Any

# pipeline 的固定順序(受控:順序由外殼決定,不由 agent 決定)
STAGES = ["planner", "script", "visual", "reviewer", "finalizer"]

STAGE_FILE = {
    "planner": "01_planner.json",
    "script": "02_script.json",
    "visual": "03_visual.json",
    "reviewer": "04_reviewer.json",
    "finalizer": "05_finalizer.json",
}

# 每個 stage 在『合併後的累積文件』裡必須具備的 top-level 欄位
REQUIRED_TOP = {
    "planner": ["project_title", "target_audience", "core_message",
                "video_length_seconds", "asset_policy", "review_items"],
    "script": ["voice_tone"],
    "visual": ["visual_style"],
    "reviewer": ["verdict", "overall_score"],
    "finalizer": ["readme_summary", "edit_checklist"],
}

# 每個 stage 在每個 scene 內必須具備的子欄位(操作 scenes 的 stage 才檢查)
REQUIRED_SCENE = {
    "planner": ["scene_id", "time_range", "purpose", "visual_plan"],
    "script": ["narration", "subtitle"],
    "visual": ["shot_list", "asset_needs"],
    # finalizer 不重列 scene 欄位:narration/subtitle/shot_list 已在 script/visual 驗過,merge 會保留。
}

# 這些欄位用 "a | b | c" 表示陣列
LIST_FIELDS = {"target_audience", "review_items", "risks",
               "revision_requests", "findings", "asset_list",
               "edit_checklist", "asset_sources"}
INT_FIELDS = {"video_length_seconds", "overall_score", "scene_id"}

_FENCE = re.compile(r"```[a-zA-Z0-9_]*[ \t]*\r?\n(?P<body>.*?)\r?\n```", re.DOTALL)
_SCENE_KEY = re.compile(r"scene\.(\d+)\.(.+)", re.IGNORECASE)


# --------------------------------------------------------------------------
# 解析:agent 文字 -> dict
# --------------------------------------------------------------------------

def extract_block(text: str) -> str:
    """取最後一段 fenced block;沒有 fence 就用全文。"""
    if not isinstance(text, str):
        return ""
    blocks = _FENCE.findall(text)
    return (blocks[-1] if blocks else text).strip()


def _coerce(field: str, val: str) -> Any:
    leaf = field.split(".")[-1]
    if leaf in LIST_FIELDS:
        return [p.strip() for p in val.split("|") if p.strip()]
    if leaf in INT_FIELDS:
        try:
            return int(val)
        except ValueError:
            try:
                return float(val)
            except ValueError:
                return val
    return val


def parse_agent_block(text: str) -> dict:
    """把扁平 `key: value`(含 scene.N.field)解析成 dict。agent 不需要寫 JSON。"""
    body = extract_block(text)
    data: dict = {}
    scenes: dict = {}
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, _, val = line.partition(":")
        key, val = key.strip(), val.strip()
        if not key:
            continue
        m = _SCENE_KEY.match(key)
        if m:
            sid = int(m.group(1))
            field = m.group(2).strip()
            sc = scenes.setdefault(sid, {"scene_id": sid})
            if field == "scene_id":
                continue
            sc[field] = _coerce(field, val)
        else:
            data[key] = _coerce(key, val)
    if scenes:
        data["scenes"] = [scenes[k] for k in sorted(scenes)]
    return data


# --------------------------------------------------------------------------
# 合併 + 驗證
# --------------------------------------------------------------------------

def merge_scenes(base: list, add: list) -> list:
    """以 scene_id 為鍵,把新欄位疊到既有 scene 上(上游資料保留,下游只補欄位)。"""
    by_id: dict = {}
    for s in base or []:
        by_id[s.get("scene_id")] = dict(s)
    for s in add or []:
        sid = s.get("scene_id")
        if sid in by_id:
            by_id[sid].update(s)
        else:
            by_id[sid] = dict(s)
    return [by_id[k] for k in sorted(by_id, key=lambda x: (x is None, x))]


def build_merged(upstream: dict, parsed: dict) -> dict:
    """上游累積文件 + 本 stage 解析結果 -> 新的累積文件。"""
    merged = dict(upstream or {})
    merged.pop("_stage", None)
    base_scenes = merged.get("scenes", [])
    for k, v in parsed.items():
        if k == "scenes":
            continue
        merged[k] = v
    if "scenes" in parsed:
        merged["scenes"] = merge_scenes(base_scenes, parsed["scenes"])
    return merged


def validate(stage: str, data: dict) -> list:
    """回傳 error 字串清單;空 list = 合格。"""
    errs = []
    for k in REQUIRED_TOP.get(stage, []):
        if k not in data or data[k] in ("", [], None):
            errs.append("missing/empty top-level field: %s" % k)
    if stage in REQUIRED_SCENE:
        scenes = data.get("scenes")
        if not scenes:
            errs.append("missing scenes[]")
        else:
            for sc in scenes:
                for f in REQUIRED_SCENE[stage]:
                    if f not in sc or sc[f] in ("", [], None):
                        errs.append("scene %s: missing %s" % (sc.get("scene_id", "?"), f))
    return errs


def canonical(stage: str, merged: dict) -> dict:
    """加上 stage 標記,回傳要寫進檔案的 dict。"""
    out = {"_stage": stage}
    out.update(merged)
    return out


def emit(stage: str, raw_text: str) -> dict:
    """skill 工具用:parse + 驗證該 stage 自身欄位 -> canonical dict。
    不合格時 raise ValueError(error_list)。"""
    parsed = parse_agent_block(raw_text)
    errs = validate(stage, parsed)
    if errs:
        raise ValueError(errs)
    return canonical(stage, parsed)
