---
name: arti-math
description: Write the current answer onto a per-session artifact notebook page — math typeset with MathJax, diagrams drawn as inline SVG — and leave only a short summary plus the link in the terminal. Use ONLY when the user explicitly asks for it, e.g. types /arti-math, or says 「開 artifact 講」「用 artifact 回答」「寫到筆記頁」「這題畫在頁面上」「放到 artifact」, or, once a notebook page exists in this session, says 「接著寫」「加到筆記」「覆蓋筆記」「重寫筆記」. Do not use it on your own initiative when the user has not mentioned an artifact or the notebook page.
---

# arti-math — notebook page for math and diagrams

The user studies engineering courses inside Claude Code. Raw LaTeX and ASCII diagrams in the terminal are hard to read, so this skill moves the answer onto a web page where formulas are actually typeset and circuits, phasor diagrams, etc. are drawn. The terminal keeps only a few lines and the link.

## One page per session

- The page file always lives at **`<scratchpad>/note/note.html`**, where `<scratchpad>` is the session scratchpad directory from the system prompt (use its full absolute path). The scratchpad is unique per session, so "one page per session" falls out naturally.
- Always publish with the **same `file_path`**, so the URL never changes and an open page updates in place.

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
