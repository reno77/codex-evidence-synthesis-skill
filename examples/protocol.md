# Protocol — Greenhouse gas emissions of natural vs. synthetic fertilizers

Pre-registered. Written before searching. Any change after this point is
recorded with its rationale in `synthesis/progress.md`; the protocol is
not silently re-scoped to make a verification check pass.

## Decision question

In arable cropping systems, does the application of natural/organic
fertilizers (animal manure, slurry, compost, biosolids, green manure)
result in **more, less, or about the same** greenhouse gas emissions as
synthetic/mineral nitrogen fertilizers, and under what conditions does
the direction change?

This is a comparative environmental-exposure question, not an
intervention-efficacy question.

## Audience

[REPLACE WITH YOUR ACTUAL AUDIENCE — e.g. a national agriculture and
environment policy team weighing fertilizer guidance, or an organic
certification body.] The synthesis is tailored to a decision-maker who
needs to know the direction, size, and conditionality of the difference,
not a literature overview.

## Stance

**policy-neutral.** This synthesis summarises what the evidence shows
about the direction and magnitude of the difference and the conditions
that modify it. It presents options and their evidential support; it does
not recommend a fertilizer policy. Goal momentum toward a confident "X is
greener" conclusion is to be resisted; the conclusion may not exceed the
appraised, GRADE-rated evidence.

## Framing (PECO)

- **Population / setting**: arable / cropland agricultural soils, field
  and farm scale. Field measurement studies, meta-analyses, and life-
  cycle assessments.
- **Exposure**: natural/organic fertilizer — animal manure, slurry,
  compost, digestate, biosolids, green manure / legume residues.
- **Comparator**: synthetic mineral nitrogen fertilizer (urea, ammonium
  nitrate, calcium ammonium nitrate, ammonium sulphate, etc.).
- **Outcome**: greenhouse gas emissions expressed as CO2-equivalent
  (GWP100), with N2O reported separately because it dominates fertilizer-
  related warming. Soil-organic-carbon change and CH4 reported where
  primary studies provide them.

## Critical scoping decisions (these determine what "more/less/same" means)

1. **System boundary**: *cradle-to-farm-gate life cycle*. Includes
   upstream emissions of synthetic N manufacture (Haber-Bosch energy and
   process emissions) and upstream manure/compost management, plus
   field/soil emissions after application. Rationale: a field-only
   boundary systematically flatters synthetic N by excluding its
   manufacturing burden, and a manufacturing-only view flatters organic;
   the policy-relevant comparison is the full chain to the farm gate.
   A *field/soil-emissions-only* analysis is run as a pre-specified
   **sensitivity analysis**, not the primary boundary.
2. **Functional unit**: primary unit is **yield-scaled** (kg CO2e per
   tonne of harvested product or per unit N taken up), because organic
   systems sometimes yield less and a per-hectare-only comparison can
   mislead. Per-hectare and per-kg-N-applied are reported as secondary
   units.
3. **Equivalence basis**: comparisons at equal available-N rate where
   reported; as-applied comparisons included but flagged.
4. **GWP metric**: GWP100. A GWP* treatment of CH4 is out of scope
   (CH4 is minor for most arable fertilizer comparisons); note as a
   limitation if CH4 proves material.

## Inclusion criteria

- Field experiments, farm-scale studies, life-cycle assessments, and
  systematic reviews / meta-analyses that directly compare an
  organic/natural N source with a synthetic mineral N source.
- Report at least one quantified GHG outcome (N2O emission factor or
  flux, CO2e, or full LCA result) attributable to the fertilizer
  contrast.
- Arable / cropland systems. 2000–present (captures modern N2O
  measurement and LCA methods).
- English-language full text available.

## Exclusion criteria

- No direct organic-vs-synthetic contrast (e.g., organic-only or
  synthetic-only studies) → `wrong_comparator`.
- Outcome not a quantified GHG attributable to the fertilizer contrast →
  `wrong_outcome`.
- Non-arable systems (grassland-only, forestry, paddy rice unless a
  separate stratum) outside the stated population → `wrong_population`.
- Pre-2000 → `out_of_date_range`.
- Modelled scenarios with no empirical or LCA grounding →
  `wrong_study_design`.
- Full text unavailable after reasonable effort →
  `full_text_unavailable`.
- Non-English with no usable translation → `language`.

(Exclusion reasons are drawn from this list and recorded only at the
full-text stage, per `references/methodology.md` §4.)

## Sources and search strategy

Sources/databases to search: a major bibliographic database (agricultural
/ environmental science), an LCA-aware source, plus grey literature —
FAO, IPCC emission-factor documentation, national GHG inventory
methodology reports, and institutional agricultural-research repositories.
Backward and forward citation chasing on included reviews and key
primary studies.

Search strategy — three concept blocks, AND-combined; within each block
controlled vocabulary OR free-text synonyms:

- **Block A (fertilizer type contrast)**: organic fertilizer, manure,
  slurry, compost, digestate, biosolids, green manure OR synthetic
  fertilizer, mineral nitrogen, urea, ammonium nitrate, inorganic N.
- **Block B (greenhouse gas outcome)**: nitrous oxide, N2O, greenhouse
  gas, carbon dioxide equivalent, global warming potential, life cycle
  assessment, emission factor, soil carbon.
- **Block C (system)**: arable, cropland, agricultural soil, crop
  production, farming system.

Every executed query is logged verbatim with source, date, and hit count
in `synthesis/search_log.jsonl` (PRISMA-S granularity). The search favours
recall over precision; it is not narrowed to reduce screening load.

## Synthesis method

Systematic evidence review. Quantitative **meta-analysis** of N2O
emission factors and of life-cycle CO2e **only if** the included
estimates are conceptually combinable, measured commensurably, and
heterogeneity is assessable (decision rule in `references/methodology.md`
§1 and §7); random-effects model with prediction interval and I²/τ²
reported, subgroups (boundary, functional unit, crop type, climate)
pre-specified. Where pooling is inappropriate, **structured synthesis
without meta-analysis** (effect-direction summary; no naive vote
counting), per §8. Certainty rated with **GRADE** per §9, and findings
phrased to match certainty.

Critical appraisal: field/LCA primary studies appraised with a design-
appropriate observational/LCA checklist; any included systematic reviews
appraised with AMSTAR 2 — tool selection per `references/methodology.md`
§5. Appraisal is a human gate (Checkpoint 5).

## Page / word budget

Target 6–10 printed pages of main text (~6,000–8,000 words), excluding
references and the PRISMA flow, consistent with the Royal Society
evidence-synthesis article type.
