# Skill Choice Task

You are given one user query and a small list of candidate skills. Choose the
single skill that should be used first.

Rules:

1. Use only the query and the candidate skill text.
2. Do not assume hidden labels, answer keys, or hidden grouping metadata.
3. Prefer the skill whose procedure, resources, preconditions, and artifact
   target fit the query.
4. Return exactly one JSON object:

```json
{"case_id":"<case_id>","selected_display_id":"<candidate display id>","rationale_short":"<one sentence>","confidence":"low|medium|high"}
```

Case:

```json
<CASE_JSON_WITHOUT_ANSWER_KEY>
```
