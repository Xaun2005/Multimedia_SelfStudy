# Final Agentic Video — 受控式多代理短影片《The Last Prompt》

Multimedia Systems 期末自主學習作業。用 **Hermes Agent** 把短影片製作拆成 5 個 specialized agent,
以 file-based handoff 串成一個**可追蹤、可控制、可重現、零付費 token** 的 workflow,最後產出一支 60 秒短影片。

| | |
|---|---|
| 作者 / 學號 | 吳誌軒 / S11259009 |
| 平台 | Hermes Agent(skills + file-based handoff + 確定性 orchestrator) |
| 短影片 | `outputs/final_video.mp4`(59.96 秒,16:9,含英文字卡) |
| 報告 | `report/Final_Report.pdf` |

> **AI 使用揭露:** 本專案以 Claude 協助設計架構與生成各 agent 內容(開發期 model backend);影片之素材選擇、剪輯、調色、最終創作判斷均由作者完成。零付費 token 路徑(Hermes + 免費/本機模型)可原樣重現。詳見 `report/Final_Report.pdf` §7。

## 怎麼讀這個 repo

| 路徑 | 是什麼 |
|---|---|
| `docs/architecture.md` | **先看這個** — 完整架構設計 |
| `orchestrator/contracts.py` | 交接契約(解析/驗證/合併)single source of truth |
| `orchestrator/pipeline.py` | 確定性外殼(順序/驗證/重試/timeout/trace/有界修正) |
| `agents/<role>/SKILL.md` | 每個 agent 的角色、輸入、輸出格式、工具邊界 |
| `handoff/0X_*.json` | agent 之間的 structured JSON 交接(執行期產生) |
| `traces/execution_trace.md` | 執行紀錄(誰、用哪個模型、耗時、重試) |
| `inputs/topic_brief.json` | Planner 的輸入(主題/受眾/目標/限制) |
| `outputs/` | 最終 `final_video.mp4`、`subtitles.srt`、`asset_sources.md` |
| `baseline/` | 單 agent 一發 prompt 對照組 |
| `report/` | 專案報告 PDF |
| `PRODUCTION_NOTES.md` | **逐場剪輯指南**(白話:每場畫面/字卡/Shotcut 步驟/免費素材來源) |
| `PRODUCTION_TODO.md` | 拍攝/授權待辦清單 |

## 怎麼跑

```bash
# 驗證現有 handoff 契約完整性(不呼叫模型)
python orchestrator/pipeline.py --mode check

# 用 Hermes + 免費/本機模型真跑一遍(可重現路徑)
#   先依 docs/hermes-config.example.yaml 設好 ~/.hermes/config.yaml
python orchestrator/pipeline.py --mode hermes

# 人工指示的有界修正:重跑單一 stage(看完 reviewer feedback 後)
python orchestrator/pipeline.py --revise script
```

## 零付費 token 完成性

基本分 100 分不需購買任何商業 LLM token、不需個人付費 API、不需訂閱 AI 影音服務。
Hermes skill 設定與 file-based handoff 為真;agent 輸出可由免費(OpenRouter free / 本機 Ollama)模型重現;
最終影片以手機拍攝 / 免費剪輯工具 / 開放授權或自製素材完成。素材來源與授權見 `outputs/asset_sources.md`。

## 完成狀態

- [x] 確定性外殼 `orchestrator/`(contracts + pipeline + emit_outputs)
- [x] 五個 agent:planner / script / visual / reviewer / finalizer
- [x] baseline:single-agent(同主題)輸出 + 比較分析
- [x] 主題「The Last Prompt」→ 5 份 handoff + execution_trace + subtitles.srt + asset_sources
- [x] 1 輪有界修正:Reviewer revise(6/10)→ 修 3 項計畫問題 → Reviewer **pass(9/10)**;v1 留存於 `handoff/round0/`
- [x] 60 秒短影片(Shotcut 剪輯)→ `outputs/final_video.mp4`
- [x] 專案報告 → `report/Final_Report.pdf`
