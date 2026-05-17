# Evidence synthesis — methodology reference

Consult this file when the SKILL.md checkpoints reach a methodological
decision the main file deliberately keeps terse: choosing the synthesis
type, framing the question, building the search, selecting a risk-of-bias
tool, deciding meta-analysis vs structured narrative, rating certainty,
and reporting. The SKILL.md is the contract; this file is the *how*.

This is decision guidance, not a substitute for a methodologist. When a
choice here materially changes scope or conclusions, that is a `/goal
pause` point, not an autonomous decision.

## Contents

1. Choosing the synthesis type
2. Framing the question
3. Search strategy
4. Screening and selection
5. Critical appraisal — tool selection by design
6. Data extraction
7. Meta-analysis: when, and how not to misuse it
8. Structured synthesis without meta-analysis (SWiM)
9. Certainty of evidence (GRADE family)
10. Bias, spin, and stance discipline
11. Reporting standards
12. The four principles → artifact mapping
13. Honest limits of an autonomous run

---

## 1. Choosing the synthesis type

Pick the lightest design that still answers the decision question
defensibly, and state it in `protocol.md`. The choice is driven by the
question, the evidence base, and the time the decision can wait for.

- **Structured/narrative evidence review** — default for policy
  questions spanning heterogeneous designs or outcomes. Systematic search
  and appraisal, narrative synthesis. Use when effects are not
  statistically combinable.
- **Systematic review** — a clearly formulated question, exhaustive
  search, explicit selection, formal appraisal. May or may not include
  meta-analysis.
- **Meta-analysis** — only when included studies estimate a conceptually
  comparable effect, measured commensurably, with assessable
  heterogeneity. Meta-analysis is a *method within* a review, not a
  separate license to pool anything numeric.
- **Scoping review** — when the goal is to map what evidence exists and
  how it is studied, not to answer an effect question. Report with
  PRISMA-ScR. Does not produce pooled effects or graded certainty.
- **Rapid review** — a systematic review with pre-declared, justified
  shortcuts (e.g., single-reviewer screening, restricted sources, no
  meta-analysis). Permitted for time-critical decisions *only if every
  shortcut is recorded in the protocol and its risk acknowledged*. Never
  present a rapid review as a full systematic review.

Decision rule for meta-analysis vs narrative: pool **only if** (a) the
PICO is the same across studies, (b) outcomes are measured on a
combinable scale or convertible to one, (c) study designs are similar
enough that an average effect is meaningful, and (d) heterogeneity can be
quantified and interpreted. If any fails → structured synthesis (§8).

---

## 2. Framing the question

A synthesis question must be answerable and scoped to its audience. Use
the framework that fits the question type:

- **PICO** — intervention effect questions: Population, Intervention,
  Comparator, Outcome. Add **S** (study designs) for the eligibility
  boundary, **T** (timeframe) where relevant.
- **PECO** — exposure questions (environmental, epidemiological):
  Exposure replaces Intervention.
- **PICOC** — adds Context; useful for policy where transferability
  across settings is part of the question.
- **SPIDER** — qualitative/mixed evidence: Sample, Phenomenon of
  Interest, Design, Evaluation, Research type.
- **PIRO / CoCoPop** — prevalence/burden questions (Condition, Context,
  Population).

For policy syntheses the *audience and decision context* are part of the
frame: state what decision the answer informs and what would change it.
Vague questions ("what do we know about X") must be sharpened before
searching; record the final question as pre-registered.

---

## 3. Search strategy

The search is the part most often unreproducible, and reproducibility is
non-negotiable. Build and log it as follows.

- **Concept blocks.** Decompose the question into 2–4 concepts (e.g.,
  Population AND Intervention AND Outcome). Within each block, OR together
  controlled vocabulary and free-text synonyms; AND the blocks together.
- **Controlled vocabulary + free text.** Use database thesaurus terms
  (MeSH in MEDLINE, Emtree in Embase) *and* title/abstract keywords;
  controlled vocabulary alone misses recent/unindexed records.
- **Sensitivity over precision.** A synthesis search favours recall;
  expect to screen out most hits. Do not narrow the search to reduce
  screening load.
- **Multiple sources.** At minimum a bibliographic database; for policy
  questions also search trial/protocol registries, preprint servers, HTA
  agencies, government and NGO reports, and reference lists. Grey
  literature counters publication bias.
- **Citation chasing.** Backward (references of included studies) and
  forward (works citing them) snowballing catches what database syntax
  misses. Record it as a search source.
- **Date/language limits** must be justified in the protocol, not applied
  for convenience; language restriction is itself a bias.
