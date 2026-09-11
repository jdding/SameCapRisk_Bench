# Access and Release Status

| Surface | Current state | What it means |
|---|---|---|
| Benchmark research snapshot | Frozen | 940 units, 1,327 queries, splits and hashes are fixed for the paper |
| Evaluation code | Locally validated | Existing ranks can be checked and scored on CPU |
| Method-submission interface | Locally validated | A complete RRF submission was recomputed and accepted by the validator |
| Public project surface | Active | This repository is the public project homepage; the frozen benchmark bundle remains a gated release asset |
| Author-created code license | Apache-2.0 (granted 2026-09-11) | Covers author-created code, schemas, documentation, and leaderboard tables in this repository; third-party and upstream text is not relicensed (see docs/SOURCE_AND_LICENSES.md) |
| Full-text public release | Pending | Final third-party notices and CHAMP task-material distribution must be resolved |
| Community intake | Prepared locally | Issue/PR templates become active when the repository is opened |

The repository should publish code, schemas, project documentation, leaderboard records, and release manifests. The 259 MB benchmark/result bundle should be a versioned release asset, not normal Git history. Its manifest and SHA-256 must be shown on the release page and in this repository.

Before creating an anonymous link:

1. resolve or exclude/reconstruct material whose terms do not permit the chosen review distribution route;
2. rebuild the artifact, rerun hash/anonymity/metric checks, and record the final archive SHA-256;
3. add the real access URL and archive hash here without changing benchmark content or results;
4. download through the anonymous URL and rerun `scripts/validate_artifact.py`;
5. only then state in the paper or response that the artifact is inspectable.

