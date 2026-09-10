# Run and Submit a Method

## 1. Fix the Input and Information Setting

Use the package's frozen `benchmark/inference/` directory. Each pool has
`queries.jsonl` (`query_case_id`, `text`) and `candidates.jsonl`
(`candidate_id`, `text`). The two pools are evaluated independently.
These are the only files a public text-only retriever may use at inference.
Do not load label, family, taxonomy, evidence, split, or source fields into the
retriever. The local package is not a security sandbox: keep inference and
evaluation separate yourself. Models that use released families or benchmark
training labels must declare that setting and cannot be called text-only.

The submission interface requests top 20 for all 1,327 queries so the unchanged
evaluator can report K=1,3,5,20 and development separately. Only 1,258 held-out
queries contribute to the main leaderboard. Do not tune on held-out labels.

## 2. Implement the Adapter

Copy `scripts/method_adapter_example.py` and replace its `Retriever` class:

```python
class Retriever:
    def __init__(self, candidates):
        # Build one index per pool. Each candidate has candidate_id and text.
        ...

    def rank(self, query, k):
        # Return k distinct (candidate_id, finite_score) pairs in best-first order.
        ...
```

Use complete text unless your method has a documented tokenizer/context limit.
Record all truncation, chunking, prompts, checkpoint revisions, and reranking
depth. Never shorten the benchmark query files themselves. The returned order
is authoritative; score values are recorded for inspection, not used to reorder.

```bash
python3 scripts/run_method_adapter.py \
  --inference benchmark/inference \
  --adapter scripts/method_adapter_example.py \
  --method-id my_method \
  --out my_results/top20.tsv
python3 scripts/evaluate_frozen_rankings.py \
  --inputs benchmark --ranks my_results/top20.tsv \
  --out my_results/metrics.json
```

The first command writes ranks and a hash receipt, and rejects malformed adapter
outputs. The second verifies the frozen inputs, all query IDs, pool membership,
unique candidates and ranks, complete coverage, and finite scores before scoring.
An independent runner can skip the adapter and produce the same TSV schema:

`method_id, query_case_id, candidate_pool_id, rank, candidate_id, score`

Fields are tab-separated; ranks are consecutive integers 1..20 per query.
One method per file set. To combine pool-specific files, repeat `--ranks`.

## 3. Inspect the Result

- `scopes.main_comparison`: held-out pooled query-micro and unit-macro metrics.
- `scopes.main_core`: 484 held-out single-query cases (legacy machine field name).
- `scopes.main_hard`: 774 paired-query cases (legacy machine field name).
- `scopes.development_only`: 69 development queries, never a main result.
- `main_breakdown`: primary mechanism, conflict type, and source/domain metrics.

Report Recall, HSR and CleanHit together, not HSR alone: an empty or irrelevant
list is not a useful retriever. Comparisons also depend on candidate depth and
the information setting. The supplied point-estimate evaluator does not generate
new confidence intervals; label those as uncomputed until a matched group-level
analysis is run.

## 4. Submit for Maintainer Review

Attach the rank TSV, metrics JSON, adapter receipt, and completed
`METHOD_CARD_TEMPLATE.md`, including source commit and checkpoint revision.
Provide code/config/environment sufficient to regenerate ranks, and disclose
compute, context limits, training data, development use, and external services.
Do not include credentials or private data. Maintainers verify input/rank hashes,
recompute metrics, confirm the information setting, and review reproducibility
before adding a result. Self-reported results remain marked as unverified.

There is no live submission endpoint yet. Once anonymous review access is
prepared, use its permitted communication channel; public GitHub contributions
must wait for the public release and its license disposition.
