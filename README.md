# SameCapRisk-Bench

Companion benchmark artifact for the paper:

> **Right Family, Wrong Skill: Benchmarking Risk Exposure in Agent Skill
> Retrieval** (under review)

SameCapRisk-Bench measures a retrieval failure where a system finds the right
capability family but exposes the wrong same-capability representative. Each
risk-exposure unit records a query, a helpful skill, a query-specific risky
sibling, a capability family relation, a fixed candidate pool, and admission
evidence for that label.

This repository contains the review snapshot used by the paper: query-case
tables, fixed candidate pools, family relations, ranked outputs, schemas,
summary reports, and CPU scripts for checking the reported benchmark results.
The 694 core queries and all query-dependent ranks use the repaired canonical
query surface. Schema, fixed-rank, selector, and clustered-uncertainty checks
pass.

## What is included

- 1,190 skill-risk units and 1,686 evaluation query cases.
- 694 audited core marked-sibling units under public-library pressure.
- 496 hard query-conditioned role-flip units, each contributing two paired
  query-relative cases.
- 9,040 fixed candidate rows summed across the separate core and hard
  evaluation surfaces; no query ranks over a shared 9,040-candidate pool.
- Main retrieval results, cutoff/stratum tables, selector certificates,
  family-source diagnostics, selector-on-public-scores diagnostics, R3-Skill,
  open neural/listwise diagnostics, and label/scope audit summaries.

## Five-minute quickstart

The same minimal instructions are also available in
`ARTIFACT_QUICKSTART.md`.

From the artifact root, run:

```bash
python3 -m pip install -r requirements.txt
bash scripts/run_release_checks.sh
python3 scripts/reproduce_results.py
```

Expected outputs:

- `reports/validation_report.json` with `"status": "ok"`.
- `reports/reproduction_report.json` with `"status": "ok"`.
- Recomputed result summaries from fixed TSV candidate pools and ranked
  outputs.

This quickstart checks the released benchmark surface. It does not rerun GPU
embedding, reranker, or LLM inference from raw checkpoints.

## Repository layout

- `data/`: benchmark units, query cases, candidate pools, and family relations.
- `schemas/`: required-column contracts for the released tables.
- `scripts/`: release validation, metric reproduction, uncertainty
  recomputation, and family-source aggregation.
- `results/`: fixed per-query ranks and paper-facing result summaries.
- `reports/`: composition, admission, provenance, validity, and diagnostic
  summaries.
- `manifest.json`: benchmark counts, surface hashes, and release boundaries.

The scripts are the core evaluation and reproduction code for the released
benchmark. They recompute Recall, NDCG, HSR, CleanHit, cutoff sensitivity,
uncertainty, and selector-certificate results from the released data and fixed
ranks. They do not claim to reproduce neural checkpoint inference or retrain
the controlled reference scorer end to end.

## Compute and reproducibility boundary

The release is designed to reproduce paper tables from fixed data and rank
outputs on CPU. We validated the quickstart on local macOS arm64 with Python
3.9.6, NumPy 1.26.4, SciPy 1.11.4, scikit-learn 1.6.1, and pandas 2.3.3.
Neural diagnostic ranks were generated separately on CUDA GPU instances
from cached SkillRouter, SkillRet, R3-Skill, BGE, and Qwen2.5 checkpoints; the
artifact records their fixed outputs and metadata so reviewers do not need to
rerun GPU inference to check the reported benchmark metrics.

## Evidence boundary

The natural-candidate screen, controlled verifier checks, and chooser proxy
answer three separate validity questions. They use different evidence units
and do not form a case-level retrieval-to-execution chain. The natural screen
supports occurrence rather than prevalence; the verifier checks support the
consequences of controlled labels; and the chooser proxy measures first-skill
selection rather than execution outcomes.

Candidate texts are released as inert benchmark data and should not be
executed directly. Some source-derived texts contain example commands,
endpoints, or public test credentials. See `SECURITY.md`.

## Paper claim map

