#!/usr/bin/env python3
"""Build setting-separated leaderboard rows from frozen expected metrics."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

MAIN = {
    'rrf', 'skillrouter_official', 'skillret_embedding_0_6b',
    'r3_skill_embedding_reranker', 'skillsight_qwen3_embedding_0_6b'
}
DISPLAY = {
    'rrf': 'RRF', 'skillrouter_official': 'SkillRouter',
    'skillret_embedding_0_6b': 'SkillRet',
    'r3_skill_embedding_reranker': 'R3-Skill',
    'skillsight_qwen3_embedding_0_6b': 'SkillSight'
}


def classify(method: str) -> tuple[str, str]:
    if method in MAIN:
        return 'public_text_only', DISPLAY[method]
    if method.endswith('__text_cluster_selector') and method.split('__')[0] in MAIN:
        base = method.split('__')[0]
        return 'public_text_cluster', DISPLAY[base] + ' + text cluster'
    if method.endswith('__released_family_selector') and method.split('__')[0] in MAIN:
        base = method.split('__')[0]
        return 'released_family_control', DISPLAY[base] + ' + released family'
    return 'diagnostic_not_ranked', method


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--metrics', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    with args.metrics.open(newline='') as handle:
        source = list(csv.DictReader(handle, delimiter='\t'))
    rows = []
    for row in source:
        setting, display = classify(row['method_id'])
        rows.append({'setting': setting, 'result_status': 'paper_frozen', 'display_name': display, **row})
    rows.sort(key=lambda row: (row['setting'], -float(row['cleanhit_at_3']), -float(row['recall_at_3']), row['method_id']))
    ranks = {}
    for row in rows:
        if row['setting'] == 'diagnostic_not_ranked':
            row['rank_within_setting'] = ''
        else:
            ranks[row['setting']] = ranks.get(row['setting'], 0) + 1
            row['rank_within_setting'] = str(ranks[row['setting']])
    fields = ['setting', 'rank_within_setting', 'result_status', 'display_name'] + list(source[0])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fields, delimiter='\t')
        writer.writeheader(); writer.writerows(rows)
    print(f'Wrote {len(rows)} rows across {len(set(row["setting"] for row in rows))} settings')


if __name__ == '__main__':
    main()

