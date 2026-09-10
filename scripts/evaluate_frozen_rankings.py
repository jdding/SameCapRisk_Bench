#!/usr/bin/env python3
"""Evaluate label-free frozen rankings after inference has completed."""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
from collections import defaultdict
from pathlib import Path

import run_frozen_public_baselines as frozen


KS = (1, 3, 5, 20)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline='', encoding='utf-8') as handle:
        return list(csv.DictReader(handle, delimiter='\t'))


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else float('nan')


def rounded(value: float) -> float | None:
    return None if not math.isfinite(value) else round(value, 9)


def metric_vectors(cases: list[dict], ranked: dict[str, list[str]]) -> dict[str, list[float]]:
    out: dict[str, list[float]] = defaultdict(list)
    for case in cases:
        ids = ranked[case['query_case_id']]
        for k in KS:
            top = ids[:k]
            hit = float(case['helpful_skill_id'] in top)
            exposed = float(case['risky_sibling_id'] in top)
            out[f'recall_at_{k}'].append(hit)
            out[f'hsr_at_{k}'].append(exposed)
            out[f'cleanhit_at_{k}'].append(hit * (1.0 - exposed))
    return out


def aggregate(cases: list[dict], ranked: dict[str, list[str]]) -> dict:
    vectors = metric_vectors(cases, ranked)
    query_micro = {key: rounded(mean(values)) for key, values in vectors.items()}
    by_unit: dict[str, list[dict]] = defaultdict(list)
    for case in cases:
        by_unit[case['unit_id']].append(case)
    unit_values: dict[str, list[float]] = defaultdict(list)
    for unit_cases in by_unit.values():
        unit_vectors = metric_vectors(unit_cases, ranked)
        for key, values in unit_vectors.items():
            unit_values[key].append(mean(values))
    unit_macro = {key: rounded(mean(values)) for key, values in unit_values.items()}
    result = {'queries': len(cases), 'units': len(by_unit),
              'query_micro': query_micro, 'unit_macro': unit_macro}
    if cases and all(case['stratum'] == 'hard_role_flip' for case in cases):
        paired = {}
        for k in KS:
            hit, clean = [], []
            for unit_cases in by_unit.values():
                hit.append(float(all(case['helpful_skill_id'] in ranked[case['query_case_id']][:k]
                                     for case in unit_cases)))
                clean.append(float(all(case['helpful_skill_id'] in ranked[case['query_case_id']][:k]
                                       and case['risky_sibling_id'] not in ranked[case['query_case_id']][:k]
                                       for case in unit_cases)))
            paired[f'paired_recall_at_{k}'] = rounded(mean(hit))
            paired[f'paired_cleanhit_at_{k}'] = rounded(mean(clean))
        result['paired_unit_success'] = paired
    return result


def grouped(cases: list[dict], ranked: dict[str, list[str]], field: str) -> dict:
    groups: dict[str, list[dict]] = defaultdict(list)
    for case in cases:
        groups[case[field]].append(case)
    return {key: aggregate(value, ranked) for key, value in sorted(groups.items())}


def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    with tmp.open('w', encoding='utf-8') as handle:
        json.dump(value, handle, sort_keys=True, indent=2)
        handle.write('\n')
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--inputs', type=Path, required=True)
    parser.add_argument('--ranks', type=Path, action='append', required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()

    pools = frozen.load_inputs(args.inputs)
    rows = [row for path in args.ranks for row in read_tsv(path)]
    if not rows:
        raise RuntimeError('No rank rows')
    methods = {row['method_id'] for row in rows}
    if len(methods) != 1:
        raise RuntimeError(f'Expected one method, got {sorted(methods)}')
    frozen.validate_ranks(rows, pools)
    ranked: dict[str, list[str]] = defaultdict(list)
    for row in sorted(rows, key=lambda item: (item['query_case_id'], int(item['rank']))):
        ranked[row['query_case_id']].append(row['candidate_id'])

    cases = read_tsv(args.inputs / 'data' / 'query_cases.tsv')
    if {case['query_case_id'] for case in cases} != set(ranked):
        raise RuntimeError('Label/ranking query coverage mismatch')
    main = [case for case in cases if case['main_evaluation'] == 'yes']
    if len(cases) != 1327 or len(main) != 1258:
        raise RuntimeError(f'Frozen query counts changed: all={len(cases)} main={len(main)}')
    core = [case for case in main if case['stratum'] == 'core_local_contract']
    hard = [case for case in main if case['stratum'] == 'hard_role_flip']
    development = [case for case in cases if case['split_role'] == 'development_only']

    result = {
        'schema': 'samecaprisk.frozen-evaluation.v1',
        'status': 'METRICS_COMPLETE',
        'method_id': next(iter(methods)),
        'gate_sha256': frozen.GATE_SHA,
        'rank_files': [{'path': str(path), 'sha256': frozen.sha(path)} for path in args.ranks],
        'scopes': {
            'main_comparison': aggregate(main, ranked),
            'main_core': aggregate(core, ranked),
            'main_hard': aggregate(hard, ranked),
            'all_query_census': aggregate(cases, ranked),
            'development_only': aggregate(development, ranked),
        },
        'main_breakdown': {
            'primary_category': grouped(main, ranked, 'primary_category'),
            'conflict_type': grouped(main, ranked, 'conflict_type'),
            'domain': grouped(main, ranked, 'domain'),
        },
        'metric_definition': {
            'recall_at_k': 'helpful skill occurs in top K',
            'hsr_at_k': 'marked risky sibling occurs in top K',
            'cleanhit_at_k': 'helpful occurs and marked risky sibling does not occur in top K',
            'unit_macro': 'average within each unit, then average across units',
        },
    }
    atomic_json(args.out, result)
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
