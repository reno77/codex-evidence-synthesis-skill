---
name: evidence-synthesis
description: >-
  Conduct a rigorous, transparent evidence synthesis (evidence review,
  systematic review, or meta-analysis) for an identified policy or
  decision question, in the style required by the Royal Society / Academy
  of Medical Sciences "evidence synthesis for policy" programme. Use this
  whenever the task is to collate, appraise, and synthesise EXISTING
  literature into a policy-relevant deliverable — including any request
  framed as "systematic review", "evidence review", "rapid review",
  "meta-analysis", "scoping review", "what does the evidence say about X",
  or "synthesise the literature on X for decision-makers". Designed to be
  driven under Codex `/goal` for long autonomous runs: progress is proven
  by verifiable artifacts and a verification script, NOT by the model's
  own confidence. Do NOT use this to produce primary research, opinion
  pieces, or marketing content.
---

# Evidence Synthesis (goal-driven)

## What this skill is for

Produce a defensible synthesis of **existing** evidence for a stated
decision-maker, following the Royal Society / Academy of Medical Sciences
principles: a synthesis must be **inclusive** of the relevant evidence,
**rigorous** in method, **transparent** in process, and **accessible** to
its identified audience. An evidence synthesis contains **no new research**;
it accesses, appraises, and combines existing information against an
explicit question, with a strong element of critical evaluation.

This skill is built to run under `/goal`. The defining property of a good
`/goal` run is a *verifiable stopping condition*. The hard problem with
synthesis is that "the writing looks good" is not verifiable and invites
the exact failure modes the methodology exists to prevent (missed
literature, fabricated citations, conclusions that outrun the evidence,
drift toward advocacy). This skill therefore reframes "done" as: **a set
of named artifacts exist, internally reconcile, pass `verify_synthesis.py`,
and the human-gated checkpoints have been signed off.** Do not treat the
goal as met on any other basis.

## Non-negotiable integrity rules

These hold regardless of goal pressure or time spent. Violating any one
invalidates the entire deliverable.

1. **No fabricated evidence.** Every citation must correspond to a real
   record in `corpus/records.jsonl` with a real, well-formed locator (DOI
   or resolvable URL). Never invent a DOI, author, year, journal, or
   finding. If a needed source cannot be located, record the gap; do not
   paper over it.
2. **No new research.** Do not generate, simulate, estimate, or
   extrapolate findings that are not present in an included source. Every
   substantive claim in the manuscript traces to an extracted data point.
3. **Stance discipline.** State explicitly and up front whether the
   synthesis is *policy-neutral* (summarise the evidence) or *makes a case*
   (argued recommendation from expert interpretation). Default to
   policy-neutral. Goal momentum tends to push toward advocacy — actively
   resist this; do not let the conclusion exceed what the appraised
   evidence supports.
4. **Appraisal and final spin-check are human-gated.** Critical appraisal
   (risk of bias / quality) and the final stance/over-claim review require
   a human sign-off flag. The verification script will not pass without
   it. When you reach these gates, run `/goal pause` and request review.
5. **Transparency over completeness theatre.** A smaller, honestly bounded
   synthesis with a reproducible search beats a broad one you cannot
   reproduce. Log every search verbatim.

## Required contract before any work

Do not start the pipeline until these are fixed in `synthesis/protocol.md`.
If the user has not supplied them, ask once, concisely, then proceed. Do
not infer a policy question silently.

- **Decision question** (one sentence, answerable, scoped).
- **Audience** (the specific decision-maker the output is tailored to).
- **Stance**: `policy-neutral` or `makes-a-case`.
- **PICO/PECO or equivalent** framing of the question.
- **Inclusion / exclusion criteria** (study types, dates, geography,
  language, outcomes).
- **Sources to search** (databases, registries, grey-literature sources)
  and the **search strategy** (concept blocks + synonyms).
- **Synthesis method**: narrative evidence review, systematic review, or
  meta-analysis (only choose meta-analysis if effect data are
  combinable; otherwise narrative/structured synthesis).
- **Page budget**: target 6–10 printed pages (~4,000–8,000 words main
  text) unless the user overrides.