| Paper surface | What it checks | Artifact path |
|---|---|---|
| Benchmark accounting | unit/query/candidate-pool counts | `data/units.tsv`, `data/query_cases.tsv`, `manifest.json` |
| Composition and evidence layers | core evidence layers and risk-type counts | `reports/benchmark_composition_summary.tsv` |
| Reference scorer protocol | grouped folds, negatives, features, and tuning grid | `reports/reference_scorer_config.json` |
| Compute provenance | validated software environments and roles | `reports/environment_provenance.tsv` |
| Main Recall/NDCG/HSR table | helpful retrieval versus marked-sibling exposure, including public R3-Skill | `results/main_table.tsv`, `results/diagnostics/r3_skill_summary.tsv` |
| Recall-HSR figure | public retrievers, same-score selector rows, and reference point | `results/main_table.tsv`, `results/diagnostics/selector_on_public_scores_summary.tsv` |
| Open LLM reranking diagnostic | Qwen2.5-7B listwise reranking over BGE-M3 top-20 candidates | `results/diagnostics/open_llm_listwise_summary.tsv` |
| Family-source sensitivity | released relation versus public resolver sources | `reports/table3_family_source_reference.tsv`, `results/diagnostics/reference_family_source_per_query.tsv` |
| Source/domain composition | source skew, core risk types, hard domains, artifact axes | `reports/source_domain_composition.tsv` |
| Source sensitivity | leave-one-core-source stability check | `reports/source_sensitivity_leave_one_core_domain.tsv` |
| Cutoff sensitivity | K=3/10/20 recall--exposure behavior | `results/cutoff_sensitivity.tsv` |
| Paired tests | paired sign tests for main K=3 comparisons | `reports/paired_sign_tests.tsv` |
| Selector certificate | no-selector exposure versus final exposure | `results/selector_certificate.tsv`, `results/selector_certificate_cases.tsv` |
| Same-score selector diagnostic | public score orders plus released selector, including R3-Skill | `results/diagnostics/selector_on_public_scores_summary.tsv` |
| No-family-label diagnostic | public score orders plus public family sources | `results/diagnostics/public_family_source_selector_summary.tsv` |
| Label and scope checks | verifier, hard-gate, family-pressure, and natural-candidate validation summaries | `reports/label_validity/`, `reports/gate_summaries/` |

For a more detailed table-by-table mapping, see
`FIGURE_TABLE_ARTIFACT_MAP.md`.

## Files

- `data/units.tsv`: one row per skill-risk unit.
- `data/query_cases.tsv`: one row per evaluation query case.
- `data/candidate_pool.tsv`: candidate texts and roles.
- `data/family_relation.tsv`: family grouping used by the exposure protocol.
- `results/main_table.tsv`: current paper-facing main result table.
- `results/cutoff_sensitivity.tsv`: K=3/10/20 Recall-HSR sensitivity table
  derived from compact per-query ranks.
- `results/extended_k20.tsv`: extended cutoff results.
- `results/selector_certificate.tsv`: no-selector versus final exposure counts.
- `results/compact_predictions.tsv`: per-query helpful/risky ranks used to
  reproduce the result tables.
- `results/selector_certificate_cases.tsv`: per-query selector exposure audit
  used to reproduce the selector certificate.
- `results/stratum_metrics.tsv`: core, hard, and merged metrics by method.
- `results/paired_bootstrap_ci.tsv`: benchmark-unit clustered bootstrap
  intervals for the main reference-pipeline versus public-baseline comparisons.
- `results/diagnostics/`: supplementary public-family-source diagnostics,
  including the R3-Skill public baseline, same-score released-selector
  diagnostics, no-family-label text-cluster selection, BGE reranker
  diagnostics, and Qwen2.5-7B listwise reranking over BGE-M3 top-20
  candidates.
- `results/diagnostics/reference_family_source_per_query.tsv`: 1,686
  per-query rows for each controlled, metadata/title, and text-cluster family
  source used in the reference-interface sensitivity table.
- `reports/paired_sign_tests.tsv`: paired sign tests over 1,190 benchmark
  units, keeping the two queries of each hard role-flip unit together.
- `reports/chooser_proxy/`: prompt, condition summaries, and paired effects for
  the bounded Qwen2.5-7B chooser-proxy check reported in the supplement.
- `reports/admission_ledger.tsv`: public admission and evidence-layer ledger.
- `reports/table3_family_source_reference.tsv`: exact family-source sensitivity
  rows for the controlled reference interface.
- `reports/source_domain_composition.tsv`: compact source, domain, risk-type,
  and artifact-axis coverage table matching the supplementary coverage table.
- `reports/source_sensitivity_leave_one_core_domain.tsv`: source-sensitivity
  diagnostic after dropping each core source domain.
- `reports/label_validity/`: verifier, hard-gate, and model-screened
  natural-candidate validation summaries supporting label validity and HSR
  scope claims.
- `reports/hard_leakage_per_family.tsv`: hard-stratum leakage summary. Raw
  gate transcripts and detailed construction material are not included.
- `schemas/`: required-column schemas for public TSV files.
- `scripts/reproduce_results.py`: recomputes the result summaries from compact
  ranks and selector-case rows.
- `scripts/reproduce_family_source.py`: recomputes the three family-source
  sensitivity rows from their per-query indicators.
- `manifest.json`: count and provenance manifest.
- `FIGURE_TABLE_ARTIFACT_MAP.md`: paper figure/table to artifact path map.
- `SOURCE_AND_LICENSES.md`: source, redistribution, and model-provenance notes.
- `SECURITY.md`: safe-handling guidance for source-derived candidate text.

## Metric Boundary

`HSR@K` counts exposure of the marked risky sibling for each query case. It is
a fixed-library exposure certificate for that annotated sibling. Released
multi-member-family pressure is reported as a scope indicator, not as an
additional risk label.

## Release boundary

The artifact is designed for paper review and table-level reproducibility. It
contains fixed data, schemas, ranked outputs, and summary diagnostics. It does
not include raw private construction transcripts, local model caches, or GPU
inference environments.
