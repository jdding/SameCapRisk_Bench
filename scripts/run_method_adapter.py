#!/usr/bin/env python3
"""Run an external retriever against only the label-free inference surface."""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import math
from pathlib import Path

FIELDS = ['method_id', 'query_case_id', 'candidate_pool_id', 'rank', 'candidate_id', 'score']


def read_records(path: Path, identifier: str) -> list[dict]:
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    if not rows or any(set(row) != {identifier, 'text'} for row in rows):
        raise ValueError(f'Expected only {identifier} and text: {path.name}')
    if any(not isinstance(row[k], str) or not row[k].strip() for row in rows for k in (identifier, 'text')):
        raise ValueError('Empty or non-string input')
    if len({row[identifier] for row in rows}) != len(rows):
        raise ValueError('Duplicate input identifiers')
    return rows


def validate_output(selected: list, candidate_ids: set[str], k: int) -> list:
    selected = list(selected)
    if len(selected) != k:
        raise ValueError(f'Adapter must return {k} candidates')
    seen = set()
    for cid, score in selected:
        if cid not in candidate_ids or cid in seen or not math.isfinite(float(score)):
            raise ValueError('Unknown/duplicate candidate or non-finite score')
        seen.add(cid)
    return selected


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inference', type=Path, required=True)
    parser.add_argument('--adapter', type=Path, required=True)
    parser.add_argument('--method-id', required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    receipt = args.out.with_suffix('.receipt.json')
    if args.out.exists() or receipt.exists():
        raise ValueError('Choose a new output path; existing results are not overwritten')
    if not args.method_id.strip():
        raise ValueError('Empty method identifier')
    spec = importlib.util.spec_from_file_location('external_retriever', args.adapter)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    pools = sorted(p for p in args.inference.iterdir() if p.is_dir())
    if not pools:
        raise ValueError('No inference pools')
    inputs = {}
    rows = []
    seen_queries = set()
    for pool in pools:
        queries = read_records(pool / 'queries.jsonl', 'query_case_id')
        candidates = read_records(pool / 'candidates.jsonl', 'candidate_id')
        ids = {c['candidate_id'] for c in candidates}
        model = module.Retriever(candidates)
        for query in queries:
            qid = query['query_case_id']
            if qid in seen_queries:
                raise ValueError('Query belongs to more than one pool')
            seen_queries.add(qid)
            selected = validate_output(model.rank(query['text'], min(20, len(ids))), ids, min(20, len(ids)))
            for rank, (cid, score) in enumerate(selected, 1):
                rows.append(dict(zip(FIELDS, [args.method_id, qid, pool.name, rank, cid, float(score)])))
        for name in ('queries.jsonl', 'candidates.jsonl'):
            inputs[f'{pool.name}/{name}'] = hashlib.sha256((pool / name).read_bytes()).hexdigest()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.out.with_suffix(args.out.suffix + '.tmp')
    try:
        with temporary.open('w', newline='', encoding='utf-8') as handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDS, delimiter='\t')
            writer.writeheader()
            writer.writerows(rows)
        temporary.replace(args.out)
    finally:
        temporary.unlink(missing_ok=True)
    receipt.write_text(json.dumps({
        'schema': 'samecaprisk.method-run.v1', 'method_id': args.method_id,
        'queries': len(seen_queries), 'rank_rows': len(rows),
        'input_sha256': inputs,
        'adapter_sha256': hashlib.sha256(args.adapter.read_bytes()).hexdigest(),
        'rank_sha256': hashlib.sha256(args.out.read_bytes()).hexdigest(),
        'scope': 'Inference-only; run the frozen evaluator to verify version and metric scope.',
    }, indent=2) + '\n')
    print(f'Wrote {len(rows)} rank rows for {len(seen_queries)} queries')


if __name__ == '__main__':
    main()
