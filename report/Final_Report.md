# Final 自主學習報告 — 受控式多代理人短影片工作流程
## 《The Last Prompt》

| | |
|---|---|
| **作業** | Multimedia Systems — Final 自主學習:OpenClaw / Hermes Agent 多代理人短影片工作流程 |
| **平台** | Hermes Agent(skills + file-based handoff + 確定性 orchestrator) |
| **多媒體成果** | 一支 60 秒短影片(`outputs/final_video.mp4`,實長 59.96s) |
| **學生 / 學號** | 吳誌軒 / S11259009 |
| **GitHub Repo** | https://github.com/Xaun2005/Multimedia_SelfStudy |
| **日期** | 2026/6/28 |

---

## 1. 問題定義(Problem Definition)

**主題:** *The Last Prompt* —— 在 AI 時代,人不可被取代的創造與靈魂。
**核心訊息:** AI 再強,也無法取代人類「創造的過程」;真正決定世界方向的「最後一個 prompt」,是人類自己。
**目標受眾:** 對 AI 焦慮的一般觀眾、高中與大學生。
**與課程關聯:** 屬「AI 應用 / 社會應用」範疇;以 prompt 的「升級與奪回」為唯一敘事主軸。
**主題獨立性:** 與本人 Lab1–3 的題目(camera 廣告、AI 殺軟體對決)不同,為全新題材。

---

## 2. 系統總覽(System Overview)

本專案的設計核心是一句話:**「把聰明放在外殼,讓 agent 盡量笨。」**

```
inputs/topic_brief.json
        │
        ▼
[Planner] ─01─▶ [Script] ─02─▶ [Visual] ─03─▶ [Reviewer] ─04─▶ [Finalizer] ─05─▶ 剪輯包
        └──────────────── 確定性外殼(orchestrator)驅動 ────────────────┘
```

- **平台 = Hermes Agent。** 五個 agent 以 Hermes skill 形式定義(`agents/<role>/SKILL.md` + `scripts/run.py` 工具),交接採 **file-based**(`handoff/0X_*.json`)。
- **確定性外殼(`orchestrator/`)** 負責:固定順序、契約驗證、契約重試、timeout、execution trace、以及有界的修正輪。agent 只負責「產內容」。
- **可重現性:** 同一套 skill 可由 `hermes chat` 指向任何免費 / 本機模型重跑(見 `docs/hermes-config.example.yaml`),這就是零付費 token 路徑的本體。

---

## 3. Agent 設計(Agent Design)

| Agent | 角色(只做一件事) | 輸入 | 輸出 |
|---|---|---|---|
| **Planner** | 企劃 / 分鏡導演 | topic_brief | core_message、target_audience、scene outline(time_range/purpose/visual_plan) |
| **Script** | 腳本作者 | 上游 scenes | voice_tone、每 scene 的 narration / subtitle(字卡) |
| **Visual** | 分鏡 / 美術 | 上游 scenes | visual_style、每 scene 的 shot_list / asset_needs、asset_list |
| **Reviewer** | 嚴格審查者 | 完整計畫 | verdict、score、findings、risks、revision_requests |
| **Finalizer** | 製作統整 | 完整 + 審查 | readme_summary、edit_checklist、asset_sources |

**「agent 不手寫 JSON」的設計(§5.1 的解法):** structured JSON 是**交接檔案**的格式;但**產生 JSON 的責任在工具,不在 agent**。agent 只輸出爛不掉的扁平 `key: value`(scene 用 `scene.N.field`),由 `orchestrator/contracts.py` 解析 → 合併上游 → 驗證 → 寫成 JSON。agent 全程不碰大括號,結構上壞不了;缺欄位則由 `validate()` 抓出並觸發帶錯誤回饋(`_fix`)的重試。

**控制旋鈕(「受控」的本體):** 固定 pipeline 順序、`MAX_CONTRACT_RETRY`(技術重試)、`HERMES_TIMEOUT_SEC`(真 wall-clock)、每 agent 釘死模型、工具權限收斂(不上網、不動 repo 外檔)、handoff 只帶必要欄位。

---

## 4. Workflow 執行(Workflow Execution)

實際執行了 **兩輪**,完整紀錄於 `traces/execution_trace.md`:

