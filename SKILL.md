---
name: arti-math
description: Write the current answer onto a per-session artifact notebook page — math typeset with MathJax, diagrams drawn as inline SVG — and leave only a short summary plus the link in the terminal. Use ONLY when the user explicitly asks for it, e.g. types /arti-math, or says 「開 artifact 講」「用 artifact 回答」「寫到筆記頁」「這題畫在頁面上」「放到 artifact」, or, once a notebook page exists in this session, says 「接著寫」「下一題」「加到筆記」「覆蓋筆記」「重寫筆記」. Once the page exists, short follow-up questions (wording, concept checks, one-line "why") are answered in the terminal, not on the page — see "Page or terminal?". Do not use it on your own initiative when the user has not mentioned an artifact or the notebook page.
---

# arti-math — notebook page for math and diagrams

The user studies engineering courses inside Claude Code. Raw LaTeX and ASCII diagrams in the terminal are hard to read, so this skill moves the answer onto a web page where formulas are actually typeset and circuits, phasor diagrams, etc. are drawn. The terminal keeps only a few lines and the link.

## One page per session

- The page file always lives at **`<scratchpad>/note/note.html`**, where `<scratchpad>` is the session scratchpad directory from the system prompt (use its full absolute path). The scratchpad is unique per session, so "one page per session" falls out naturally.
- Always publish with the **same `file_path`**, so the URL never changes and an open page updates in place.

## Page or terminal?

The page is for content that needs typesetting, not for every message. Decide by what the answer needs, not by how big the question is.

- **Write to the page**: a new problem or topic (「下一題」「接著寫」), multi-line derivations (`aligned`), anything that needs a drawing (circuit, phasor diagram, waveform), or a crop of the problem / manual to compare against.
- **Answer in the terminal**: follow-ups that clarify wording or concepts (「題目哪句在講什麼」「這個詞什麼意思」), one- or two-line "why" questions, and answers with at most a couple of simple formulas that read fine as Unicode / `$…$` in the terminal.
- **Explicit request wins**: if the user says 「寫到筆記」「加到頁面」「放到 artifact」, write it to the page even if it is short.
- After a terminal answer, do **not** ask whether to add it to the page; the user will say so.
- An entry is one problem or one topic, not one chat message. When a follow-up the user wants on the page belongs to an existing entry, extend that entry (add a sub-heading inside its `<section>`) rather than appending a new one — the page should read like notes, not a chat log.

## Workflow

### 1. Decide: create, append, or overwrite

- **File does not exist** → create the page.
- **File exists** → **append** one entry by default. **Overwrite** only when the user says so (「覆蓋」「重寫」「清掉重來」「換新的」).
- If the user is **correcting the previous entry** ("上一題算錯了"), fix that entry in place instead of appending a duplicate.

### 2. Create the page

