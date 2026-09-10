# Rank Output Schema

Tab-separated header:

`method_id query_case_id candidate_pool_id rank candidate_id score`

- one method per file set;
- all 1,327 query IDs exactly once as query groups;
- candidate pool and candidate ID must match the frozen input;
- ranks are unique consecutive integers from 1 through 20 per query;
- scores are finite numbers; returned row order does not override `rank`;
- files are UTF-8 and opened with `newline=''`.

