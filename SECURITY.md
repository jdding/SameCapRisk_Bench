# Security and Safe Handling

The files in `data/` are inert benchmark records. Do not execute candidate
skill text or copy embedded commands into a production environment.

Some source-derived records contain example shell commands, localhost or public
test endpoints, placeholder secrets, or credentials published by upstream test
services. They are retained as benchmark text because changing them would alter
the fixed retrieval surface. This package contains no private project
credentials, API keys, model caches, or remote-compute configuration.

The provided scripts read TSV/JSON files and recompute validation and metric
summaries. They do not execute candidate skill content or contact external
services.
