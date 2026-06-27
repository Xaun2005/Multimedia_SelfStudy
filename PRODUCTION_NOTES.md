# 剪輯製作筆記 — The Last Prompt(給你照著剪用)

把 `handoff/05_finalizer.json` 的內容翻成白話 + 加上 **Shotcut 怎麼做** + **免費素材去哪抓**。
影片:60 秒、16:9、1080p。工具:Shotcut(`E:\programFiles\Shotcut\shotcut.exe`)。

---

## 開工前(做一次)

1. 開 Shotcut → Settings → Video Mode → **HD 1080p 30fps**(16:9)。
2. Settings → **   → Custom** → 指到 `E:`(快取不塞 C:)。
3. 匯入音樂:`Voxel Revolution.mp3`、`Rains Will Fall.mp3`,放到音軌。
4. **標節拍**:播放 Voxel,跟著拍子按 `M` 在音軌上插 marker;之後畫面切點都對到 marker(Shotcut 不會自動抓拍,要手動標)。

## Shotcut 技巧速查(會一直用到)

| 想做的事 | Shotcut 怎麼做 |
|---|---|
| 放字卡 | `Open Other → Text` 做純字卡片段;或上層軌片段加 `Filters → Text: Simple` |
| 擠壓/縮放律動 | `Filters → Size, Position & Rotate` → 點碼錶開 keyframe,對著 marker 做縮放/位移 |
| 疊裂紋/glitch/overlay | 上層軌放 overlay 素材 → `Filters → Blend Mode`(screen/add)或 `Opacity`,用 keyframe 讓它漸強 |
| 左右分割 | 兩段各放上下軌,各加 `Size, Position & Rotate` 縮成左右半 + `Crop: Rectangle` |
| 對拍切點 | 對齊 marker 按 `S` 切開,或拖片段邊緣吸附 marker |
| 淡入/淡出黑 | 拉片段右上/左上角的淡化圓點;或 `Filters → Fade Out Video` |
| 調色(冷/暖) | `Filters → Color Grading`(Lift/Gamma/Gain)+ `Saturation`、`White Balance` |
| 上字幕檔 | `View → Subtitles` 面板 → 匯入 `outputs/subtitles.srt`(時間已對好),匯出時燒進畫面 |
| 輸出 | `Export` → 選 **H.264 / MP4** → 1080p,輸出到 `outputs/final_video.mp4` |

## 免費素材去哪抓(全部零付費)

| 類型 | 去哪 | 搜尋字 |
|---|---|---|
| 影片素材 | **Pexels / Pixabay / Mixkit** | campfire, keyboard typing, hands working, smoke |
| glitch / 裂紋 / TV-off overlay | **Mixkit / Pixabay** | glitch overlay, broken screen, VHS, tv turn off |
| 音效(關機/營火/Foley) | **Freesound(注意每個音的 CC 等級)/ Pixabay** | tv power off, campfire crackle, tool hit |
| 音樂 | **incompetech.com**(Kevin MacLeod,CC-BY) | 你的兩首已選好 |
| 公共領域圖/影 | **Wikimedia Commons / NASA(images.nasa.gov)/ Internet Archive** | rocket launch, manuscript, cave painting |
| 自己拍(最推薦) | 手機 | 你的手:鍵盤、雕刻、寫字、紙飛機、草稿紙 |

> 凡是抓回來的,把來源+授權記進 `outputs/asset_sources.md`,片尾也要列。

---

## 逐場剪輯(17 場,共 60 秒)

### Part 1 — AI 勝過工具(0–14s,音樂 Voxel,冷藍紫)

**Scene 1 ｜ 0–4s ｜ 無字卡**
- 畫面:左右分割,左=舊工具(紙筆、計算機),右=AI 介面;前 2s 靜,3–4s AI 方塊往左擠約 30%。
- Shotcut:上下兩軌左右擺位(Size+Crop);AI 那層用 keyframe 在第 3 拍放大一點。
- 素材:自製 AI 介面(可截圖/AI 生圖)、舊工具靜物(自拍或 Pexels)。

**Scene 2 ｜ 4–9s ｜ 無字卡**
- 畫面:AI 佔更多(3:7),左邊人影模糊,螢幕第一道裂紋。
- Shotcut:分割線位移 keyframe;上層疊「裂紋 overlay」用 Blend Mode,Opacity 從 0 漸起。
- 素材:人影背影(自拍剪影)、裂紋 overlay(Mixkit)。

**Scene 3 ｜ 9–14s ｜ 無字卡**
- 畫面:AI 填滿 90%,人手指懸空搆不到,裂紋遍佈,冷色拉到最飽和。
- Shotcut:AI 層縮放到近滿版;Saturation 拉高、色溫偏藍。
- 素材:手指懸空(自拍手)、密集介面(AI 生圖)。

### Part 2 — Prompt 升級失控(14–21s,Voxel 最 high)

> 重點:**5 張卡踩在拍點上**,一張比一張急,人影一張比一張淡。

