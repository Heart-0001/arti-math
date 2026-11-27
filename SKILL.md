---
name: arti-math
description: Write the current answer as 16:9 slides on a per-session artifact deck — one idea per slide, page with arrow keys, math typeset with MathJax, diagrams drawn as inline SVG — and leave only a short summary plus the link in the terminal. Use ONLY when the user explicitly asks for it, e.g. types /arti-math, or says 「開 artifact 講」「用 artifact 回答」「做成投影片」「用投影片講」「寫到筆記頁」「這題畫在頁面上」「放到 artifact」「帶我讀第 N 章」, or, once a deck exists in this session, says 「接著寫」「下一題」「加到投影片」「加到筆記」「覆蓋」「重寫」. Once the deck exists, short follow-up questions (wording, concept checks, one-line "why") are answered in the terminal, not on the deck — see "Deck or terminal?". Do not use it on your own initiative when the user has not mentioned an artifact, slides or the notebook page.
---

# arti-math — slide deck for math and diagrams

The user studies engineering courses inside Claude Code. Raw LaTeX and ASCII diagrams in the terminal are hard to read, so this skill puts the answer on a web page laid out as 16:9 slides: a fixed 1280×720 stage that scales to the window, one idea per slide, paged with ←/→, buttons, swipe, or a page menu. Formulas are typeset and circuits, phasor diagrams, etc. are drawn. The terminal keeps only a few lines and the link.

It is a plain HTML artifact on purpose: the Slides artifact type cannot render math, so do not use it here.

## One deck per session

- The deck file lives at **`<scratchpad>/deck/deck.html`**, where `<scratchpad>` is the session scratchpad directory from the system prompt (full absolute path). Always publish with this same `file_path`, so the URL never changes and an open deck updates in place.
- Exception — a **chapter deck** (see "Studying a whole chapter") lives in the course folder instead, because it is reused across sessions.

## Deck or terminal?

The deck is for content that needs typesetting, not for every message. Decide by what the answer needs, not by how big the question is.

- **Deck**: a new problem or topic (「下一題」「接著寫」), multi-line derivations, anything that needs a drawing, or a crop of the problem / manual to compare against.
- **Terminal**: follow-ups that clarify wording or concepts, one- or two-line "why" questions, answers with at most a couple of simple formulas. The terminal does not render LaTeX for this user, so write those formulas as plain text or in a code block (`V_S = A·V_R + B·I_R`).
- **Explicit request wins**: 「寫到投影片」「加到頁面」「放到 artifact」 → deck, even if short.
- After a terminal answer, do **not** ask whether to add it to the deck; the user will say so.
- Keep terminal answers short: answer what was asked, don't volunteer extra material.

## Workflow

### 1. Create, append, or overwrite

- **File does not exist** → create the deck.
- **File exists** → **append** slides by default. **Overwrite** only when the user says so (「覆蓋」「重寫」「清掉重來」「換新的」).
- **Correcting earlier slides** ("上一題算錯了") → fix those slides in place with `edits`; don't append a duplicate.

### 2. Create the deck

1. Load the `artifact-design` skill before the first publish (the Artifact tool requires it). The template already meets its page contract (title, two-theme tokens, phone width, CDN allowlist) — don't redesign, just use it.
2. Copy the template and fill the placeholders with `sed` (works in Git Bash; `python` is often missing from its PATH):
   ```bash
   mkdir -p "<scratchpad>/deck" && sed -e 's/__TITLE__/<title>/g' -e 's/__SUBTITLE__/<subtitle>/' "$HOME/.claude/skills/arti-math/assets/template.html" > "<scratchpad>/deck/deck.html"
   ```
   - `__TITLE__` (twice: `<title>` and the cover): 2–4 words from course + topic, e.g. 「電力系統 Ch3」. Never change it later.
   - `__SUBTITLE__`: course and date, e.g. 「NTUST 115-1 · 2026-11-27」.
3. Publish with `Artifact`: `file_path`, `icon: "slides"`, a one-sentence `description`, and the first slides inserted via `edits` (as in step 3).

### 3. Append slides (the common case)

One `Artifact` publish with `file_path` and `edits` — no Read, no separate Edit:

```
edits: [{ "old_str": "<!-- NEXT -->", "new_str": "<section class=\"slide\" data-start>…</section>\n<section class=\"slide\">…</section>\n<!-- NEXT -->" }]
```

