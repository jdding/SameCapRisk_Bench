# Chooser-Proxy Evidence

This directory supports the bounded chooser-proxy check in the technical
supplement. It is not an executor-level validation and is excluded from the
benchmark leaderboard.
It uses different evidence units from the natural-candidate and verifier
checks, so the three checks do not constitute a case-level
retrieval-to-execution chain.

The fixed Qwen2.5-7B-Instruct chooser receives a query and three displayed
skill texts without candidate identifiers, family labels, or helpful/risky
labels. Each paired effect compares an observed clean list with a risk-added
list that holds the query and other displayed candidates fixed.

Files:

- `chooser_prompt.md`: fixed chooser instruction.
- `r3_condition_summary.tsv` and `bge_condition_summary.tsv`: condition-level
  accounting for R3-Skill and BGE reranking source lists.
- `r3_paired_effects.tsv` and `bge_paired_effects.tsv`: one row per matched
  clean/risk-added pair.

Across the 24 core pairs for each source ranker, adding the marked risky sibling
changed the chooser's first selection to that sibling in 8 R3-Skill pairs and
10 BGE-reranking pairs. The corresponding 24 hard pairs produced no such
transition. One BGE risk-added response did not map to an offered display and
is retained as a parse failure in the condition table. Raw model transcripts,
private answer keys, and model weights are not included.
