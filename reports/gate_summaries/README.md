# Hard-Stratum Gate Summaries

This directory contains sanitized reviewer-visible summaries for the 496
hard role-flip units. External review transcripts, hidden gate material,
and internal generation traces are local-only provenance artifacts and are not
part of this release surface.

- `hard_blind_gate_external_summary.json`: external query-blind static-cue gate.
- `hard_oracle_gate_external_summary.json`: external query-aware oracle gate.
- `hard_leakage_diversity_summary.json`: local leakage, template, duplication,
  and coverage audit.

The blind and oracle summaries retain the final external bulk-review row count
(`rows = 449`) and add release-level fields showing how the 496 hard units are
formed: 449 full naturalized-repair rows plus 47 earlier hard candidates that
were carried through the same clean gate-closure process.
