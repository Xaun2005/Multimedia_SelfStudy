# Execution Trace

本檔由確定性外殼(`orchestrator/pipeline.py`)在每個 stage 落地時自動蓋章,記錄多代理 pipeline 的實際執行。

**怎麼讀:** pipeline 固定順序為 `Planner → Script → Visual → Reviewer → Finalizer`。`step` 欄的 `1–5` 為第一輪(Round 0),`r1` 為人工觸發的第 1 輪有界修正。每一步的**完整輸出內容**(該 agent 實際產生的 handoff)對應同名檔案:

| step / 階段 | 對應的 handoff 證據 |
|---|---|
| Round 0(14 scenes) | `handoff/round0/01_planner.json … 05_finalizer.json` |
| Round 1(17 scenes,定版) | `handoff/01_planner.json … 05_finalizer.json` |

- **多 agent 分工與交接**:每個 agent 讀上游的 handoff JSON、只新增自己負責的欄位,寫成下一份 handoff —— 交接資料即 `handoff/*.json`,可逐欄追溯。
- **受控修正迴圈**:Round 0 的 Reviewer 給 `verdict: revise (6/10)`;人工依其 `revision_requests` 觸發 Round 1;Round 1 的 Reviewer 給 `verdict: pass (9/10)`。修到此即停(作業上限 1–2 輪)。
- **`retries`**:本次每步一次通過,故為 0;若 agent 輸出不合契約,外殼會帶錯誤回饋(`_fix`)重試(上限 `MAX_CONTRACT_RETRY`)。
- **`model = haiku`**:各 agent 內容由 Claude Haiku 作為 model backend 經外殼的 file-based record 路徑產生(此路徑不量測 wall-clock,故 `elapsed = 0.0`);同一套 Hermes skill 以 `hermes chat` 指向免費 / 本機模型即可原樣重現(見報告 §4 揭露)。

| step | agent | model | status | elapsed(s) | retries | note |
|---|---|---|---|---|---|---|
| 1 `17:39:05` | planner | haiku | OK | 0.0 | 0 | 14 scenes |
| 2 `17:42:56` | script | haiku | OK | 0.0 | 0 | 14 scenes |
| 3 `17:50:02` | visual | haiku | OK | 0.0 | 0 | 14 scenes |
| 4 `17:53:12` | reviewer | haiku | OK | 0.0 | 0 | 14 scenes |
| 5 `17:56:20` | finalizer | haiku | OK | 0.0 | 0 | 14 scenes |
| r1 `18:18:38` | planner | haiku | OK | 0.0 | 0 | 17 scenes |
| r1 `18:20:20` | script | haiku | OK | 0.0 | 0 | 17 scenes |
| r1 `18:23:15` | visual | haiku | OK | 0.0 | 0 | 17 scenes |
| r1 `18:24:57` | reviewer | haiku | OK | 0.0 | 0 | 17 scenes |
| r1 `18:26:16` | finalizer | haiku | OK | 0.0 | 0 | 17 scenes |
