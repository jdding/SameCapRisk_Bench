# Evaluation Protocol

The main evaluation reports helpful ranking and targeted risky-sibling exposure
on 1,686 query cases.

Core queries rank the 8,048-candidate public-pressure pool and hard queries rank
the 992-candidate role-flip pool. Aggregate rows are query-weighted across these
two surfaces, not rankings over a shared 9,040-candidate pool.

For each query case, systems rank a fixed candidate pool. The benchmark reports:

- `Recall@K`: whether the helpful skill appears in the top-K list.
- `NDCG@K`: graded helpful ranking quality.
- `HSR@K`: whether the marked risky sibling appears in the top-K list.

`HSR@K` is a targeted exposure certificate for the marked risky sibling. Broader
unmarked-candidate risk is measured separately by companion diagnostics.

The paper reports aggregate results and stratum diagnostics:

- aggregate over all 1,686 query cases;
- core marked-sibling diagnostics over 694 query cases;
- hard role-flip diagnostics over 992 query cases.

The current paper-facing rows are:

- Hybrid lexical RRF;
- SkillRouter;
- SkillRet;
- R3-Skill;
- Reference pipeline.

The reference pipeline is reported for the benchmarked within-family decision.
Its main result uses the released controlled family relation in
`data/family_relation.tsv` for one-representative selection. Its utility scorer
is stratum-specific: the core rows come from a five-fold grouped held-out
pairwise scorer, while the hard role-flip rows use the fixed label-free lexical
hybrid recorded as `reference_hybrid_hard_neutral`. No hard role label trains
or tunes that scorer. SkillRouter, SkillRet, and R3-Skill are public
retrieval/routing baselines and do not use SameCapRisk labels or family
relations during scoring.

The selector-certificate result compares the reference pipeline before and after
one-representative-per-family selection at K=3, K=5, and K=20.

Uncertainty estimates respect the construction unit. Clustered bootstrap and
paired sign tests operate over 1,190 benchmark units, keeping both query cases
of each hard role-flip unit together; reported point estimates remain weighted
over all 1,686 query cases.

Supplementary diagnostics in `results/diagnostics/` apply public metadata/title
or text-cluster family sources to public score orders. These rows test whether
exposure control still helps without released family-label access; they are
diagnostic post-processing rows, not main-table baselines.

To reproduce the paper-facing summaries, run `scripts/reproduce_results.py`
and `scripts/reproduce_family_source.py`.
It recomputes `results/main_table.tsv`, `results/extended_k20.tsv`,
`results/cutoff_sensitivity.tsv`, and `results/selector_certificate.tsv` from
the fixed rank files and selector-certificate cases. R3-Skill is reproduced
from the fixed R3 rank file in `results/diagnostics/r3_skill_per_query.tsv`;
the reviewer artifact does not rerun neural inference. The first script also
checks the released BGE and Qwen diagnostic rows from their 1,686 per-query
fixed-rank records; the second recomputes family-source sensitivity from 5,058
per-query indicators.