1. The Artifact tool requires loading the `artifact-design` skill before writing a page; do that on this first creation. The bundled template already satisfies its page contract (title, two-theme tokens, phone width, CDN allowlist), so don't redesign — just use the template.
2. Copy the template and fill the two placeholders in one Bash command. Use `sed`, which works in Git Bash, macOS and Linux alike (`python` is often missing from Git Bash's PATH on Windows):
   ```bash
   mkdir -p "<scratchpad>/note" && sed -e 's/__TITLE__/<title>/g' -e 's/__SUBTITLE__/<subtitle>/' "$HOME/.claude/skills/arti-math/assets/template.html" > "<scratchpad>/note/note.html"
   ```
   - `__TITLE__` (appears twice): a 2–4 word name from course + topic, e.g. 「電力系統 Ch3 筆記」. Never change it on later appends.
   - `__SUBTITLE__`: course/folder and date, e.g. 「NTUST 115-1 · 2026-10-17」.
3. Publish with `Artifact`: `file_path`, `icon: "notebook"`, a one-sentence `description`, and the first entry inserted via `edits` (same as step 3 below).

### 3. Append an entry (the common case)

One `Artifact` publish call with `file_path` and `edits` — no Read, no separate Edit:

```
edits: [{ "old_str": "<!-- NEXT -->", "new_str": "<section class=\"entry\">…</section>\n<!-- NEXT -->" }]
```

`<!-- NEXT -->` occurs exactly once in the file, so new entries stack at the bottom. The table of contents is built by page JS from each entry's `<h2>`, and on load the page scrolls to the newest entry — nothing else to maintain. Omit `icon` on every publish after the first.

### 4. Overwrite

Rewrite `note.html` with Write: the template content (keeping the existing title) plus just the new entry. Publish with the same `file_path`, without `icon`.

### 5. Terminal reply

2–4 lines only: the conclusion or final numeric answer, then a pointer that the full derivation and figures are on the page, with the link. Do **not** repeat the derivation in the terminal — the whole point is to read it on the page.

## Working from course files

Often the user is studying from a file — a textbook PDF, a solution manual, their own solution PDF ("帶我看 Ch3 sol 的 3.4"). They will not flip between the PDF and the page, so **the page must be self-contained**: put the relevant part of the file (the problem statement, the figure, the manual step being discussed) on the page as an image right above the explanation.

1. **Find it.** Read the file with the Read tool (PDF `pages`), and/or locate text with the bundled script:
   ```
   py "$HOME/.claude/skills/arti-math/scripts/pdfcrop.py" find "<pdf>" "Problem 3.4"
   ```
   (`py` on Windows, `python3` elsewhere; needs `pip install pymupdf`.) `find` is a substring match — "3.4" also hits 3.40–3.49 — so confirm the page by looking at it.
2. **Look before cropping.** `render <pdf> <page> <out.png>` writes a low-dpi page image; view it with Read and pick the box as page fractions `x0,y0,x1,y1` (origin top-left). `find` prints boxes in the same units, which helps place the top edge.
3. **Crop.** Save into `<scratchpad>/note/img/`:
   ```
   py "$HOME/.claude/skills/arti-math/scripts/pdfcrop.py" crop "<pdf>" <page> "<scratchpad>/note/img/p3-4" --box 0.05,0.06,0.95,0.42
   ```
   This writes `p3-4.png` and `p3-4_dark.png`, already tinted to the page's paper/ink colors for each theme (no CSS filters, which blur). Add `--color` when the color itself carries meaning (colored plots); then the light image keeps its colors and the dark one is inverted. Read the cropped PNG once to check nothing is cut off; a problem that spans two pages gets two crops shown one after another.
4. **Upload, then append.** `edits` cannot be combined with `files`, so it takes two publishes of the same `file_path`:
   - first `Artifact` publish with `files: {"img/p3-4.png": "<scratchpad>/note/img/p3-4.png", "img/p3-4_dark.png": "<scratchpad>/note/img/p3-4_dark.png"}` (page unchanged),
   - then the usual `edits` publish that appends the entry referencing them.
   Uploaded files persist across later publishes, so each image is uploaded once.
5. In the entry, cite the source in the caption (file name + PDF page; printed page too when it differs) so the user can find it again:
   ```html
   <figure class="source">
     <img class="src-light" src="img/p3-4.png" alt="Problem 3.4 題目">
     <img class="src-dark" src="img/p3-4_dark.png" alt="">
     <figcaption>Chapter3 Sol.pdf · PDF p.4</figcaption>
   </figure>
   ```
6. **Fixed problem → two columns.** When the entry is built around a fixed source (a problem statement, a manual excerpt), make `<div class="prob">…</div>` the entry's first child and put the `.ask`, the `<h2>`, the `figure.source` and the short 題意 paragraph inside it, so the question line and title stay pinned with the problem. On wide screens the template then shows that block pinned in the left column while the explanation scrolls on the right; narrow screens stay single-column. Entries without a fixed source (concept questions, plain explanations) don't get a `.prob` and stay single-column — don't wrap other content in `.prob` just to get the layout.

Crop only what the entry discusses. The images are context; the explanation, derivation and redrawn diagrams are still written out on the page as usual — don't paste a whole solution page in place of explaining it.

## Entry HTML

```html
<section class="entry">
  <p class="ask">One-line paraphrase of the user's question</p>
  <h2>Entry title (shown in the TOC)</h2>

  <p>Prose with inline math such as $Z_{base} = \dfrac{V_{base}^2}{S_{base}}$.</p>

  <div class="math">$$ I = \frac{S^*}{\sqrt{3}\,V^*} $$</div>

  <ol class="steps"><li>Step one…</li><li>Step two…</li></ol>

  <figure class="diagram">
    <svg viewBox="0 0 400 160" width="400" role="img" aria-label="…">…</svg>
    <figcaption>圖：…</figcaption>
  </figure>

  <div class="tbl"><table>…</table></div>

  <div class="tip">Intuition or a small reminder</div>
  <div class="warn">Common mistake</div>
  <div class="answer">$I = 2.31\angle{-36.9^\circ}\ \text{kA}$</div>
</section>
```

| class | purpose |
|---|---|
| `.ask` | small caption with the user's question |
| `.math` | wraps display math; scrolls sideways if too wide |
| `ol.steps` | ordered derivation steps |
| `figure.diagram` | SVG figure |
| `figure.source` | cropped image from a course file (light + dark `<img>`), see above |
| `.prob` | first child of an entry with a fixed problem; holds `.ask`, `<h2>`, source crop and 題意; pinned left column on wide screens |
| `.tbl` | wraps a table; scrolls sideways if too wide |
| `.tip` / `.warn` | hint / common mistake |
| `.answer` | final answer, yellow highlight |

Pick the pieces the content needs; not every entry uses all of them.

## Math

- MathJax (SVG output). Inline: `$…$` or `\(…\)`. Display: `$$…$$`.
- Multi-line derivations: `\begin{aligned} … \\ … \end{aligned}`. The line break must really be two backslashes. Writing through `edits` JSON or the Write tool is safe; **never** write the file with a Bash heredoc, which eats backslashes.
- A literal dollar sign in prose is `\$`.

## Diagrams

- Draw only when a picture helps understanding (circuits, phasor diagrams, block diagrams, waveforms, plots, geometry). For anything non-trivial, consult the `artifact-diagramming` skill first.
- Inline SVG that reads in both themes:
  - Lines and text use `currentColor` (`svg text` already defaults to it).
  - Emphasis: `class="accent"` for strokes, `class="fill-accent"` for fills.
  - No hard-coded `#000`, `white`, etc. that only work in one theme.
  - Give every closed shape an explicit `fill` (usually `fill="none"`).
  - Leave room in the viewBox for outer labels; labels must not overlap.
  - Arrowheads: a `<marker>` whose path uses `fill="currentColor"` (or `class="fill-accent"` for an accent arrow). Give each marker a unique id across the whole page (e.g. prefix with the entry number), since all entries share one document.
- MathJax does not touch text inside SVG — use plain text with `<tspan baseline-shift="sub" font-size="10">` for subscripts and Unicode for Greek letters and symbols (θ, ∠, Ω, °).
- Flowcharts / state diagrams may use `<pre class="mermaid">…</pre>`; the platform renders it natively, no library needed.

## Content

- Write the page content in Traditional Chinese with Taiwanese terminology; add the English term in parentheses on first use of a technical term.
- Explain intuition first, then the derivation. Show the substituted numbers in every calculation, not just the formula.
- If the working folder's CLAUDE.md has course-specific rules (notation, following the solution manual, verifying numbers in Python), the content follows those rules; this skill only decides the **presentation**.
