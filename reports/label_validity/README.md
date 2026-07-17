# Label-Validity and Scope Check Summaries

This directory contains reviewer-visible summaries for the label-validity and
scope checks cited in the paper. Detailed non-public gate materials and local
construction workspaces are not included.

- `label_validity_summary.tsv`: compact counts for preference, verifier,
  SkillsBench, hard cue, and hard role-flip checks.
- `skillsbench_risk_sweep_summary.tsv`: aggregate SkillsBench verifier-backed
  risk-side sweep summary.
- `natural_validation/`: row-level admission metadata and funnel accounting for
  the model-screened natural-candidate validation companion. Raw model outputs,
  answer keys, and reasoning transcripts are not included.

Boundary: these summaries support label validity and metric scope. They are not
training data and do not change the fixed benchmark labels or ranked outputs.
The previous rewrite-stress and unmarked-risk estimates were not carried onto
the repaired query surface and are therefore excluded from this release.
The natural-validation companion establishes occurrence only; it is not a
prevalence estimate or natural HSR rate.
These summaries and the separate chooser proxy use different evidence units;
together they are complementary checks, not a case-level
retrieval-to-execution chain.
