# Submit a Method Result

A result moves through five explicit states:

1. **Self-reported:** an issue supplies the method card and result archive.
2. **Schema-checked:** IDs, pools, ranks, hashes, and required metadata pass.
3. **Metric-recomputed:** maintainers reproduce metrics from submitted ranks.
4. **Setting-verified:** code/configuration, development use, and the declared information setting have been inspected.
5. **Accepted:** the result is added to the corresponding setting table with immutable code and rank hashes.

Prepare a directory containing:

```text
submission/
  method_card.json
  top20.tsv
  metrics.json
  adapter_receipt.json        # when the supplied adapter runner was used
```

Create `method_card.json` from `submission_templates/method_card.json`. Then run:

```bash
python scripts/validate_method_submission.py \
  --artifact ../samecaprisk_bench_v1.0 \
  --submission submission \
  --out submission/validation_receipt.json
```

The validator checks the card, rank hash, full query/pool coverage and score finiteness, recomputes all metric scopes, and compares the submitted metrics. A `METRIC_RECOMPUTED` receipt is an automated checkpoint, not leaderboard acceptance. It does not certify method novelty, absence of training leakage, the declared information setting, or external compute claims; maintainers inspect those separately.

Open the **Method result submission** issue and attach a ZIP of the validated directory. A PR should add only the small accepted method card, metric JSON, and receipt under `submissions/<method_id>/`; large rank files belong in a release or issue attachment and are bound by SHA-256. Results are ranked only within the same information setting.



Maintainers use this final checklist:

- the code URL and commit are immutable and sufficient to regenerate ranks;
- the checkpoint revision, prompts, preprocessing, truncation, reranking depth, and tie handling are declared;
- training data and benchmark development use are disclosed;
- the inference code does not read labels or metadata forbidden by the declared setting;
- the submitted ranks and recomputed metrics match their recorded hashes;
- results are placed in the correct setting table and show Recall, HSR, and CleanHit together.

Until the repository is opened, this procedure is locally executable but there is no public submission endpoint. The issue template becomes the intake form at anonymous or public release.