- `<!-- NEXT -->` occurs exactly once, so slides stack at the end.
- Put **`data-start` on the first slide of each answer.** On open (no `#pN` in the URL) the deck jumps to the last `data-start`, i.e. the start of the newest answer. Older `data-start`s are harmless; leave them.
- Page count, page menu and the overflow check are done by page JS — nothing else to maintain. Omit `icon` after the first publish.

### 4. Overwrite

Rewrite the file with Write: the template (same title) plus just the new slides. Publish with the same `file_path`, no `icon`.

### 5. Terminal reply

2–4 lines: the conclusion or final number (plain text), then the link and which pages to look at (「第 5–7 頁」). Don't repeat the derivation in the terminal.

## Turning an answer into slides

The stage is fixed at 1280×720 with 56/80 px padding, so space is the main constraint. One slide = one idea.

- **Concept slide** (`.slide`): eyebrow (section number + topic), an `<h2>` that states the point as a sentence (「短線：A=1、B=Z」, not 「短線模型」), then one key formula and 2–4 cards or a short table. A `.note` line at the bottom defines symbols.
- **Example slide** (`.slide.ex`): eyebrow 「例題 · 作業 x.y(z)」, `<h2>` stating the method, then `.exgrid` with the problem in `.prob` (left) and the work in `.sol` (right), ending with `.answer`.
- **Cover / section divider** (`.slide.inv`): dark background; use sparingly to separate big sections.
- **Budget per slide**: about 6 lines of `aligned` in `.sol`, 4 cards in a row, 5 table rows, 3 lines of prose. More than that → split across slides (「…（續）」), don't cram.
- A homework problem with several parts usually becomes one example slide per part or per pair of short parts.
- Each answer that introduces a concept should be followed by an example slide that works a basic part of a real homework problem, so symbols like z, y, γ, ABCD are tied to numbers.

If a slide still overflows, the page shrinks its content down to 70%, and past that shows a red 「內容超出此頁」 badge. Treat the badge as a bug: split the slide.

### Optional visual check

When the deck has new diagrams or dense slides and Chrome exists, screenshot the pages before replying:
```bash
timeout 60 "/c/Program Files/Google/Chrome/Application/chrome.exe" --headless=new --disable-gpu --user-data-dir="<scratchpad>/chrome" --window-size=1400,820 --virtual-time-budget=15000 --screenshot="<scratchpad>/deck/shot.png" "file:///<scratchpad>/deck/deck.html#p5"
```
Read the PNG; check for the overflow badge, overlapping SVG labels and broken line breaks in `aligned`.

## Studying a whole chapter

When the user wants to learn a chapter (「帶我讀第 5 章」「把第 N 章做成投影片」):

- Save the source as **`<course folder>/Ch{N} 投影片.html`** (not the scratchpad) and publish from that path; record the artifact URL in the course's project memory. In a later session, republish that same file with `url` set to the recorded link so the deck updates instead of getting a new link.
- Structure: cover → for each section, concept slide(s) then an example slide → a closing 「做作業前」 slide with the solving steps and the homework problem numbers.
- Example numbers come from the verified solution in the course folder (e.g. `Chapter5 Sol.pdf`) and are re-checked in Python before they go on a slide.
- When the user stops partway, note in the course memory which page they reached.

## Slide HTML

```html
<section class="slide" data-start>
  <p class="ask">One-line paraphrase of the user's question (first slide of an answer only)</p>
  <p class="eyebrow">5.1 雙埠模型</p>
  <h2>任何線路都能寫成 ABCD</h2>
  <div class="math big">$$\begin{bmatrix}V_S\\ I_S\end{bmatrix}=\begin{bmatrix}A&B\\ C&D\end{bmatrix}\begin{bmatrix}V_R\\ I_R\end{bmatrix}$$</div>
  <div class="row4">
    <div class="card"><h3>$A$</h3><p>開路電壓比，無單位</p></div>
    …
  </div>
  <p class="note">S：送電端，R：受電端。</p>
</section>

<section class="slide ex">
  <p class="eyebrow">例題 · 作業 5.1（短線）</p>
  <h2>短線：$A=1$、$B=Z$</h2>
  <div class="exgrid">
    <div class="prob">30 km、34.5 kV 三相線路，受電端在 <b>33 kV</b> 吸收 <b>10 MVA</b>…</div>
    <div class="sol">
      $$\begin{aligned} Z&=zl=11.68\angle 60.8^\circ\ \Omega\\ V_S&=AV_R+BI_R=20.76\angle 3.24^\circ\ \text{kV} \end{aligned}$$
      <div class="answer">$|V_S|_{LL}=35.96\ \text{kV}$</div>
    </div>
  </div>
</section>
```

