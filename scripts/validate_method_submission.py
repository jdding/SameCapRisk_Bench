#!/usr/bin/env python3
"""Validate and recompute one SameCapRisk-Bench method submission."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

REQUIRED = {
    'schema', 'method_id', 'method_name', 'information_setting', 'code_url',
    'code_commit', 'checkpoint', 'training_data', 'development_use',
    'preprocessing', 'compute', 'rank_file', 'rank_sha256', 'metrics_file'
}
SETTINGS = {
    'public_text_only', 'public_text_cluster', 'released_family',
    'benchmark_trained', 'other_declared'
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_card(path: Path) -> dict:
    card = json.loads(path.read_text())
    missing = REQUIRED - set(card)
    if missing:
        raise ValueError('Missing method-card fields: ' + ', '.join(sorted(missing)))
    if card['schema'] != 'samecaprisk.method-card.v1':
        raise ValueError('Unsupported method-card schema')
    if card['information_setting'] not in SETTINGS:
        raise ValueError('Unknown information setting')
    for key in REQUIRED - {'schema'}:
        if not isinstance(card[key], str) or not card[key].strip():
            raise ValueError('Empty method-card field: ' + key)
    return card


def comparable(actual, submitted) -> bool:
    """Compare the scored content; paths and run receipts may differ."""
    return (actual.get('method_id') == submitted.get('method_id') and
            actual.get('gate_sha256') == submitted.get('gate_sha256') and
            actual.get('scopes') == submitted.get('scopes') and
            actual.get('main_breakdown') == submitted.get('main_breakdown') and
            actual.get('metric_definition') == submitted.get('metric_definition'))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--artifact', type=Path, required=True)
    parser.add_argument('--submission', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    card = load_card(args.submission / 'method_card.json')
    rank_path = args.submission / card['rank_file']
    metric_path = args.submission / card['metrics_file']
    if not rank_path.is_file() or not metric_path.is_file():
        raise ValueError('Rank or metric file is missing')
    if sha256(rank_path) != card['rank_sha256']:
        raise ValueError('Rank SHA-256 does not match method card')
    generated = args.submission / '.recomputed_metrics.json'
    if generated.exists():
        generated.unlink()
    command = [sys.executable, str(Path(__file__).with_name('evaluate_frozen_rankings.py')),
               '--inputs', str(args.artifact / 'benchmark'), '--ranks', str(rank_path),
               '--out', str(generated)]
    try:
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL)
        recomputed = json.loads(generated.read_text())
    finally:
        generated.unlink(missing_ok=True)
    submitted = json.loads(metric_path.read_text())
    if recomputed['method_id'] != card['method_id']:
        raise ValueError('Method ID differs across card and ranks')
    if not comparable(recomputed, submitted):
        raise ValueError('Submitted metrics do not match recomputation')
    adapter_receipt = args.submission / 'adapter_receipt.json'
    if adapter_receipt.exists():
        receipt = json.loads(adapter_receipt.read_text())
        if receipt.get('method_id') != card['method_id'] or receipt.get('rank_sha256') != card['rank_sha256']:
            raise ValueError('Adapter receipt does not bind the submitted rank file')
    artifact_manifest = args.artifact / 'PACKAGE_MANIFEST.json'
    result = {
        'schema': 'samecaprisk.method-submission-validation.v1',
        'status': 'METRIC_RECOMPUTED',
        'method_id': card['method_id'],
        'information_setting': card['information_setting'],
        'rank_sha256': card['rank_sha256'],
        'metrics_sha256': sha256(metric_path),
        'artifact_manifest_sha256': sha256(artifact_manifest),
        'benchmark_gate_sha256': recomputed['gate_sha256'],
        'checks': ['method_card', 'rank_hash', 'full_query_coverage', 'pool_membership',
                   'consecutive_unique_ranks', 'finite_scores', 'metric_recomputation'],
        'remaining_human_review': ['information_setting', 'training_overlap',
                                   'code_reproducibility', 'leaderboard_eligibility'],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    tmp = args.out.with_suffix(args.out.suffix + '.tmp')
    tmp.write_text(json.dumps(result, indent=2) + '\n')
    tmp.replace(args.out)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()