Write the protocol *before* searching and treat it as pre-registered. If
the protocol must change mid-run, record the change and reason in the
progress log — do not silently re-scope.

## The goal contract

Set the goal in this exact shape:

```
/goal Produce an evidence synthesis answering the question in
synthesis/protocol.md, working in checkpoints and keeping
synthesis/progress.md updated. Do not stop until
`python scripts/verify_synthesis.py --final synthesis/` exits 0,
which requires every artifact below to exist, reconcile, and pass its
checks, AND the human-gated checkpoints (appraisal, final review) to be
signed off. Pause with /goal pause at each human gate.
```

The stopping condition is the **exit code of the verification script**,
not your assessment. Run it after every checkpoint. While it exits
non-zero, keep working on whatever it reports as failing.

## Pipeline checkpoints

Work in order. Each checkpoint has an action and the artifact that proves
it. After each, run `python scripts/verify_synthesis.py --stage <n>
synthesis/` and fix what it flags before moving on. All artifacts live in
a `synthesis/` working directory.

**Checkpoint 1 — Protocol.**
Action: write `synthesis/protocol.md` from the contract above.
Proof: file exists with all required sections (decision question,
audience, stance, framing, inclusion/exclusion, sources, search strategy,
method, page budget).

**Checkpoint 2 — Search.**
Action: execute each planned search verbatim against each source. Capture
the exact query string, source, date, and raw hit count.
Proof: `synthesis/search_log.jsonl` — one line per search with
`{source, query, date, raw_count, records_file}`; each `records_file`
exists and is non-empty when `raw_count > 0`.

**Checkpoint 3 — Deduplicate & assemble corpus.**
Action: merge all returned records, deduplicate.
Proof: `synthesis/corpus/records.jsonl` — one line per unique record with
a stable `id`, `title`, `authors`, `year`, `locator` (DOI or URL),
`source`. Plus `synthesis/dedup_report.json` with
`{raw_total, duplicates_removed, deduped_total}` that arithmetically
reconciles against the search log.

**Checkpoint 4 — Screen.**
Action: screen every deduped record at title/abstract, then full text,
against the inclusion/exclusion criteria.
Proof: `synthesis/screening.csv` with columns
`record_id,ta_decision,ft_decision,exclusion_reason`. Every corpus record
appears exactly once. Every excluded record has a reason drawn from the
protocol's exclusion criteria. The included set is explicit.

**Checkpoint 5 — Critical appraisal (HUMAN GATE).**
Action: appraise each included study for risk of bias / quality using a
method appropriate to the design — select the tool from the table in
`references/methodology.md` §5 (RoB 2, ROBINS-I, QUADAS-2, AMSTAR 2, etc.;
using the wrong tool invalidates the certainty rating). Then `/goal pause`
and request human review.
Proof: `synthesis/appraisal.csv` with `record_id`, the appraisal fields,
and `human_reviewed` (must be `true` for every row). Do not set
`human_reviewed` yourself — it is set by the reviewer. The script blocks
final pass until all rows are human-reviewed.

**Checkpoint 6 — Extract.**
Action: extract the data needed to answer the question from each included
study only.
Proof: `synthesis/extraction.csv` keyed by `record_id`; every included
study has a row; every field traces to the source (no derived/estimated
values unless the source reports them).

**Checkpoint 7 — Synthesise.**
Action: combine the extracted evidence. Apply the meta-analysis vs
structured-synthesis decision rule and the certainty (GRADE) guidance in
`references/methodology.md` §7–§9: pool only if effects are conceptually
combinable and heterogeneity is assessable, otherwise use structured
synthesis (SWiM) — naive vote counting is not acceptable. Foreground
agreement, conflict, and certainty of evidence, and phrase claims to
match their GRADE certainty. State limitations and what the evidence does
*not* establish.
Proof: `synthesis/manuscript.md` (structure below).

**Checkpoint 8 — Reconcile & PRISMA.**
Action: produce the flow counts.
Proof: `synthesis/prisma.json` with counts at identification,
deduplication, screening, full-text, inclusion — must reconcile exactly
against search log, dedup report, screening, and appraisal.