| class | purpose |
|---|---|
| `.slide` / `.slide.ex` / `.slide.inv` | concept / example (orange eyebrow) / dark cover or divider |
| `data-start` | first slide of an answer; deck opens there |
| `data-title="…"` | optional page-menu label when the `<h2>` is unsuitable |
| `.ask` | small 「問 ·」 line with the user's question |
| `.eyebrow`, `h1`, `h2`, `h3`, `.lead`, `.note` | section label, cover title, slide title, sub-heading, cover subtitle, small footnote |
| `.math`, `.math.big` | display math, 36 / 48 px |
| `.row`, `.grid2`, `.row4`, `.card` | flexible row, 2×2 grid, 4 columns, tinted box |
| `.exgrid` > `.prob` + `.sol` | example layout: problem left, work right |
| `ol.steps`, `table` | ordered steps, table |
| `.tip` / `.warn` | hint / common mistake |
| `.answer` | final answer, yellow highlight |
| `figure.diagram`, `figure.source` | SVG figure, cropped course-file image |

## Working from course files

When the user studies from a file (textbook, solution manual, their own solution PDF — 「帶我看 Ch3 sol 的 3.4」), the deck must be self-contained: put the problem text on the slide.

- **Prefer retyping** the problem into `.prob` (numbers in `<b>`, math in `$…$`) and redrawing its figure as SVG. It stays sharp, themes correctly and fits the slide.
- **Crop only when retyping is impractical** (scans, handwriting, dense figures):
  1. Locate: `py "$HOME/.claude/skills/arti-math/scripts/pdfcrop.py" find "<pdf>" "Problem 3.4"` (`py` on Windows, `python3` elsewhere; needs `pymupdf`). Substring match — confirm by looking.
  2. Look: `render <pdf> <page> <out.png>`, view it, pick the box as page fractions `x0,y0,x1,y1`.
  3. Crop: `crop "<pdf>" <page> "<scratchpad>/deck/img/p3-4" --box …` → `p3-4.png` + `p3-4_dark.png`, pre-tinted to the deck's paper/ink (`--color` keeps colors when they carry meaning). Check the PNG once.
  4. Upload, then append — `edits` can't be combined with `files`, so two publishes of the same `file_path`: first with `files: {"img/p3-4.png": "…", "img/p3-4_dark.png": "…"}`, then the `edits` publish. Uploaded files persist.
  5. Place it inside `.prob` and cite the source:
     ```html
     <figure class="source">
       <img class="src-light" src="img/p3-4.png" alt="Problem 3.4 題目">
       <img class="src-dark" src="img/p3-4_dark.png" alt="">
       <figcaption>Chapter3 Sol.pdf · PDF p.4</figcaption>
     </figure>
     ```

## Math

- MathJax (SVG output). Inline `$…$` or `\(…\)`; display `$$…$$`. Display math is left-aligned on slides.
- Multi-line: `\begin{aligned} … \\ … \end{aligned}` — the line break must really be two backslashes. Writing through `edits` JSON or the Write tool is safe; **never** write the file with a Bash heredoc, which eats backslashes.
- A literal dollar sign in prose is `\$`.

## Diagrams

- Draw when a picture helps (circuits, phasor diagrams, block diagrams, waveforms). For anything non-trivial, consult the `artifact-diagramming` skill first.
- Size for the stage: `viewBox` width ≤ 1120 (full slide width) or ≤ 640 (beside text); text `font-size` 22–26, subscripts 16–18.
- Both themes: lines and text use `currentColor`; emphasis with `stroke="var(--accent)"` / `class="accent"`, tinted fills with `fill="var(--soft)"`; no hard-coded `#000` / `white`; every closed shape gets an explicit `fill`.
- Arrowheads: a `<marker>` whose path uses `fill="currentColor"`. Marker ids must be unique across the whole deck (prefix with the slide id).
- MathJax does not touch SVG text — use `<tspan baseline-shift="sub" font-size="18">` for subscripts and Unicode for symbols (θ, ∠, Ω, °).
- Leave room for outer labels; labels must not overlap.

## Content

- Traditional Chinese with Taiwanese terminology; English term in parentheses on first use.
- Intuition first, then the derivation; show substituted numbers, not just formulas.
- If the course folder's CLAUDE.md or project memory has rules (notation, following the solution manual, Python verification, units with k/M prefixes), the content follows them; this skill only decides the **presentation**.
