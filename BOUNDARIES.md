# Boundaries

## What This Package Is

This is the 2026-07-17 frozen reviewer-visible SameCapRisk-Bench release surface for the
1,190-unit / 1,686-query-case benchmark. All 694 core queries and their
query-dependent ranks use the recovered complete query surface; schema,
fixed-rank, selector, and uncertainty checks pass.

## What This Package Is Not

- It is not a full model-training release.
- It does not include local model caches, remote compute work directories, or private
  generation traces.
- It does not include raw gate transcripts or internal construction traces.
- It does not supersede the 694-unit core package as provenance; it builds on
  it as a core stratum.
- Its natural-candidate, verifier, and chooser checks are complementary
  validity checks, not a linked retrieval-to-execution experiment.

## Historical Compatibility

the core compatibility source layer remains a compatibility package for the
694-unit core stratum. Current paper claims should use this current package and the
merged 1,190-unit evidence ledger.