- **When to stop searching.** There is no fixed N. Stop when the planned
  sources are exhausted and snowballing yields no new includable records.
  Log every executed query verbatim (this populates `search_log.jsonl`),
  so the search can be rerun.

Report search methods to PRISMA-S granularity: each source, the full
query string, date run, and counts.

---

## 4. Screening and selection

- Screen in two passes: title/abstract against eligibility, then full
  text. Be inclusive at title/abstract (when in doubt, carry forward).
- **Record exclusion reasons at the full-text stage** (PRISMA convention):
  each full-text exclusion gets one primary reason from the protocol's
  criteria. Title/abstract exclusions are counted, not individually
  reasoned.
- Dual independent screening is the methodological ideal. A single
  autonomous agent cannot self-replicate independence; this skill
  compensates with the human appraisal gate, but record in `protocol.md`
  that screening was single-pass and treat that as a stated limitation —
  do not imply dual screening occurred.
- Keep the flow auditable: every deduplicated record has exactly one
  screening fate, and the numbers must reconcile into `prisma.json`.

---

## 5. Critical appraisal — tool selection by design

Appraise *every included study* with a tool matched to its design. Using
the wrong tool (or none) invalidates the certainty rating. Selection
table:

| Study / evidence type | Use |
|---|---|
| Randomised controlled trial | Cochrane RoB 2 |
| Non-randomised study of an intervention | ROBINS-I |
| Cohort / case-control (observational, non-intervention) | Newcastle–Ottawa Scale, or JBI design-specific checklist |
| Diagnostic test accuracy | QUADAS-2 |
| Prognostic / risk-prediction model | PROBAST |
| Prevalence / incidence study | JBI prevalence critical-appraisal checklist |
| Qualitative study | CASP qualitative, or JBI qualitative |
| Mixed-methods study | MMAT |
| Economic evaluation | Drummond checklist, or CHEC |
| A systematic review being *included* as evidence | AMSTAR 2 (and/or ROBIS for risk of bias) |
| Animal experimental study | SYRCLE risk-of-bias tool |

Rules:

- Appraise at the **outcome level** where the tool supports it (RoB 2 and
  ROBINS-I are per-result, not per-study) — bias can differ by outcome.
- Record the domain-level judgements, not just an overall label, so the
  certainty rating in §9 can use them.
- Appraisal is judgement-heavy and is a **human gate** (Checkpoint 5).
  Produce the appraisal, then `/goal pause`; do not set `human_reviewed`.

---

## 6. Data extraction

- Use a pre-specified extraction schema; decide fields before extracting
  to avoid outcome cherry-picking.
- Every extracted value is keyed to a `record_id` and should be locatable
  in the source (table/figure/section). No value enters `extraction.csv`
  that is not stated by the study.
- **Never impute, estimate, or back-calculate silently.** If a needed
  statistic is missing, record it missing. Standard conversions (e.g.,
  SE↔CI, median/IQR→mean/SD via accepted formulae) are permitted only if
  the conversion method is named in the protocol and the source provides
  the required inputs.
- Harmonise units and effect directions before synthesis; document the
  transformation.
- Missing data: prefer contacting authors / using study-reported values;
  if unresolved, carry as missing and reflect it in certainty (§9), not
  in an invented number.

---

## 7. Meta-analysis: when, and how not to misuse it

Only if §1's pooling rule is satisfied.

- **Effect measure.** Binary: risk ratio or odds ratio (report absolute
  risk difference for the audience too); continuous: mean difference if
  same scale, standardised mean difference if different scales;
  time-to-event: hazard ratio.
- **Model.** Random-effects is the sensible default in policy/clinical
  syntheses because between-study heterogeneity is expected; state the
  estimator (e.g., REML) and report a prediction interval, not only the
  summary effect.
- **Heterogeneity.** Report τ² (between-study variance), I² (proportion
  of variability not due to chance), and the prediction interval.
  Interpret heterogeneity; do not pool through severe, unexplained
  heterogeneity just because the arithmetic runs.
- **Pre-specify** subgroup and sensitivity analyses in the protocol;
  post-hoc subgrouping is hypothesis-generating at best and must be
  labelled as such.
