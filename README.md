# arti-math

在 Claude Code 裡問數學或工程問題時，終端機顯示的 LaTeX 原始碼和 ASCII 圖很難讀。這個 skill 會把回答寫到一個 artifact 網頁上：

- 公式用 MathJax 正式排版，多行推導會對齊
- 電路圖、相量圖、方塊圖用 SVG 畫
- 同一個 session 共用一頁，網址不變，每問一題就往下加一則，上方有目錄
- 終端機只留 2–4 行結論和連結
- 淺色和深色模式都看得清楚，手機也能看

## 需求

- [Claude Code](https://claude.com/claude-code)，並且能使用 **Artifact** 功能（頁面會發佈到 claude.ai，預設只有你自己看得到）

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
- 或直接說「開 artifact 講」「用 artifact 回答」「寫到筆記頁」

同一個 session 已經開過筆記頁之後：

- 「接著寫」「加到筆記」：往下追加一則（預設）
- 「覆蓋筆記」「重寫筆記」：清掉舊內容重來

範例：

```
/arti-math 三相負載 50 MVA、功因 0.8 落後、線電壓 13.8 kV，線電流多少？畫相量圖
```

## 檔案

| 檔案 | 內容 |
|---|---|
| `SKILL.md` | 給 Claude 看的流程說明 |
| `assets/template.html` | 筆記頁模板（版面、配色、MathJax、自動目錄） |

想改外觀，例如字體、配色或答案框顏色，直接改 `assets/template.html` 最上面的 CSS 變數即可。
