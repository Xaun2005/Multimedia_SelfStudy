# Baseline 比較:single-agent vs multi-agent

對照作業 §5.3 與評分表「Evaluation 與 baseline 比較(10 分)」。
下表的**結構性差異**(不依主題)先填好;**主題相關觀察**(打勾欄)等兩邊都用最終主題跑完後補。

## 結構性差異(已知)

| 面向 | Multi-agent workflow(本專案) | Single-agent baseline |
|---|---|---|
| **結構** | 5 個 specialized agent,file-based handoff,累積 JSON 快照 | 一坨文字,責任不分離 |
| **錯誤檢查** | 逐 stage 契約驗證 + retry(把錯誤用 `_fix` 塞回);Reviewer 專責查長度/真實性/版權/肖像 | 只有模型一次性的自評,無強制驗證 |
| **分鏡完整度** | Visual agent 專責,每個 scene 強制有 `shot_list` / `asset_needs` | 分鏡常常薄、不均;無欄位強制 |
| **追蹤性** | `execution_trace.md` 蓋章每一步(agent/model/retry);決策可回溯到 handoff 檔 | 單一輸出,看不出哪個決策來自哪裡 |
| **低資源完成** | 每個 agent 只看必要欄位;修正輪有界;可跑免費/本機模型 | 一個大 prompt,單獨重跑某一段、控成本都較難 |

## 主題相關觀察(主題:The Last Prompt,兩邊同主題各跑一次)

| 項目 | 觀察 |
|---|---|
| baseline 漏掉、但 multi-agent 抓到的問題 | Reviewer agent 具體抓到:Part2 的 prompt 升級被壓縮(只剩 essay→who I am,中間 code/email/think 沒展開)、scene7 字卡是長句 3 秒讀不完、火箭/營火/手部素材來源過於籠統需指定、Part2→Part4 轉折缺提示。baseline 的「自審」只給打勾式檢查,這些一個都沒抓到。 |
| baseline 比較好或夠用的地方 | 誠實說:baseline **一次就產出完整、自洽、可讀的企劃**(含分鏡表 + 自審),速度快。對「需求簡單、不需嚴格控管」的片,baseline 其實夠用。 |
| 兩邊最終計畫的差異 | baseline **自行更改了既定設計**(加入 3-2-1 倒數、把斷電移到 0:28、prompt 升級用三個詞帶過);multi-agent 嚴守 topic_brief 的 5-part 結構與「Prompt 升級→奪回」主軸,且每個決策可回溯到對應 handoff 檔。 |
| 追蹤性 | multi-agent:5 份 handoff JSON + execution_trace 可逐步追;baseline:單一文字塊,無法指出哪個決策來自哪一步。 |
| 結論(誠實) | 對這支**有明確設計、又要嚴格控長度/版權/結構**的片,multi-agent 明顯值得:它擋住了 baseline 會放過的錯誤,並保住了原始設計。但若只是隨手的簡單短片,baseline 更快、成本更低——複雜度要用在對的地方。 |

> 誠實原則:baseline 不是稻草人。若某些面向 baseline 其實夠用,如實寫——這比硬說 multi-agent 全面輾壓更有說服力。
