# Evidence Synthesis Skill for Codex `/goal`

A rigorous, transparent evidence-synthesis methodology for autonomous literature reviews under [Codex](https://github.com/openai/codex) `/goal` mode. Designed for policy-relevant questions following Royal Society / Academy of Medical Sciences principles.

---

## What This Is

This repository provides the **contract, methodology reference, and executable stopping condition** for conducting defensible evidence syntheses with an AI agent. It replaces "the model thinks it looks good" with **verifiable artifacts that must pass a script before the run is declared complete**.

Use it for:
- Systematic reviews
- Rapid reviews  
- Meta-analyses (when effects are combinable)
- Scoping reviews
- Evidence reviews for policy or decision-making

---

## The 3 Files

| File | Purpose | When to Read |
|------|---------|-------------|
| `SKILL.md` | **The contract.** Pipeline checkpoints, artifact requirements, human gates, and the goal statement that drives the run. | Read **first** — this defines what "done" means. |
| `references/methodology.md` | **The how.** Deep guidance on synthesis type selection, search strategy, risk-of-bias tools, GRADE certainty rating, and reporting standards. | Read when a checkpoint reaches a methodological decision the contract keeps terse. |
| `scripts/verify_synthesis.py` | **The stopping condition.** Executable script that checks every artifact for existence, reconciliation, citation integrity, and human sign-off. | Run after **every checkpoint** and for the **final pass**. Exit 0 = done. |

---

## Quick Start

### 1. Drop these files into your project

Create a `synthesis/` working directory and place the skill files alongside it:

```
your-project/
├── SKILL.md                    ← this skill's contract
├── references/
│   └── methodology.md          ← methodological reference
├── scripts/
│   └── verify_synthesis.py     ← verification script
└── synthesis/                  ← working directory (created during run)
    ├── protocol.md
    ├── search_log.jsonl
    ├── corpus/
    │   └── records.jsonl
    ├── dedup_report.json
    ├── screening.csv
    ├── appraisal.csv
    ├── extraction.csv
    ├── manuscript.md
    ├── prisma.json
    ├── citation_audit.jsonl
    ├── signoff.json
    └── progress.md
```

### 2. Set the goal in Codex

```
/goal Produce an evidence synthesis answering the question in
synthesis/protocol.md, working in checkpoints and keeping
synthesis/progress.md updated. Do not stop until
`python scripts/verify_synthesis.py --final synthesis/` exits 0,
which requires every artifact below to exist, reconcile, and pass its
checks, AND the human-gated checkpoints (appraisal, final review) to be
signed off. Pause with /goal pause at each human gate.
```

### 3. Work in checkpoints

| Checkpoint | Artifact Produced | Verification Command |
|-----------|-------------------|---------------------|
| 1 — Protocol | `synthesis/protocol.md` | `python scripts/verify_synthesis.py --stage 1 synthesis/` |
| 2 — Search | `synthesis/search_log.jsonl` + per-source records | `--stage 2` |
| 3 — Corpus | `synthesis/corpus/records.jsonl` + `dedup_report.json` | `--stage 3` |
| 4 — Screen | `synthesis/screening.csv` | `--stage 4` |
| 5 — Appraisal | `synthesis/appraisal.csv` | `--stage 5` |
| 6 — Extract | `synthesis/extraction.csv` | `--stage 6` |
| 7 — Synthesise | `synthesis/manuscript.md` | `--stage 7` |
| 8 — PRISMA | `synthesis/prisma.json` | `--stage 8` |
| 9 — Citation audit | `synthesis/citation_audit.jsonl` | `--stage 9` |
| 10 — Final review | `synthesis/signoff.json` | `--stage 10` or `--final` |

### 4. Use `--final` to declare done

```bash
python scripts/verify_synthesis.py --final synthesis/
```

**Exit 0** → goal met. All artifacts exist, reconcile, citations resolve, and human gates are signed off.  
**Exit 1** → keep working on the reported failures.  
**Exit 2** → structural error (e.g., missing `synthesis/` directory).

---

## The 10 Checkpoints Explained

### Checkpoint 1 — Protocol
Write `synthesis/protocol.md` **before** searching. It must declare:
- Decision question (one sentence, answerable)
- Audience (the specific decision-maker)
- Stance (`policy-neutral` or `makes-a-case`)
- PICO/PECO framing
- Inclusion/exclusion criteria
- Sources and search strategy
- Synthesis method
- Page budget (default: 6–10 pages)

### Checkpoint 2 — Search
Execute each planned search verbatim. Log:
- Source (database, registry, grey-lit)
- Exact query string
- Date run
- Raw hit count
- Path to returned records file

### Checkpoint 3 — Deduplicate & Assemble
Merge all records, remove duplicates. Produce:
- `corpus/records.jsonl` — one line per unique record with `id`, `title`, `authors`, `year`, `locator` (DOI or URL), `source`
- `dedup_report.json` — `{raw_total, duplicates_removed, deduped_total}` must arithmetically reconcile

### Checkpoint 4 — Screen
Screen every deduplicated record at title/abstract then full text. `screening.csv` columns:
- `record_id`, `ta_decision`, `ft_decision`, `exclusion_reason`

Every corpus record appears exactly once. Every excluded record has a reason from the protocol.

### Checkpoint 5 — Critical Appraisal (**HUMAN GATE**)
Appraise each included study with a design-matched tool (RoB 2, ROBINS-I, QUADAS-2, AMSTAR 2, etc.). See `references/methodology.md` §5 for the full selection table.

`/goal pause` here. Request human review. Do **not** set `human_reviewed` yourself.

### Checkpoint 6 — Extract
Extract data from each included study only. No imputation, no silent back-calculation.

### Checkpoint 7 — Synthesise
Combine extracted evidence. Pool only if effects are conceptually combinable; otherwise use structured synthesis (SWiM). Rate certainty with GRADE. Write `manuscript.md` with:
- Stance declaration
- Plain-language summary
- Background & question
- Methods
- Evidence base (PRISMA flow)
- Findings (every claim cited as `[@record_id]`)
- Limitations & certainty
- Implications for decision-maker
- References

### Checkpoint 8 — Reconcile & PRISMA
Produce `prisma.json` with counts at every stage. Must reconcile exactly against search log, corpus, and screening.

### Checkpoint 9 — Citation Audit
Verify every `[@record_id]` in the manuscript resolves to a real corpus record with a well-formed locator. No fabricated citations.

### Checkpoint 10 — Final Review (**HUMAN GATE**)
`/goal pause`. Human reads for:
1. Does any conclusion exceed the appraised evidence?
2. Does the stance match the declared stance?

Produce `signoff.json`: `{appraisal_signed_off: true, final_review_signed_off: true, reviewer, date}`.

---

## Verification Script Options

```bash
# Check a single checkpoint
python scripts/verify_synthesis.py --stage 3 synthesis/

# Run all checks (stopping at the first failure)
python scripts/verify_synthesis.py --final synthesis/

# Also attempt to resolve URLs (warns on failure; requires network)
python scripts/verify_synthesis.py --final --check-urls synthesis/

# Treat URL failures as hard failures
python scripts/verify_synthesis.py --final --check-urls --strict-urls synthesis/

# Show help
python scripts/verify_synthesis.py --help
```

---

## Non-Negotiable Rules

1. **No fabricated evidence.** Every citation must resolve to a real record in `corpus/records.jsonl`.
2. **No new research.** Don't generate, simulate, or extrapolate findings.
3. **Stance discipline.** Default to `policy-neutral`. Don't let conclusions exceed what the evidence supports.
4. **Human gates at checkpoints 5 and 10.** Critical appraisal and final review require human sign-off.
5. **Transparency over completeness theatre.** A smaller, honestly bounded synthesis with reproducible search beats a broad one you cannot reproduce.

---

## When to Use What Synthesis Type

| Type | Use When |
|------|----------|
| **Structured/narrative evidence review** | Default for policy questions with heterogeneous designs. Effects not statistically combinable. |
| **Systematic review** | Clearly formulated question, exhaustive search, explicit selection. May or may not include meta-analysis. |
| **Meta-analysis** | Included studies estimate a conceptually comparable effect, measured commensurably, with assessable heterogeneity. |
| **Scoping review** | Goal is to map what evidence exists, not answer an effect question. |
| **Rapid review** | Time-critical decisions only. Every shortcut must be recorded and its risk acknowledged. |

See `references/methodology.md` §1 for full decision rules.

---

## License

These files are provided as a public methodology template. Use, modify, and share freely. Attribution to the original Royal Society / Academy of Medical Sciences evidence-synthesis programme is appreciated.
