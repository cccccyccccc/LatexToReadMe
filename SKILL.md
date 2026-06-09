---
name: readme-generator
description: >
  Generate a professional GitHub README.md by synthesizing LaTeX paper sources
  with a codebase. Use this skill whenever the user wants to create, generate,
  or improve a README for a research project, academic code repository, or
  paper-implementation combo. Also trigger when the user mentions "paper + code
  → README", "generate README from LaTeX", "make my repo look professional",
  or any request involving both .tex files and a codebase. The skill parses
  LaTeX for academic context and analyzes the codebase for technical details,
  then fuses them into a well-structured README.
---

# README Generator — LaTeX + Codebase → GitHub README

## Core principle

A great research-code README is **developer-first, paper-second**: what is
this, how do I run it, how do I cite it — in that order. Target **150–300
lines**. A README is a signpost, not the paper.

## Workflow

### 1. Scan and confirm

Quick-scan for `.tex` files (pick the main one), `.bib` files, dependency
files, entry-point scripts, `LICENSE`, and config files. Tell the user what
you found. Skip this if they already specified a file.

### 2. Extract from LaTeX

Read the main `.tex` file. Follow `\input`/`\include` references.

| Extract | Source | README placement |
|---------|--------|------------------|
| Title | `\title{...}` — strip braces, join `\\` with space | `#` heading |
| Authors | `\author{...}` — split on `\and`, strip `\thanks{...}` | Overview paragraph |
| Abstract | `\begin{abstract}` — strip all LaTeX commands | Overview section |
| Methodology | `\section{Method...}` / `\section{Approach...}` | Methodology section |
| Results | `\section{Experiments}` / `\section{Results}` | Results section |
| Key equations | Numbered `\begin{equation}` with `\label` — top 1–3 | `$$` block (see below) |
| Tables | `\begin{table}...\begin{tabular}` with numbers | Markdown table |
| Citation key | Paper's own `\cite` key | Resolve from `.bib` |

**LaTeX → Markdown:**
- `\textbf{...}` / `\textit{...}` / `\emph{...}` → `**text**` or `*text*`
- `\cite{key}` → replace with plain-text reference; `\ref{label}` → drop it
- `\url{...}` → bare URL; `\href{url}{text}` → `[text](url)`
- `\%` `\$` `\&` `\#` `\_` → `%` `$` `&` `#` `_`
- `---` → `—`, `--` → `–`
- Strip `\label{...}`, strip comments unless they contain arXiv ID

**Equations — three rules:**
1. `$$` on its own line, equation on the next line, closing `$$` on its own
   line. Never single-line `$$...$$`, never inline `$...$`. This is required
   by Typora and ensures GitHub compatibility.
2. No spacing tweaks: skip `\!`, `\,`, `\;`, `\quad`, `\qquad`.
3. Follow every equation block with a one-sentence plain-language explanation.

```
$$
\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right) V
$$

In plain terms: a weighted sum of values, where each weight is the scaled
dot-product similarity between a query and a key.
```

### 3. Analyze the codebase

Read the minimum needed to write accurate instructions:
- **Dependency file** → exact install command
- **One entry-point script** → CLI args for Quick Start
- **One config file** → representative example for the README
- **LICENSE** → exact license name for badge and License section

### 4. Resolve the citation

Find the paper's own entry in the `.bib` file and copy it **exactly**.
Do not reconstruct from LaTeX metadata. If no `.bib` file exists, create
a BibTeX entry from the paper metadata but flag it for user review.

### 5. Assemble the README

```
# [Title from LaTeX]

[Badges — only verified ones. See badge rules.]

## Overview
[120–200 words. (1) What the model DOES, not "this repo contains". (2) Why it
matters — the key insight, what it replaced. (3) Key numbers with context. (4)
Authors and venue woven naturally into the text. Avoid "we propose a novel".]

## Installation
[Exact commands from the actual dependency file. No virtual env, no Docker
unless the project has a specific script for it.]

## Quick Start
[One training command, one eval command. Show --help hint.]

## Methodology
[2–4 paragraphs. Include 1–3 key equations using `$$` blocks. Cross-reference
paper figures/sections.]

## Results
[Summary table from the paper. Show delta vs baselines prominently. Include
the command to reproduce these numbers.]

## Project Structure
[ASCII tree, max depth 2. One-line comments. Skip empty dirs and dotfiles.]

## Citation
[Exact BibTeX entry from .bib file.]

## License
[One line: "Licensed under [Name]. See [LICENSE](LICENSE)."]
```

## Badge rules

Only include badges **verified from an actual file**:

| Badge | Verify from |
|-------|-------------|
| Language version | `python_requires` in setup.py/pyproject.toml, `engines` in package.json |
| License | Actual LICENSE file contents |
| arXiv | arXiv ID in LaTeX `\href`, comments, or `.bib` entry |
| Framework | Import in code (e.g. `import torch` → PyTorch badge) |
| Venue | Conference/journal name in LaTeX or `.bib` |

Never guess. Three verified badges beat five where two are guesses.

## Anti-patterns

Check your output against this list before writing:

1. **Invented content.** No venv, no Docker, no "code style: black" badge
   unless you find the exact config file that proves it.
2. **Redundancy.** No dependency table if `requirements.txt` is shown. No
   separate "Reproducibility" section duplicating training commands.
3. **Bad equation formatting.** See equation rules above — `$$` on separate
   lines, no spacing tweaks, always followed by plain-language explanation.
4. **HTML wrappers.** No `<div>`, `<p>`, `<br>`, `<center>`, `<img>`. Pure
   markdown.
5. **Paper sections.** Skip Related Work, Discussion, Future Work,
   Acknowledgments — the README is for the repository.
6. **Bloat.** Over 400 lines → cut. The paper has the details.
7. **Hallucinated IDs.** If arXiv ID isn't findable, use `XXXX.XXXXX` and
   tell the user. Honest placeholder beats made-up ID.
8. **Separate "Paper" section.** The Overview already covers this.
9. **Hard line breaks in prose.** Don't wrap paragraphs at a fixed column
   width like 80 chars. Let prose flow naturally — each paragraph is one
   long line in the source. Only break lines intentionally: headings,
   code blocks, equations, table rows, list items.

## Customization triggers

| Signal | Behavior |
|--------|----------|
| `Chinese` / `中文` | Translate to natural technical Chinese (meaning, not word-for-word). Code blocks, commands, BibTeX stay in English. |
| `short` / `minimal` | Title, overview, install, quick start, citation only. Skip methodology, results, project structure. |
| `focus on <dir>` | Only scan that directory |
| `use <file>.tex` | Use that file |
| `add <section>` | Include extra section |
| `skip <section>` | Omit that section |
| `badges: <list>` | Include exactly those (no verification needed) |
| `output: <path>` | Write to non-default path |

## Output

Write `README.md` to the project root. If one exists, ask before overwriting
— offer `README_GENERATED.md` as a preview. Report: file path, line count,
sections included and skipped.
