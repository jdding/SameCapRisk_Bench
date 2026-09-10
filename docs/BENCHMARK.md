# Benchmark and Metrics

Benchmark 1.0 has two evaluation settings:

- **Single-query public pool:** 553 source-bound units and queries over 7,713 candidates; 69 units are development-only and 484 are held out.
- **Paired role exchange:** 387 units and 774 evaluation-only queries over 774 candidates. Each unit reverses the helpful/risky roles of two fixed skills across two queries.

Candidate pools are separate. Each query is evaluated only against its recorded pool. The released relation is a controlled structural partition formed from connected components of admitted sibling edges; unconnected background skills are singletons. It is not exhaustive semantic-family annotation of the library.

At K, Recall is one when the helpful skill occurs in the returned list; HSR is one when the marked query-conflicting sibling occurs; CleanHit is one when the helpful skill occurs without that sibling. Report all three at K=3, 5, and 20. The pooled query-micro result is the fixed leaderboard protocol, not an estimate of real-world prevalence. Also report both settings and supported conflict types.

Inference consumes only query/candidate IDs and full text. Labels and provenance are loaded only by the evaluator after ranking. See `benchmark/protocol.json` in the versioned artifact for exact counts, split rules, and information boundaries.

