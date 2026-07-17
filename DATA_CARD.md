# Data Card

## Scope

SameCapRisk-Bench measures same-capability execution-risk exposure in agent
skill retrieval. A query can retrieve a relevant skill family while exposing a
query-inappropriate sibling skill.

## Current Scale

| Layer | Units | Query cases | Candidate rows |
|---|---:|---:|---:|
| Core marked-sibling | 694 | 694 | 8,048 |
| Hard role-flip | 496 | 992 | 992 |
| Total | 1,190 | 1,686 | 9,040 |

Candidate rows are summed across two separate evaluation pools. Core queries
rank 8,048 candidates and hard queries rank 992; no query ranks all 9,040 rows.

## Label Semantics

The label is query-relative. A skill is risky when exposing it for a specific
query would direct execution toward an inappropriate resource, precondition,
procedure, or evidence source. The hard stratum makes this explicit by using
role-flip units: the same two candidate skills swap helpful and risky roles
across paired queries.

## Release Split

The core stratum preserves its historical split metadata. The hard stratum is
a controlled hard slice and is reported as a stratum rather than as a natural
frequency sample.

## Reviewer Boundary

This release includes reviewer-visible data and paper-facing summary outputs.
Internal generation traces, detailed gate material, and raw gate transcripts
remain local-only provenance artifacts and are not part of this review surface.

The reviewer snapshot uses recovered complete queries for all 694 core cases
and refreshed query-dependent ranks. The historical 220-character excerpts
remain outside this package as provenance only.
