# Diagnostic Result Tables

These files support supplementary diagnostics that are not main-table baselines.
They expose the effect of using public family sources, rather than the released
controlled family relation, for representative selection over public score
orders.

- `public_family_source_selector_summary.tsv`: aggregate metrics before and
  after representative selection with metadata/title or text-cluster family
  sources.
- `public_family_source_selector_per_query.tsv`: per-query ranks and
  Recall/HSR/CleanHit indicators used to produce the summary table.
- `public_family_source_selector_status.json`: row counts and diagnostic
  boundary.
- `selector_on_public_scores_summary.tsv`: aggregate before/after metrics when
  public score orders are post-processed with the released controlled family
  relation. This is the same-score selector diagnostic used in the Recall-HSR
  figure and includes RRF, SkillRouter, SkillRet, and R3-Skill.
- `selector_on_public_scores_per_query.tsv`: per-query ranks and
  before/after Recall/HSR/NDCG indicators for the same-score selector
  diagnostic.
- `selector_on_public_scores_unmarked_pressure.tsv`: companion unmarked
  same-family pressure summary for the same-score selector diagnostic.
- `selector_on_public_scores_status.json`: input paths and scope boundary for
  the same-score selector diagnostic.
- `r3_skill_summary.tsv`: aggregate metrics for the public R3-Skill
  embedding+reranker baseline over the fixed SameCapRisk pools.
- `r3_skill_per_query.tsv`: per-query Recall/HSR/CleanHit indicators for the
  R3-Skill baseline.
- `r3_skill_top20.tsv`: mapped top-20 candidate rows from the R3-Skill baseline.
- `r3_skill_status.json`: R3-Skill repo/model revisions, input hashes, and
  run boundary.
- `bge_reranker_two_stage_summary.tsv`: aggregate metrics for a generic
  BGE-M3 dense top-20 retrieval stage followed by a BGE reranker.
- `bge_reranker_two_stage_per_query.tsv`: per-query Recall/HSR/CleanHit
  indicators for the BGE reranker diagnostic.
- `bge_reranker_two_stage_top20.tsv`: reranked top-20 candidate rows used for
  the BGE reranker diagnostic.
- `bge_reranker_two_stage_status.json`: model, protocol, metric, and boundary
  metadata for the BGE reranker diagnostic.
- `open_llm_listwise_summary.tsv`: aggregate metrics for Qwen2.5-7B-Instruct
  listwise reranking over public BGE-M3 dense top-20 candidates. The diagnostic
  uses only query text and skill text, with no family labels or helpful/risky
  labels.

The controlled reference-interface resolver sensitivity rows reported in the
main paper are stored separately at
`../../reports/table3_family_source_reference.tsv`, because they vary the
family source inside the reference pipeline rather than post-processing public
score orders.

Boundary: these rows are post-processing diagnostics. They do not change the
benchmark labels, fixed candidate pools, or main-table protocol. Same-score
selector rows use the released family relation and therefore test the selector
effect on each public score order; public family-source rows show how
marked-sibling exposure changes without released family labels for RRF,
SkillRouter, SkillRet, and R3-Skill. R3-Skill is a public skill-routing
baseline and is included in the main result surface. The generic BGE reranker
and Qwen2.5-7B listwise diagnostics show that stronger neural reranking can
improve helpful recall while leaving same-capability exposure high. These
diagnostics remain separated from the controlled-family reference pipeline
reported in the main table.
