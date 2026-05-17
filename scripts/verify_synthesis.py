#!/usr/bin/env python3
"""verify_synthesis.py — the executable stopping condition for the
evidence-synthesis skill run under Codex /goal.

The point of this script: a goal-following agent must not be able to
declare "done" on the basis of its own confidence. "Done" is defined as
"all artifacts exist, internally reconcile, citations are real, and the
human gates are signed off". This script encodes exactly that.

Exit code 0  -> the checked stage (or the whole synthesis with --final)
                passes. Under /goal this is the stopping condition.
Exit code 1  -> one or more checks failed. The agent should keep working
                on the reported failures (or pause at a human gate).
Exit code 2  -> usage / structural error (e.g. missing synthesis dir).

stdlib only. Offline-tolerant: locator checks are structural by default;
pass --check-urls to additionally attempt resolution where a network is
available (failures there are reported as warnings, not hard failures,
unless --strict-urls is also given).
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

# ----------------------------------------------------------------------
# small helpers
# ----------------------------------------------------------------------

DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$", re.IGNORECASE)
URL_RE = re.compile(r"^https?://\S+$", re.IGNORECASE)
CITE_RE = re.compile(r"\[@([A-Za-z0-9_\-:.]+)\]")

EXCLUSION_ALLOWED_FALLBACK = {
    "wrong_population", "wrong_intervention", "wrong_comparator",
    "wrong_outcome", "wrong_study_design", "out_of_date_range",
    "wrong_geography", "language", "duplicate", "not_primary_evidence",
    "full_text_unavailable", "other",
}


class Report:
    def __init__(self) -> None:
        self.failures: list[str] = []
        self.warnings: list[str] = []
        self.ok: list[str] = []

    def fail(self, msg: str) -> None:
        self.failures.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def passed(self, msg: str) -> None:
        self.ok.append(msg)

    def emit(self) -> int:
        for m in self.ok:
            print(f"  PASS  {m}")
        for m in self.warnings:
            print(f"  WARN  {m}")
        for m in self.failures:
            print(f"  FAIL  {m}")
        print()
        if self.failures:
            print(f"RESULT: FAIL ({len(self.failures)} failing check(s), "
                  f"{len(self.warnings)} warning(s))")
            return 1
        print(f"RESULT: PASS ({len(self.ok)} check(s) ok, "
              f"{len(self.warnings)} warning(s))")
        return 0


def _read_jsonl(path: Path, rep: Report) -> list[dict]:
    rows: list[dict] = []
    try:
        for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as e:
                rep.fail(f"{path.name}:{i} is not valid JSON ({e})")
    except FileNotFoundError:
        rep.fail(f"missing required artifact: {path}")
    return rows


def _read_csv(path: Path, rep: Report) -> tuple[list[str], list[dict]]:
    try:
        with path.open(encoding="utf-8", newline="") as fh:
            reader = csv.DictReader(fh)
            header = reader.fieldnames or []
            return list(header), list(reader)
    except FileNotFoundError:
        rep.fail(f"missing required artifact: {path}")
        return [], []


def _read_json(path: Path, rep: Report) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        rep.fail(f"missing required artifact: {path}")
    except json.JSONDecodeError as e:
        rep.fail(f"{path.name} is not valid JSON ({e})")
    return {}


def _valid_locator(loc: str) -> bool:
    loc = (loc or "").strip()
    if loc.lower().startswith("doi:"):
        loc = loc[4:].strip()
    return bool(DOI_RE.match(loc) or URL_RE.match(loc))


# ----------------------------------------------------------------------
# stage checks
# ----------------------------------------------------------------------

def check_protocol(d: Path, rep: Report) -> None:
    p = d / "protocol.md"
    try:
        text = p.read_text(encoding="utf-8").lower()
    except FileNotFoundError:
        rep.fail(f"missing required artifact: {p}")
        return
    required = {
        "decision question": ["decision question", "research question"],
        "audience": ["audience", "decision-maker", "decision maker"],
        "stance": ["policy-neutral", "makes a case", "makes-a-case", "stance"],
        "framing": ["pico", "peco", "framing"],
        "inclusion/exclusion": ["inclusion", "exclusion"],
        "sources/search": ["search strategy", "databases", "sources"],
        "method": ["systematic review", "meta-analysis",
                   "evidence review", "narrative synthesis", "method"],
        "page budget": ["page", "word", "budget"],
    }
    for label, needles in required.items():
        if any(n in text for n in needles):
            rep.passed(f"protocol contains '{label}'")
        else:
            rep.fail(f"protocol.md missing required section: {label}")
    if "policy-neutral" not in text and "makes a case" not in text \
            and "makes-a-case" not in text:
        rep.fail("protocol.md must declare stance explicitly "
                 "(policy-neutral or makes-a-case)")


def check_search(d: Path, rep: Report) -> list[dict]:
    rows = _read_jsonl(d / "search_log.jsonl", rep)
    if not rows:
        if not rep.failures:
            rep.fail("search_log.jsonl has no searches recorded")
        return rows
    for i, r in enumerate(rows, 1):
        for field in ("source", "query", "date", "raw_count", "records_file"):
            if field not in r:
                rep.fail(f"search_log line {i} missing '{field}'")
        rc = r.get("raw_count")
        rf = r.get("records_file")
        if isinstance(rc, int) and rc > 0 and rf:
            fp = d / rf if not Path(rf).is_absolute() else Path(rf)
            if not fp.exists():
                rep.fail(f"search_log line {i}: records_file '{rf}' "
                         f"does not exist but raw_count={rc}")
            elif fp.stat().st_size == 0:
                rep.fail(f"search_log line {i}: records_file '{rf}' is empty "
                         f"but raw_count={rc}")
    if not [f for f in rep.failures]:
        rep.passed(f"search_log.jsonl: {len(rows)} search(es) recorded "
                   f"and reconciled")
    return rows


def check_corpus(d: Path, rep: Report) -> list[dict]:
    rows = _read_jsonl(d / "corpus" / "records.jsonl", rep)
    seen: set[str] = set()
    for i, r in enumerate(rows, 1):
        rid = r.get("id")
        if not rid:
            rep.fail(f"corpus record {i} has no 'id'")
            continue
        if rid in seen:
            rep.fail(f"corpus has duplicate id '{rid}'")
        seen.add(rid)
        if not _valid_locator(r.get("locator", "")):
            rep.fail(f"corpus record '{rid}' has no well-formed locator "
                     f"(need DOI or http(s) URL) — possible fabrication")
        for field in ("title", "authors", "year", "source"):
            if not r.get(field):
                rep.fail(f"corpus record '{rid}' missing '{field}'")
    dr = _read_json(d / "dedup_report.json", rep)
    if dr:
        raw = dr.get("raw_total")
        dup = dr.get("duplicates_removed")
        ded = dr.get("deduped_total")
        if None in (raw, dup, ded):
            rep.fail("dedup_report.json must have raw_total, "
                     "duplicates_removed, deduped_total")
        else:
            if raw - dup != ded:
                rep.fail(f"dedup arithmetic does not reconcile: "
                         f"{raw} - {dup} != {ded}")
            if ded != len(rows):
                rep.fail(f"dedup_report deduped_total={ded} but "
                         f"corpus has {len(rows)} records")
            if not rep.failures:
                rep.passed(f"corpus: {len(rows)} unique records, "
                           f"locators well-formed, dedup reconciles")
    return rows


def check_screening(d: Path, corpus: list[dict], rep: Report) -> set[str]:
    header, rows = _read_csv(d / "screening.csv", rep)
    needed = {"record_id", "ta_decision", "ft_decision", "exclusion_reason"}
    if header and not needed.issubset(set(header)):
        rep.fail(f"screening.csv missing columns: "
                 f"{sorted(needed - set(header))}")
        return set()
    corpus_ids = {r.get("id") for r in corpus}
    seen: set[str] = set()
    included: set[str] = set()
    for r in rows:
        rid = r.get("record_id")
        if rid in seen:
            rep.fail(f"screening.csv: record_id '{rid}' appears more than once")
        seen.add(rid)
        ta = (r.get("ta_decision") or "").strip().lower()
        ft = (r.get("ft_decision") or "").strip().lower()
        reason = (r.get("exclusion_reason") or "").strip()
        is_excluded = ta in {"exclude", "no"} or ft in {"exclude", "no"}
        is_included = ft in {"include", "yes"}
        if is_excluded and not reason:
            rep.fail(f"screening.csv: '{rid}' excluded with no "
                     f"exclusion_reason")
        if is_included:
            included.add(rid)
    if corpus_ids and seen != corpus_ids:
        missing = corpus_ids - seen
        extra = seen - corpus_ids
        if missing:
            rep.fail(f"screening.csv does not cover {len(missing)} corpus "
                     f"record(s), e.g. {sorted(list(missing))[:3]}")
        if extra:
            rep.fail(f"screening.csv references {len(extra)} id(s) not in "
                     f"corpus, e.g. {sorted(list(extra))[:3]}")
    if not rep.failures:
        rep.passed(f"screening.csv: every corpus record screened once; "
                   f"{len(included)} included")
    return included


def check_appraisal(d: Path, included: set[str], rep: Report) -> None:
    header, rows = _read_csv(d / "appraisal.csv", rep)
    if not header:
        return
    if "record_id" not in header or "human_reviewed" not in header:
        rep.fail("appraisal.csv must have 'record_id' and 'human_reviewed'")
        return
    appraised = {r.get("record_id") for r in rows}
    if included and not included.issubset(appraised):
        miss = included - appraised
        rep.fail(f"{len(miss)} included study(ies) not appraised, e.g. "
                 f"{sorted(list(miss))[:3]}")
    not_reviewed = [r.get("record_id") for r in rows
                    if str(r.get("human_reviewed", "")).strip().lower()
                    not in {"true", "yes", "1"}]
    if not_reviewed:
        rep.fail(f"HUMAN GATE: {len(not_reviewed)} appraisal row(s) not "
                 f"human_reviewed (e.g. {not_reviewed[:3]}). Run /goal "
                 f"pause and request review — do not self-approve.")
    else:
        rep.passed("appraisal.csv: all included studies appraised and "
                   "human-reviewed")


def check_extraction(d: Path, included: set[str], rep: Report) -> None:
    header, rows = _read_csv(d / "extraction.csv", rep)
    if not header:
        return
    if "record_id" not in header:
        rep.fail("extraction.csv must have a 'record_id' column")
        return
    extracted = {r.get("record_id") for r in rows}
    if included and not included.issubset(extracted):
        miss = included - extracted
        rep.fail(f"{len(miss)} included study(ies) have no extraction row, "
                 f"e.g. {sorted(list(miss))[:3]}")
    else:
        rep.passed(f"extraction.csv: all {len(included)} included studies "
                   f"have extracted data")


def check_prisma(d: Path, search: list[dict], corpus: list[dict],
                 included: set[str], rep: Report) -> None:
    pr = _read_json(d / "prisma.json", rep)
    if not pr:
        return
    for k in ("identified", "after_dedup", "screened", "included"):
        if k not in pr:
            rep.fail(f"prisma.json missing '{k}'")
    if rep.failures:
        return
    raw_total = sum(int(s.get("raw_count", 0)) for s in search)
    if search and pr["identified"] != raw_total:
        rep.fail(f"prisma identified={pr['identified']} but search_log "
                 f"raw_count sum={raw_total}")
    if corpus and pr["after_dedup"] != len(corpus):
        rep.fail(f"prisma after_dedup={pr['after_dedup']} but corpus "
                 f"has {len(corpus)} records")
    if included and pr["included"] != len(included):
        rep.fail(f"prisma included={pr['included']} but screening marks "
                 f"{len(included)} included")
    if not rep.failures:
        rep.passed("prisma.json reconciles with search, corpus, screening")


def check_manuscript_and_citations(d: Path, corpus: list[dict],
                                    rep: Report) -> set[str]:
    p = d / "manuscript.md"
    try:
        text = p.read_text(encoding="utf-8")
    except FileNotFoundError:
        rep.fail(f"missing required artifact: {p}")
        return set()
    low = text.lower()
    if "stance declaration" not in low:
        rep.fail("manuscript.md missing 'Stance declaration' section")
    if "policy-neutral" not in low and "makes a case" not in low \
            and "makes-a-case" not in low:
        rep.fail("manuscript.md does not state its stance explicitly")
    for sec in ("plain-language summary", "methods", "findings",
                "limitations", "references"):
        if sec not in low:
            rep.fail(f"manuscript.md missing section: {sec}")

    cited = set(CITE_RE.findall(text))
    corpus_ids = {r.get("id") for r in corpus}
    if not cited:
        rep.fail("manuscript.md has no [@record_id] citations — a synthesis "
                 "must cite its evidence base")
    unresolved = sorted(c for c in cited if c not in corpus_ids)
    if unresolved:
        rep.fail(f"{len(unresolved)} citation key(s) do not resolve to a "
                 f"corpus record (possible fabrication): "
                 f"{unresolved[:5]}")

    # Findings section must not contain uncited paragraphs.
    m = re.search(r"^#+\s*findings\b(.*?)(^#+\s|\Z)",
                  text, re.IGNORECASE | re.DOTALL | re.MULTILINE)
    if m:
        body = m.group(1)
        for para in [b.strip() for b in body.split("\n\n") if b.strip()]:
            if para.startswith("#"):
                continue
            words = len(re.findall(r"\w+", para))
            if words >= 25 and not CITE_RE.search(para):
                rep.fail("Findings contains a substantive uncited paragraph "
                         f"(starts: \"{para[:60].strip()}...\")")
                break
    if not rep.failures:
        rep.passed(f"manuscript.md: structure ok, {len(cited)} citation(s) "
                   f"all resolve, Findings cited")
    return cited


def check_citation_audit(d: Path, cited: set[str], rep: Report,
                         check_urls: bool, strict_urls: bool) -> None:
    rows = _read_jsonl(d / "citation_audit.jsonl", rep)
    audited = {r.get("key") for r in rows}
    missing = sorted(c for c in cited if c not in audited)
    if missing:
        rep.fail(f"{len(missing)} cited key(s) not in citation_audit.jsonl: "
                 f"{missing[:5]}")
    for r in rows:
        if r.get("status") == "fabricated_or_unverifiable":
            rep.fail(f"citation '{r.get('key')}' is marked "
                     f"fabricated_or_unverifiable — remove or replace it")
        if r.get("resolves") is False and not check_urls:
            rep.warn(f"citation '{r.get('key')}' marked resolves=false")
    if check_urls:
        _resolve_urls(d, rep, strict_urls)
    if not [f for f in rep.failures]:
        rep.passed(f"citation_audit.jsonl: all {len(cited)} cited keys "
                   f"audited, none fabricated")


def _resolve_urls(d: Path, rep: Report, strict: bool) -> None:
    import urllib.request
    import urllib.error
    corpus = _read_jsonl(d / "corpus" / "records.jsonl", Report())
    for r in corpus:
        loc = (r.get("locator") or "").strip()
        if loc.lower().startswith("doi:"):
            loc = "https://doi.org/" + loc[4:].strip()
        elif DOI_RE.match(loc):
            loc = "https://doi.org/" + loc
        if not URL_RE.match(loc):
            continue
        try:
            req = urllib.request.Request(loc, method="HEAD",
                                         headers={"User-Agent": "verify"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status >= 400:
                    raise urllib.error.HTTPError(
                        loc, resp.status, "", {}, None)
        except Exception as e:  # noqa: BLE001 - offline tolerant
            msg = (f"locator for '{r.get('id')}' did not resolve "
                   f"({type(e).__name__})")
            (rep.fail if strict else rep.warn)(msg)


def check_signoff(d: Path, rep: Report) -> None:
    so = _read_json(d / "signoff.json", rep)
    if not so:
        rep.fail("HUMAN GATE: signoff.json missing — final review not done")
        return
    if so.get("appraisal_signed_off") is not True:
        rep.fail("HUMAN GATE: appraisal not signed off in signoff.json")
    if so.get("final_review_signed_off") is not True:
        rep.fail("HUMAN GATE: final stance/over-claim review not signed off")
    if not so.get("reviewer"):
        rep.fail("signoff.json must name the reviewer")
    if not rep.failures:
        rep.passed("signoff.json: both human gates signed off by "
                   f"{so.get('reviewer')}")


# ----------------------------------------------------------------------
# orchestration
# ----------------------------------------------------------------------

STAGE_NAMES = {
    1: "protocol", 2: "search", 3: "corpus", 4: "screening",
    5: "appraisal", 6: "extraction", 7: "manuscript",
    8: "prisma", 9: "citation-audit", 10: "signoff",
}


def run(d: Path, stage: int | None, final: bool,
        check_urls: bool, strict_urls: bool) -> int:
    rep = Report()
    if not d.is_dir():
        print(f"error: synthesis directory not found: {d}", file=sys.stderr)
        return 2

    stages = list(range(1, 11)) if (final or stage is None) else [stage]
    label = "FINAL" if final else (f"STAGE {stage} "
                                   f"({STAGE_NAMES.get(stage, '?')})"
                                   if stage else "ALL STAGES")
    print(f"\n=== verify_synthesis : {label} : {d} ===\n")

    corpus: list[dict] = []
    search: list[dict] = []
    included: set[str] = set()
    cited: set[str] = set()

    # Stages are cumulative; later checks need earlier artifacts, so load
    # them whenever a later stage is requested.
    need = set(stages)
    if any(s >= 3 for s in stages):
        need |= {2, 3}
    if any(s >= 4 for s in stages):
        need |= {4}
    if any(s >= 8 for s in stages):
        need |= {2, 3, 4}
    if any(s >= 9 for s in stages):
        need |= {3, 7}

    if 1 in stages:
        check_protocol(d, rep)
    if 2 in need:
        search = check_search(d, rep)
    if 3 in need:
        corpus = check_corpus(d, rep)
    if 4 in need:
        included = check_screening(d, corpus, rep)
    if 5 in stages:
        check_appraisal(d, included, rep)
    if 6 in stages:
        check_extraction(d, included, rep)
    if 7 in stages or 9 in need:
        cited = check_manuscript_and_citations(d, corpus, rep)
    if 8 in stages:
        check_prisma(d, search, corpus, included, rep)
    if 9 in stages:
        check_citation_audit(d, cited, rep, check_urls, strict_urls)
    if 10 in stages or final:
        check_signoff(d, rep)

    return rep.emit()


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        description="Verifiable stopping condition for the "
                    "evidence-synthesis skill (Codex /goal).")
    ap.add_argument("synthesis_dir", type=Path,
                    help="path to the synthesis/ working directory")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--stage", type=int, choices=range(1, 11),
                   help="verify a single checkpoint (1-10)")
    g.add_argument("--final", action="store_true",
                   help="verify the whole synthesis incl. human gates; "
                        "exit 0 here is the /goal stopping condition")
    ap.add_argument("--check-urls", action="store_true",
                    help="also attempt to resolve locators over the "
                         "network (warnings unless --strict-urls)")
    ap.add_argument("--strict-urls", action="store_true",
                    help="treat unresolved locators as hard failures")
    a = ap.parse_args(argv)
    return run(a.synthesis_dir, a.stage, a.final,
               a.check_urls, a.strict_urls)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