**Scene 4–7 ｜ 各 0.8s ｜ 字卡:Write my essay / Write my code / Write my email / Tell me what to think**
- 畫面:黑底白字卡,游標閃爍越來越快,人影粒子化越來越淡;背景藍漸紫。
- Shotcut:每張卡一個 Text 片段對齊一個 marker(0.8s);游標可用一個閃爍的小直線片段(Opacity keyframe 一閃一閃)。
- 素材:純自製(文字 + 色塊),不用外部素材。

**Scene 8 ｜ 17.2–21s ｜ 字卡:Tell me who I am**
- 畫面:最後一張卡停久一點(約 3.8s),人影完全消失,只剩游標在全黑裡;**最後 0.3s 放「關機音」**。
- Shotcut:背景轉純黑;末尾插關機音效;接 Scene 9。
- 素材:關機音效(Freesound「tv power off」)。

### Part 3 — 斷電 + 提問(21–26s)

**Scene 9 ｜ 21–23s ｜ 無字卡**
- 畫面:光線從邊往中收乾→全黑;**靜默 1–1.5 秒(別手軟,這是全片靈魂)**。
- Shotcut:黑色片段;這段音軌「靜音」;前面音樂用 Fade Out 收掉。

**Scene 10 ｜ 23–26s ｜ 字卡(兩行):If AI can create anything, / what is left for us to create?**
- 畫面:黑暗中營火從下方漸亮、暖橙紅;字卡兩行居中浮現;**營火聲從這裡開始,一直到片尾都在(很小聲)**。
- Shotcut:營火素材 Fade In;Text 片段分兩行;色溫轉暖;加營火聲音軌。
- 素材:營火影片(Pexels/自拍)、營火聲(Freesound/Pixabay)。

### Part 4 — 人類的答案:創造的「過程」(26–56s,音樂 Rains Will Fall,暖色)

> 重點:放**過程**不是成品。隨鋼琴節拍上畫面。**最推薦自己拍手**。

**Scene 11 ｜ 26–32s ｜ 無字卡**
- 畫面:營火光下,手磨石器(石屑飛散)+ 草稿紙劃掉塗黑。
- 素材:自拍手 + 草稿紙;或 Pixabay「stone carving」。

**Scene 12 ｜ 32–38s ｜ 無字卡**
- 畫面:黑板算到一半被擦掉 → 紙飛機推出去墜落 → 撿回來重組。
- 素材:自拍(紙飛機最好自己拍,60fps)。

**Scene 13 ｜ 38–44s ｜ 無字卡**
- 畫面:火箭爆炸 → 人在廢墟重組,營火在身後。
- 素材:火箭=NASA(images.nasa.gov)或特效庫;**確認授權**。

**Scene 14 ｜ 44–50s ｜ 無字卡(全片情感重點)**
- 畫面:鑿刻→焊接火花→手寫,切到**黑暗中磨損雙手特寫**(指紋、老繭微距)。這就是「process = soul」。
- Shotcut:前面快切,最後雙手特寫停久一點;營火微光打在手上;音樂這裡開始準備漸淡。
- 素材:**自拍自己的手**(微距,最有感、最省、最呼應主題)。

**Scene 15 ｜ 50–56s ｜ 無字卡**
- 畫面:蒙太奇——織布 → 素描 → 彈樂器,各約 1.5s;音樂漸淡。
- 素材:自拍或 Pixabay 手工藝片段。

### Part 5 — 結尾(56–60s)

**Scene 16 ｜ 56–59s ｜ 字卡:Humanity is the prompt.**
- 畫面:手緩緩放上鍵盤 → 指尖按鍵;字卡逐字浮現;光從暖橙轉中性白;**音樂收掉,只剩營火聲**。
- 素材:自拍鍵盤 + 手。

**Scene 17 ｜ 59–60s ｜ 字卡:The Last Prompt**
- 畫面:字卡中央出現 → 漸隱至全黑;**最後一秒完全無聲**(連營火聲也收掉)。
- Shotcut:Text 片段 + Fade Out;音軌最後 Fade Out 到 0。

---

## 聲音時間軸(一眼看懂)

```
0────────────────21  Voxel Revolution(Part 1-2,21s 處 Fade Out)
                 21   關機音效(0.3s)
                 21──23  靜默(全黑)
                    23─────────────────────60  營火聲(很小聲,一直到末秒前)
                       26───────────56  Rains Will Fall(56s 前漸淡收掉)
                                        60 末秒:完全無聲
```

## 收尾檢查(輸出前)

- [ ] 總長 55–65 秒(目標 60)。
- [ ] 字幕已套(`outputs/subtitles.srt`)且看得清楚。
- [ ] 片尾字卡列出:**音樂 Kevin MacLeod(Voxel Revolution / Rains Will Fall, CC-BY)+ 連結**,以及其他外部素材來源。
- [ ] 匯出 `outputs/final_video.mp4`(H.264 / 1080p,< 100MB)。
- [ ] `PRODUCTION_TODO.md` 的授權項都打勾。
