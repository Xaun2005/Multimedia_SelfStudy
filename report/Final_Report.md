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

**為何用 file-based(agent 不手寫 JSON):** LLM 直接輸出 JSON 很容易壞——**尤其是較小的模型,或未針對 tool-calling 特別訓練的模型**,常漏括號、引號或產生不合法 JSON,使整條 pipeline 中斷。本設計把責任反過來:structured JSON 是**交接檔案**的格式,但**產生 JSON 的是工具,不是 agent**。agent 只輸出爛不掉的扁平 `key: value`(scene 用 `scene.N.field`),由 `orchestrator/contracts.py` 解析 → 合併上游 → 驗證 → 寫成 JSON。agent 全程不碰大括號,**結構上壞不了**;只剩「漏欄位」這種語意錯誤,才由 `validate()` 抓出並觸發帶錯誤回饋(`_fix`)的重試。

**為何用確定性外殼(控制旋鈕):** 動機有二:(1) **過去設計 Hermes skill 的經驗——LLM 做得越少越穩**,把順序、驗證、寫檔、trace 全交給確定性程式,輸出才可靠、可重現;(2) 作業明文「**禁止無限 loop**」——當 agent 輸出不合格時要能 retry,**但 retry 必須有界**。因此即使作業沒硬性要求,我們仍把「重試上限、修正輪上限、timeout」做進外殼,視之為「受控」的必要條件。具體旋鈕:固定 pipeline 順序、`MAX_CONTRACT_RETRY`(技術重試,有上限)、`HERMES_TIMEOUT_SEC`(真 wall-clock)、修正輪 ≤ 1–2、每 agent 釘死模型、工具權限收斂(不上網、不動 repo 外檔)、handoff 只帶必要欄位。

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

**multi-agent workflow 的限制(誠實評估):** 即使架構設計良好,multi-agent 也**不是萬靈丹**:
- 它擅長**規劃層**(拆解、分工、錯誤檢查、可追蹤),但**解決不了最難的那一關——素材的選擇與真正的審視**。Reviewer agent 能查「長度 / 版權 / 結構」,卻無法替你判斷「這個火箭鏡頭有沒有靈魂」;那仍是人的工作,也是整個製作最花時間、最關鍵的部分。
- **Reviewer 的『pass』只代表計畫『結構合格』,不代表影片『好看』。** 影片的品質來自後續人工的選材與剪輯,不是 agent 蓋章。
- 換句話說:好的 workflow 把「可自動化的規劃」做到很穩,**但『創作判斷』這條天花板,仍由人決定**——這也呼應了本片主題。

---

## 7. 成本、安全與授權(Cost & Safety)

- **零付費 token 可完成性:** 基本流程不需購買商業 token / 付費 API / AI 影音訂閱。Hermes skill + 免費 / 本機模型即可重現;影片以免費素材 + 免費 Shotcut 完成。
- **受控、無無限 loop:** 修正輪上限 1–2(實跑 1 輪);每呼叫有 timeout;工具權限收斂。
- **版權 / 授權:** 全部素材為 CC / 公共領域 / 免費授權或自製,清單與連結見 `outputs/asset_sources.md`;音樂為 Kevin MacLeod CC-BY,已於片尾標出處。
- **真實性:** 影片為觀念 / 抒情表達,未對真實機構 / 人物作不實宣稱;歷史「過程」畫面為示意,非事實主張。
- **肖像 / 隱私:** 未使用可辨識特定真人之私密影像;手部 / 人像素材取自開放授權圖庫。
- **AI 使用揭露:** 見下。

### AI 使用說明

本專案於開發過程中使用 Anthropic Claude(透過 Claude Code)作為**技術輔助工具**,用途如下:

1. **Agent 框架實作** —— 依作者的需求與設計決策,協助實作確定性 orchestrator(契約解析 / 驗證 / 重試 / trace)與各 agent 的 SKILL.md。
2. **開發期 model backend** —— 五個 agent 的內容由 Claude(Haiku)生成,經外殼驗證後落地為 handoff(屬作業允許之零付費 / 離線生成路徑)。
3. **技術問答** —— Shotcut 操作(分割畫面、keyframe 擠壓、混合模式、調色)、git 上傳,以及免費素材搜尋關鍵字。
4. **文件整理** —— 協助整理檔案結構與文件草稿(README、製作筆記、報告初稿)。

