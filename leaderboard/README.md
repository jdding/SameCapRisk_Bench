# Leaderboard

The canonical table is [`results.tsv`](results.tsv). Every accepted result reports Recall@3, HSR@3, and CleanHit@3 on the fixed 1,258-query main comparison, with confidence intervals when available.

## Comparison Rule

Ranking is performed **within** an information setting:

- `public_text_only`: query and candidate text only;
- `public_text_cluster`: public text plus unsupervised text-derived grouping;
- `released_family_control`: uses the released structural relation and is a controlled diagnostic;
- `benchmark_trained`: uses benchmark labels or training folds and is diagnostic;
- `diagnostic_not_ranked`: auxiliary analyses not eligible for a main rank.

The default sort key is CleanHit@3, followed by Recall@3 and method ID for deterministic ties. A low HSR alone cannot win by returning irrelevant candidates.

## Result Status

`paper_frozen` means the row is reproduced from the paper's immutable result bundle. Community submissions will be marked `self_reported`, `metric_recomputed`, or `accepted`. Only `accepted` rows receive a rank; every row retains its code, checkpoint, rank-output, metric, and benchmark-version hashes in its submission record.

Do not compare rank numbers across settings. Released-family and benchmark-trained rows show diagnostic headroom, not directly deployable public-text performance.