- **Small-study / publication bias.** Funnel plot and an asymmetry test
  (e.g., Egger's) are interpretable only with roughly ≥10 studies; with
  fewer, assess reporting bias qualitatively.
- **Do not** meta-analyse incommensurable outcomes, combine adjusted and
  unadjusted estimates indiscriminately, or pool a single study.

---

## 8. Structured synthesis without meta-analysis (SWiM)

When pooling is inappropriate, synthesise transparently rather than
narrating impressionistically.

- **Group** studies by a pre-stated logic (population, intervention
  variant, outcome domain) and state the grouping rationale.
- **Avoid naive vote counting.** Counting "significant vs not" ignores
  effect size, direction, precision, and study quality and is a known
  failure mode. Prefer summarising **direction and magnitude of effect**
  with certainty, e.g., effect-direction tables or harvest plots.
- **Structure the narrative**: for each grouping, state the number and
  type of studies, the range and direction of effects, consistency,
  quality, and the resulting certainty — then what the decision-maker can
  and cannot conclude.
- Make conflict explicit. Where studies disagree, present the
  disagreement and plausible reasons (population, design, bias); do not
  resolve it by selective emphasis.

Report SWiM methods so the synthesis logic is reproducible.

---

## 9. Certainty of evidence (GRADE family)

Rate how much confidence the decision-maker can place in each key
outcome, not just whether studies exist.

- **GRADE** for quantitative effect questions. Start from the design
  (RCT evidence begins high, observational begins low) and rate
  **down** for: risk of bias, inconsistency, indirectness, imprecision,
  publication bias; rate **up** (observational only) for: large
  magnitude, dose–response, plausible confounding that would reduce an
  observed effect. End at high / moderate / low / very low.
- **GRADE-CERQual** for qualitative evidence: confidence from
  methodological limitations, coherence, adequacy, and relevance of data.
- Phrase findings to match certainty. High: "X reduces Y." Moderate:
  "X probably reduces Y." Low: "X may reduce Y." Very low: "the evidence
  is very uncertain about the effect of X on Y." This wording discipline
  is how the manuscript avoids over-claiming.
- Build a brief summary-of-findings view for the key outcomes; this is
  what a policy audience actually reads.

---

## 10. Bias, spin, and stance discipline

- **Reporting/publication bias**: absence of evidence is not evidence of
  absence; flag where the literature is likely incomplete.
- **Selective outcome reporting** in primary studies: check protocols/
  registries where available; note discrepancies.
- **Spin**: do not frame a null or uncertain result as positive. The
  conclusion may not exceed the appraised, graded evidence.
- **Stance**: the protocol declares *policy-neutral* or *makes-a-case*.
  Policy-neutral means present options and their evidential support
  without recommending. `/goal` momentum biases toward a confident
  recommendation — this is a known drift; the verification script's
  uncited-paragraph and stance checks plus the human review gate exist to
  counter it. If the evidence genuinely supports a single course, that is
  a finding to be stated at its certainty level, not advocacy.

---

## 11. Reporting standards

- **PRISMA 2020** — the reporting backbone for systematic reviews;
  drives the flow counts in `prisma.json` and the Methods section.
- **PRISMA-S** — search reporting granularity (per-source query strings,
  dates, counts).
- **PRISMA-ScR** — scoping reviews.
- **MOOSE / relevant equivalents** — observational-study syntheses.
- For the Royal Society / Academy of Medical Sciences evidence-synthesis
  article type: tailor to the named audience, be accessible to
  non-specialists, be explicit about stance, and keep to the page budget.
  Policy relevance and a clear audience at the outset are what
  distinguish this from a standard academic review.

---

## 12. The four principles → artifact mapping

The Royal Society / AMS principles for good evidence synthesis map onto
this skill's artifacts. Use this to check the synthesis is principled,
not just complete.

| Principle | Met by | Artifact |
|---|---|---|
| **Inclusive** — represents the relevant evidence | Sensitive multi-source search + snowballing | `search_log.jsonl`, `corpus/records.jsonl` |
| **Rigorous** — sound, design-appropriate method | Tool-matched appraisal + graded certainty | `appraisal.csv`, GRADE statements in `manuscript.md` |
| **Transparent** — reproducible process | Pre-registered protocol, verbatim search log, reconciling counts | `protocol.md`, `prisma.json`, `progress.md` |
| **Accessible** — usable by the named audience | Plain-language summary, stance declared, page budget, options not jargon | `manuscript.md` |

---

## 13. Honest limits of an autonomous run

State these as limitations in the manuscript where they apply; do not let
the verification gates create false assurance.

- The script checks that artifacts exist, reconcile, and that citations
  resolve structurally. It does **not** verify that a cited source
  actually supports the claim attached to it — that requires the human
  review gate and, ideally, source checking.
- Single-agent screening lacks independent dual review; record it.
- Search recall cannot be fully self-verified; an agent does not know
  what it failed to find. Snowballing and grey-literature breadth
  mitigate but do not eliminate this.
- Appraisal and certainty rating are expert judgements; the human gate is
  load-bearing, not a formality.
- A passing `--final` means the process was followed and is auditable. It
  does not by itself make the synthesis publication-ready or correct.