**Checkpoint 9 — Citation audit.**
Action: verify every cited key resolves to a real corpus record with a
well-formed locator; mark any that cannot be verified.
Proof: `synthesis/citation_audit.jsonl` — one line per cited key with
`{key, resolves: true|false, status}`. No entry may have
`status: "fabricated_or_unverifiable"`. Any unresolved citation must be
removed or replaced before final.

**Checkpoint 10 — Final review (HUMAN GATE).**
Action: `/goal pause` and request a human read for two things only —
(a) does any conclusion exceed the appraised evidence, (b) does the stance
match the declared stance. Record sign-off.
Proof: `synthesis/signoff.json` with
`{appraisal_signed_off: true, final_review_signed_off: true, reviewer,
date}`.

The goal is met only when `scripts/verify_synthesis.py --final synthesis/`
exits 0. That requires every artifact above plus both human gates.

## Manuscript structure

Write `synthesis/manuscript.md` using exactly this skeleton (it mirrors
the Royal Society evidence-synthesis article type):

```
# [Title — names the question and the audience]

## Stance declaration
One sentence: this synthesis is policy-neutral / makes a case, and why.

## Plain-language summary
For the identified decision-maker. No jargon. <250 words.

## Background and the decision question
Why this matters now; the exact question; the audience.

## Methods
Protocol, sources searched, search strategy, inclusion/exclusion,
appraisal approach, synthesis method. Enough to reproduce.

## Evidence base (PRISMA-style flow)
Counts identified -> deduped -> screened -> included. Reference prisma.json.

## Findings
Structured synthesis. Every claim cited as [@record_id]. Present
agreement, conflict, and certainty. Do not smooth over disagreement.

## Limitations and certainty of evidence
What the evidence does NOT establish. Bias and gaps.

## Implications for the decision-maker
Tied strictly to appraised findings. If stance is policy-neutral, present
options and their evidential support, not a recommendation.

## References
Only keys cited above; each entry from corpus/records.jsonl with locator.
```

Cite inline as `[@record_id]` where `record_id` matches
`corpus/records.jsonl`. The verification script checks that every `[@...]`
resolves and that no Findings paragraph is uncited.

## Progress log

Keep `synthesis/progress.md` as a short append-only log. After each
checkpoint append one block:

```
## Checkpoint <n> — <name> — <date/time>
Done: <what was produced>
Verified: <verify_synthesis.py --stage <n> result>
Blocked: <none | what and why>
Next: <next checkpoint>
```

Keep status updates compact and honest. If status becomes vague, that is
the signal to tighten on the specific failing check, not to add prose.

## When to pause vs. stop

- `/goal pause` at Checkpoint 5 and Checkpoint 10 (human gates), or when
  the verification script reports a failure you cannot resolve without a
  scoping decision (e.g., a key source is inaccessible).
- Do **not** stop merely because the draft reads well, or because time
  has passed. Stop only on `verify_synthesis.py --final` exit 0.
- If the protocol needs to change, pause, record the change and rationale
  in `progress.md`, update `protocol.md`, then resume — never re-scope
  silently to make a check pass.

## Reference

`scripts/verify_synthesis.py` is the executable stopping condition. Run
`--stage N synthesis/` after each checkpoint and `--final synthesis/`
before declaring the goal met. Read its `--help` for the full check list.
It is stdlib-only and offline-tolerant; pass `--check-urls` to also
attempt locator resolution where network is available.

`references/methodology.md` is the *how* behind the checkpoints. Read it
whenever a checkpoint reaches a methodological decision the contract keeps
terse: choosing the synthesis type and framing the question (before
Checkpoint 1), building a reproducible search (Checkpoint 2), selecting a
risk-of-bias tool (Checkpoint 5), deciding meta-analysis vs structured
synthesis and rating certainty (Checkpoint 7), and reporting standards
(Checkpoint 8). Its final section states the honest limits of an
autonomous run — reflect those as manuscript limitations where they
apply; do not let a passing `--final` create false assurance.
