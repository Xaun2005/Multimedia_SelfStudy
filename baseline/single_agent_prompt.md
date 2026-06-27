# Single-Agent Baseline — 一個 prompt、一次生成

作業 §5.3 要求的對照組。**單一 LLM 呼叫**,一次產出整支 60 秒影片的企劃 + 腳本 + 分鏡,
**沒有** specialized agents、**沒有** file-based handoff、**沒有** 逐 stage 驗證、**沒有** retry、**沒有** execution trace。

這就是我們的 multi-agent workflow 要對照、並證明自己更好的「天真做法」。

## 執行方式

把下面 prompt 連同 `inputs/topic_brief.json` 的內容,丟給**一個** LLM 跑一次,
原始輸出存成 `baseline/single_agent_output.md`(用最終定案主題,與 multi-agent 跑同一個主題才公平)。

## The prompt

```text
You are a video production assistant. From the brief below, produce a COMPLETE plan for a
60-second (55-65s) short video in ONE response. Do everything yourself in a single pass:
concept, audience, scene-by-scene narration, subtitles, shot list, asset list, and a short
self-review. Write all human-readable content in Traditional Chinese.

Brief:
<paste the contents of inputs/topic_brief.json here>

Produce, in order:
1. Title, core message, target audience.
2. A scene-by-scene table: time_range, visual, narration, subtitle, shot.
3. Asset list (self-made or openly licensed only).
4. A short self-review covering length, truthfulness, copyright, portrait rights.
```

> 注意:baseline **刻意**不加結構、驗證與 trace —— 它的「缺點」正是用來凸顯 multi-agent 的價值。
> 不要替 baseline 補上這些,否則就失去對照意義。
