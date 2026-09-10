# Contribute Data or Validation Evidence

Data contribution is separate from leaderboard submission. A proposed unit must include the original query and source revision, helpful and conflicting skill text or exact spans, identical test conditions, one primary mechanism and one existing conflict type, and evidence bound to those exact versions.


Each proposal has one recorded state:

1. **Registered:** identity, source revision, and redistribution status are recorded.
2. **Source-bound:** the query and both candidate versions resolve to immutable source material.
3. **Contract-verified:** the query requirement, helpful behavior, and conflicting span satisfy the admission criteria below.
4. **Consequence-verified (optional):** an execution, checker, or matched computation demonstrates a downstream consequence.
5. **Admitted:** lineage, duplicate, cue, split, and release checks pass for a named future version.

Proposals can instead be **deferred** with a concrete missing requirement or **excluded** with a recorded reason. Consequence evidence strengthens a record but is not required when the local contract is statically decisive.


Maintainers apply the same six admission conditions as Benchmark 1.0:

1. the query states the tested requirement;
2. the helpful operation satisfies it;
3. the conflicting span violates it specifically;
4. both candidates use the same query, input, and criterion;
5. the taxonomy assignment follows the smallest corrective change;
6. all evidence resolves to the current record hashes.

Static evidence is sufficient only when it decides the local contract. Use a checker or computation when execution is needed to decide it. Full-agent failure is optional consequence evidence, not a requirement imposed retroactively on all units. Ambiguous proposals are deferred with a reason; counts or method scores never determine admission.

Open a **Data or label proposal** issue first. Do not post restricted source text, private data, or credentials. Accepted records still pass duplicate, lineage, cue, split, and license checks and enter a future version; Benchmark 1.0 remains immutable. A correction to v1.0 is released as a documented patch with old/new hashes rather than silently changing the artifact.