**以下由作者本人完成,為本專案不可取代的核心:** 創作概念與敘事主軸(*The Last Prompt*、五段結構、「Prompt 升級與奪回」);所有素材的挑選與判斷;影片的剪輯、調色、節奏與最終呈現;每一個創作決定(保留什麼、刪除什麼、順序與情緒)。

零付費 token 路徑(Hermes + 免費 / 本機模型)可原樣重現本工作流程。AI 生成素材(Scene 3 的 AI 修圖、Scene 4–7 的溶解人影)已於 `outputs/asset_sources.md` 標明。

> 呼應本片主題:AI 承擔了可被自動化的技術與生成,而「選擇什麼、為何感動、如何呈現」這些需要人類判斷與品味的部分由作者完成 —— 這正是本片所要表達的「人不可被取代」。

---

## 8. Repository 與繳交

- **結構:** `agents/`(Hermes skills)、`orchestrator/`(contracts + pipeline + emit_outputs)、`handoff/`(交接 JSON + `round0/` 對照)、`traces/`、`outputs/`(影片 / 字幕 / 素材表)、`baseline/`、`docs/`、`PRODUCTION_NOTES.md`、`PRODUCTION_TODO.md`。
- **如何閱讀:** 先看 `README.md` 與 `docs/architecture.md`。
- **GitHub(Public):** https://github.com/Xaun2005/Multimedia_SelfStudy
- **繳交方式:** 依作業規定,將上述公開 repo 連結繳交至 Ecourse 作業區。

---

## 9. 學習成果與反思(Learning Outcomes & Reflection)

### 學習目標達成(對照作業 §1.1)

| 學習目標 | 達成方式 |
|---|---|
| 理解 agentic workflow 與單一 prompt 的差異 | 親手做了 single-agent baseline 對照並實測差異(§6) |
| 設計多個職責明確的 specialized agents | 5 個 agent,各只做一件事(§3) |
| 用 Hermes 建立可追蹤的多 agent 流程 | Hermes skills + file-based handoff + execution trace |
| 把影片製作拆成企劃/腳本/分鏡/審查/統整 | Planner→Script→Visual→Reviewer→Finalizer |
| 設計 structured handoff | 契約化 JSON,由工具封裝(§3) |
| 控制模型/成本/工具權限/安全 + 零付費路徑 | 有界修正輪、timeout、權限收斂、零付費可重現(§7) |
| 比較 single-agent 與 multi-agent | §6 baseline 比較 |

### 反思

1. **最大的難關不是技術,是「選對素材」。** 剪輯與調色只能安排與加強,**變不出本來不在畫面裡的東西**——一個鏡頭的情緒來自它「是什麼」。本片親自印證:那排**連續失敗的 NASA 火箭**讓我起雞皮疙瘩,是「選對」而非剪法;**紙飛機**怎麼調色都沒感覺。

2. **那個「選擇」就是人不可被取代的部分。** AI 能生成無限畫面,但「知道哪一個有靈魂、哪一個該留」是人的判斷與品味。我在做這支「AI 取代不了人的創造」的片時,親手摸到了它的核心——**製作的方式,恰好就是影片想說的話。**

3. **multi-agent 也有天花板。** 它把「規劃」做得很穩,卻解決不了真正困難的「審視與選擇」;Reviewer 的 pass 只代表結構合格,不代表影片好看。好的架構降低了混亂,但沒有、也不該取代人的創作判斷。

4. **門檻從來不是能力,是工具與引導。** 過去想做影片,卡在浮水印、沒錢、DaVinci Resolve 太難 + 硬體不足而放棄;這次用免費的 Shotcut + 一步步把技巧拆解,本來搞到快崩潰的 Part 1 擠壓動畫,理解「位置 X 與寬度 W 要一起改」後就通了。這是**第一次把一支自己選材、自己剪的影片完成並上傳**。

5. **用 AI 的正確姿勢:人主導,AI 當鷹架。** 把可自動化的(規劃、樣板程式、技術問答)交給 AI,把需要判斷與品味的(概念、選材、節奏、取捨)留給自己;好的上游設計 + 有界迭代,勝過無止境的微調。

6. **限制與改進:** 受限於免費圖庫,Part 4 部分素材只能「以感覺接近」替代理想畫面,理想是自拍手部以求更真;另一個可強化處是實際以 `hermes chat` 接免費 / 本機模型跑一次,讓平台證據更無懈可擊。

---

*附:`traces/execution_trace.md`(完整執行紀錄)、`handoff/round0/`(修正前版本)、`baseline/`(對照組)為本報告之佐證。*