| 階段 | 步驟 | 結果 |
|---|---|---|
| **Round 0** | Planner→Script→Visual→Reviewer→Finalizer(14 scenes) | Reviewer **verdict: revise(6/10)** |
| **Round 1(有界修正)** | 同 5 步(17 scenes) | Reviewer **verdict: pass(9/10)** |

**Reviewer 在 Round 0 抓到的具體問題 →（Round 1 修正):**
1. Part 2 的 prompt 升級被壓縮(只剩 essay + who I am)→ 拆成 **5 張獨立字卡**(essay / code / email / think / who I am)。
2. Part 3 問句一行太長,3 秒讀不完 → 拆成兩行。
3. Part 2 → Part 4 轉折太跳 → 新增「磨損的手 = process is soul」過場(scene 14)。

修到此 **stop**(符合作業「最多 1–2 輪、禁止無限 loop」)。其餘 Reviewer 意見屬「人工製作 / 授權確認」項,不是計畫層面修改,移交人工(見 `PRODUCTION_TODO.md`)。Round 0 版本保留於 `handoff/round0/` 作為修正前後對照。

> **平台與生成揭露:** Hermes skill 設定、file-based handoff、確定性外殼皆為真;execution trace 為真實 file-based 紀錄。因未使用付費 API,各 agent 的**內容**由可用 LLM(Claude Haiku)作為 model backend 經外殼的離線 record 路徑產生(屬作業允許之「Hermes + 離線 / mock 輸出」滿分路徑);同一套 skill 以 `hermes chat` 指向免費 / 本機模型即可原樣重現。

---

## 5. 影片成果(Video Output)

**檔案:** `outputs/final_video.mp4` ｜ **長度:59.96 秒**(55–65 規格內)｜ 16:9 ｜ 含英文字卡(`outputs/subtitles.srt`)。
編輯工具:**Shotcut(免安裝版)**。完整剪輯指南見 `PRODUCTION_NOTES.md`。

**實際結構與素材(對照 handoff 計畫,並標出本人在剪輯時的調整):**

| Part | 時間 | 內容 | 實際素材 |
|---|---|---|---|
| 1 AI vs 工具 | 0–12s | **真實產品對比**:維基↔ChatGPT、VS Code↔Claude、修圖↔AI 生圖,疊 glitch/裂紋 | 介面截圖 + Pixabay glitch 影片 |
| 2 Prompt 升級 | 12–21s | 5 張字卡 essay→code→email→think→who I am + 溶解人影 | 自製字卡 + AI 生成人影 |
| 3 斷電 + 提問 | 20.5–26s | TV 關機音 → 燭火浮現 + 兩行問句 | Pixabay 火粒子 + TV 關機音 |
| 4 創造的過程 | 26–56s | 石器、草稿、黑板、紙飛機、**NASA 連續失敗火箭**、雕木、磨損的手 | Pixabay / Unsplash / NASA |
| 5 結尾 | 56–60s | Humanity is the prompt → The Last Prompt | 自製字卡 |

**音軌:** Voxel Revolution(0–21,Part 1–2)、Rains Will Fall(26–56,Part 4)、營火聲(23–尾)、TV 關機音(~20.5)。

**剪輯時本人的關鍵調整(與計畫的出入):**
- 把計畫的「抽象冷色 AI 介面」**改為真實產品截圖對比**(ChatGPT/Claude/VS Code/Adobe)——更具體、更易被觀眾一秒理解。
- 大量採用**靜態圖片 + Shotcut 動畫(縮放 / 擠壓 keyframe / 調色)**,而非影片素材;Part 1 的左右擠壓以「尺寸、位置&旋轉」keyframe 完成。
- 採用**統一暖色 + 微做舊調色**把雜來源的 Part 4 黏成一體;低畫質的 NASA 失敗火箭反而成為情感最強的一段。
- 素材全部為網路免費 / 公共領域 / CC,AI 生成部分已揭露(見 §8 與 `outputs/asset_sources.md`)。

---

## 6. 評估與 baseline 比較(Evaluation)

依作業 §5.3,另建一個 **single-agent baseline**(一個 prompt 一次全包,無分工、無 handoff、無驗證、無 trace;同主題),完整輸出於 `baseline/single_agent_output.md`,比較於 `baseline/comparison.md`。

