# arti-math

在 Claude Code 裡問數學或工程問題時，終端機顯示的 LaTeX 原始碼和 ASCII 圖很難讀。這個 skill 會把回答做成一份 artifact 網頁投影片：

- 16:9 一頁一個重點，用 ←/→、按鈕、手機滑動或下拉選單翻頁，舞台會依視窗大小自動縮放
- 公式用 MathJax 正式排版，多行推導會對齊
- 電路圖、相量圖、方塊圖用 SVG 畫
- 概念頁後面接一頁例題（左題目、右解法、黃底答案）
- 同一個 session 共用一份投影片，網址不變，每問一題就在後面加幾頁，打開時直接停在最新一題
- 內容太多時自動縮小，縮到 70% 還放不下會在該頁標紅字提醒
- 可以「帶我讀第 N 章」做整章導讀，原始檔存在課程資料夾，之後的 session 接著用同一個連結
- 終端機只留 2–4 行結論和連結
- 淺色和深色模式都看得清楚，手機也能看

## 需求

- [Claude Code](https://claude.com/claude-code)，並且能使用 **Artifact** 功能（頁面會發佈到 claude.ai，預設只有你自己看得到）
- 搭配 PDF 裁圖時需要 Python 和 PyMuPDF：`pip install pymupdf`

## 安裝

把這個 repo clone 到 Claude Code 的 skills 資料夾：

```bash
git clone https://github.com/Heart-0001/arti-math.git ~/.claude/skills/arti-math
```

Windows（PowerShell）：

```powershell
git clone https://github.com/Heart-0001/arti-math.git "$HOME\.claude\skills\arti-math"
```

裝好後開一個新的 Claude Code session 就能用。之後要更新，到該資料夾執行 `git pull`。

## 使用

只有你明確要求時才會啟動，不會自己跳出來：

- 輸入 `/arti-math`，後面接你的問題
- 或直接說「開 artifact 講」「用投影片講」「做成投影片」「帶我讀第 5 章」

同一個 session 已經有投影片之後：

- 「接著寫」「下一題」「加到投影片」：在後面加頁（預設）
- 「覆蓋」「重寫」：清掉舊內容重來

範例：

```
/arti-math 三相負載 50 MVA、功因 0.8 落後、線電壓 13.8 kV，線電流多少？畫相量圖
/arti-math 帶我看 Power Systems/Chapter3 Sol.pdf 的 3.10
/arti-math 帶我讀電力系統第 5 章，每個概念後面接一題作業當例題
```

## 檔案

| 檔案 | 內容 |
|---|---|
| `SKILL.md` | 給 Claude 看的流程說明 |
| `assets/template.html` | 投影片模板（舞台縮放、翻頁、頁面選單、自動縮字、配色、MathJax） |
| `scripts/pdfcrop.py` | 在 PDF 裡找題號、預覽頁面、裁出淺色和深色兩版的圖 |

想改外觀，例如字體、配色或答案框顏色，直接改 `assets/template.html` 最上面的 CSS 變數即可。
