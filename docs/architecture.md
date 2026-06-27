# 架構設計書 — 受控式多代理短影片 workflow

## 0. 一句話

**聰明放在外殼,agent 盡量笨。** 外殼(orchestrator)負責順序、檔案、驗證、重試、timeout、trace、有界修正;agent 只負責產內容,而且連 JSON 都不用寫。

## 1. 對應作業評分(為什麼這樣設計)

| 作業要求 | 我們的對應 |
|---|---|
| 真的用 Hermes(平台 20 分) | `agents/*/SKILL.md` 是真 Hermes skill;`pipeline.py --mode hermes` 可真跑 |
| 多代理 + 可追蹤 handoff(20 分) | 5 個 specialized agent,file-based handoff(`handoff/0X_*.json`) |
| structured JSON 交接(§5.1) | 交接檔是 JSON;但由**工具**封裝,不是 agent 手寫 |
| execution trace / 可重現(10 分) | `traces/execution_trace.md` 由外殼蓋章;後端可換(Hermes/子 agent) |
| baseline 比較(10 分) | `baseline/` 單 agent 一發 prompt 版,報告對比 |
| 零付費 token / 受控(5 分) | 免費/本機模型可重現;修正輪有界、無 autonomous loop |

## 2. Pipeline(順序由外殼寫死)

```
topic_brief.json
   │
   ▼
[Planner] ─01─▶ [Script] ─02─▶ [Visual] ─03─▶ [Reviewer] ─04─▶ [Finalizer] ─05─▶ 剪輯包
```

| stage | 只做 | 新增到累積文件的欄位 |
|---|---|---|
| Planner | 企劃 | project_title, core_message, target_audience, scenes[time_range/purpose/visual_plan], asset_policy |
| Script | 旁白/字幕 | voice_tone, scenes[narration/subtitle] |
| Visual | 分鏡/素材 | visual_style, scenes[shot_list/asset_needs], asset_list |
| Reviewer | 查長度/真實性/版權/肖像 | verdict, overall_score, findings, risks, revision_requests |
| Finalizer | 統整成剪輯包 | readme_summary, subtitle_srt, edit_checklist, asset_sources |

每個 stage 的輸出檔是**累積快照**:`05_finalizer.json` 自己就是完整最終文件。

## 3. 交接契約:agent 為什麼不用寫 JSON(§5.1 的解法)

痛點:弱模型輸出 JSON 很容易壞。解法:**agent 只填爛不掉的扁平格式**,工具負責封裝。

agent 輸出:

```out
core_message: AI 會生成,但意義只有人能給
target_audience: 高中生 | 大學生 | 一般觀眾
scene.1.purpose: hook
scene.1.visual_plan: 快速閃過 AI 生圖/寫碼/作曲
```

工具(`contracts.py`)做:`解析 → 合併上游(依 scene_id)→ 驗證必填欄位 → 寫成 JSON 檔`。
agent 全程不碰大括號,所以 handoff JSON **結構上不可能壞**;壞的只可能是「漏填某欄位」,那會被 `validate()` 抓到並重試。

## 4. 控制旋鈕(「受控」的本體,全在外殼)

三種迴圈分清楚:

| 迴圈 | 是什麼 | 上限 |
|---|---|---|
| 主線 pipeline | 5 個 agent 依序各一次 | 固定,不算修正輪 |
| **修正輪** | Reviewer 挑錯 → 重跑 Script/Visual | **人工觸發** `--revise`,有界(作業限 1-2) |
| 技術重試 | 契約壞掉重叫同一 agent | `MAX_CONTRACT_RETRY`(預設 2),屬錯誤處理 |

其他旋鈕:`HERMES_TIMEOUT_SEC`(每次呼叫真 wall-clock)、每個 agent 在 Hermes config 釘死模型、工具權限收掉(不上網、不動 repo 外檔)、handoff 只帶必要欄位。

> 自動修正輪預設**關閉**;要再磨由操作者(human-in-the-loop)下 `--revise`。這是受控,不是 autonomous loop。

## 5. 可換的模型後端 = 可重現性

同一個外殼,換腦袋:

- **`hermes_runner`** — 真跑 `hermes chat`,model backend 指向免費 / 本機模型(OpenRouter free、Ollama)。任何有模型的人都能用這些 SKILL.md 重跑出同樣 pipeline。**這就是可重現性的本體。**
- **離線 / 手動路徑(`record_stage()`)** — 沒有模型 API 時,由外部產生各 stage 內容,外殼一樣負責驗證 / 寫檔 / 記 trace。

trace 的 `model` 欄如實記錄每個 stage 由哪個模型產生,**不偽造「Hermes 真的呼叫 API」的假紀錄**。

## 6. 零付費 token 聲明(草稿)

基本分 100 分可在不買任何商業 token、不用個人付費 API、不訂閱 AI 影音服務下完成:
Hermes skill 設定 + file-based handoff 為真;agent 輸出可由免費(OpenRouter free / 本機 Ollama)模型重現;最終影片用手機 / 免費剪輯 / 開放授權素材完成。
