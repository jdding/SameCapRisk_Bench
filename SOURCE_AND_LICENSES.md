# Source and License Notes

This reviewer artifact combines author-created benchmark metadata with skill
texts from four public source layers. The fixed candidate table records a hash
for every redistributed text row; the counts below match
`data/candidate_pool.tsv`.

## Public Source Layers

| Source layer | Candidate rows | Upstream | Upstream terms |
|---|---:|---|---|
| SRA-Bench | 1,260 | `https://github.com/oneal2000/SR-Agents` | MIT |
| SkillsBench | 62 | `https://github.com/benchflow-ai/skillsbench` | Apache-2.0 |
| SWE-Skills-Bench | 66 | `https://github.com/GeniusHTX/SWE-Skills-Bench` | MIT |
| SkillRet public pressure pool | 6,660 | `https://huggingface.co/datasets/ThakiCloud/SKILLRET` | Apache-2.0 benchmark metadata; source skill documents are MIT or Apache-2.0 |

The source-license audit was refreshed on 2026-07-16 against repository HEADs
`277fd8d2bbd7d3b81a5cf4ffa6e87e18c7906e4f` (SRA-Bench),
`2d57f5c5199a50f986fa0ed8633812509662bd72` (SkillsBench),
`95b3ce519fcb58d0b19e90a5b6e5165211dc6dd1` (SWE-Skills-Bench), and
`7cae7cfbad2b0e1ebc9170892f568993aae543b0` (SkillRet). These commits document
the license audit time; row-level text hashes in this artifact, rather than the
current upstream HEAD, identify the evaluated snapshot.

## Author-Created Layer

The 992 hard-role-flip candidate rows, benchmark annotations, schemas,
validation summaries, and reproducer scripts were created for
SameCapRisk-Bench. They are supplied under the review-only terms in `LICENSE`.

## Redistribution Boundary

This package is intended for anonymous peer review and reproducibility
inspection. Third-party skill texts retain the upstream terms listed above.
The package is self-contained for review; the URLs are provenance and license
locators, not external substitutes for files required to check paper claims.

## Model Provenance

- SkillRouter baseline: public SkillRouter 0.6B embedding/reranker checkpoints
  adapted to the fixed candidate pools.
- SkillRet baseline: public SkillRet-Embedding-0.6B checkpoint.
- R3-Skill baseline: public R3-Embedding-0.6B and R3-Reranker-0.6B checkpoints
  with the official inference code, adapted without family/helpful/risky labels.
- Reference pipeline: a five-fold grouped held-out pairwise scorer for core and
  a fixed label-free lexical hybrid for hard role-flip cases, followed by the
  released controlled family relation and one-representative selection.

No model checkpoints, remote work directories, private caches, or raw gate
transcripts are redistributed. The artifact includes fixed per-query rank
outputs, result summaries, schemas, and CPU scripts for checking the reported
metrics.