| 面向 | Multi-agent workflow | Single-agent baseline |
|---|---|---|
| 結構 | 5 個專責 agent、file-based 累積快照 | 一坨文字,責任不分 |
| 錯誤檢查 | 逐 stage 契約驗證 + 重試;Reviewer 專查長度/真實性/版權/連貫 | 只有模型一次性自評 |
| 追蹤性 | trace + handoff,決策可回溯 | 單一輸出,無法定位 |
| 受控修正 | 示範 revise(6)→ 修 → pass(9) 的**有界**迴圈 | 無 |

**實測差異(同主題):** Reviewer agent 具體抓到 baseline 自評完全沒抓到的問題(prompt 升級被壓縮、字卡過長、素材來源需指定);baseline 還**自行更改了既定結構**(加 3-2-1 倒數、移動斷電點)。**誠實補充:** baseline 一次就產出完整自洽的企劃,對「簡單、不需嚴管」的片其實夠快——複雜度該用在對的地方。

---

## 7. 成本、安全與授權(Cost & Safety)

- **零付費 token 可完成性:** 基本流程不需購買商業 token / 付費 API / AI 影音訂閱。Hermes skill + 免費 / 本機模型即可重現;影片以免費素材 + 免費 Shotcut 完成。
- **受控、無無限 loop:** 修正輪上限 1–2(實跑 1 輪);每呼叫有 timeout;工具權限收斂。
- **版權 / 授權:** 全部素材為 CC / 公共領域 / 免費授權或自製,清單與連結見 `outputs/asset_sources.md`;音樂為 Kevin MacLeod CC-BY,已於片尾標出處。
- **真實性:** 影片為觀念 / 抒情表達,未對真實機構 / 人物作不實宣稱;歷史「過程」畫面為示意,非事實主張。
- **肖像 / 隱私:** 未使用可辨識特定真人之私密影像;手部 / 人像素材取自開放授權圖庫。
- **AI 使用揭露:** 見下。

> **AI 使用揭露(草稿,請本人確認 / 補充):** 本專案使用 Claude(Claude Code)協助:① 設計 Hermes agent 架構與確定性外殼程式;② 作為開發期 model backend 生成各 agent 內容(Haiku);③ 協助找素材關鍵字與 Shotcut 技巧。**影片之素材選擇、剪輯、調色、最終創作判斷均由本人完成。** 零付費 token 路徑(Hermes + 免費 / 本機模型)可原樣重現本工作流程。Scene 3 的「AI 修圖」與 Scene 4–7 的溶解人影為 AI 生成素材,已於素材表標明。

---

## 8. Repository 與繳交

- **結構:** `agents/`(Hermes skills)、`orchestrator/`(contracts + pipeline + emit_outputs)、`handoff/`(交接 JSON + `round0/` 對照)、`traces/`、`outputs/`(影片 / 字幕 / 素材表)、`baseline/`、`docs/`、`PRODUCTION_NOTES.md`、`PRODUCTION_TODO.md`。
- **如何閱讀:** 先看 `README.md` 與 `docs/architecture.md`。
- **GitHub(Public):** https://github.com/Xaun2005/Multimedia_SelfStudy
- **繳交方式:** 依作業規定,將上述公開 repo 連結繳交至 Ecourse 作業區。

---

## 9. 反思(Reflection)

做完整支片,最大的體悟不是剪輯手法或調色,而是 **「選對素材」才是真正的難關**。

- 剪輯與調色只能「安排」與「加強」,**變不出本來不在畫面裡的東西**。一個鏡頭的情緒來自它「是什麼」,不是怎麼切。本片親自印證:那排**連續失敗的 NASA 火箭**讓我起雞皮疙瘩,是「選對」而非剪法;**紙飛機**無論怎麼調色都沒感覺。
- AI 可以生成無限畫面,但**知道哪一個有靈魂、哪一個該留**——那個「選擇」就是人的判斷與品味。我在做這支「AI 取代不了人的創造」的片時,親手摸到了它的核心:**最不可被取代的,正是那個『感覺對不對』的選擇。** 製作的方式,恰好就是影片想說的話。
- **限制與改進:** 受限於免費圖庫,Part 4 部分素材只能「以感覺接近」替代理想畫面;若有時間,理想是自拍手部以求更真。多 agent workflow 的價值在「有明確設計、要嚴管長度 / 版權 / 結構」時最明顯;若僅是簡單短片,single-agent 反而更快——複雜度要用在對的地方。

---

*附:`traces/execution_trace.md`(完整執行紀錄)、`handoff/round0/`(修正前版本)、`baseline/`(對照組)為本報告之佐證。*
