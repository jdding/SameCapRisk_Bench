#!/usr/bin/env python3
"""Check the small GitHub project surface before publishing it."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    'README.md', 'ARTIFACT_QUICKSTART.md', 'ACCESS_AND_RELEASE_STATUS.md', 'docs/BENCHMARK.md',
    'docs/METHOD_INTEGRATION.md', 'docs/METHOD_SUBMISSION.md',
    'docs/DATA_CONTRIBUTION.md', 'docs/SOURCE_AND_LICENSES.md',
    'leaderboard/README.md', 'leaderboard/results.tsv',
    'submission_templates/method_card.json',
    '.github/ISSUE_TEMPLATE/method_submission.yml',
    '.github/ISSUE_TEMPLATE/data_or_label.yml', '.github/workflows/ci.yml',
]


def main() -> None:
    missing = [name for name in REQUIRED if not (ROOT / name).is_file()]
    if missing:
        raise SystemExit('Missing project files: ' + ', '.join(missing))
    broken = []
    for md in ROOT.rglob('*.md'):
        for target in re.findall(r'\[[^]]+\]\(([^)]+)\)', md.read_text()):
            if '://' in target or target.startswith('#'):
                continue
            local = (md.parent / target.split('#', 1)[0]).resolve()
            if not local.exists():
                broken.append(f'{md.relative_to(ROOT)} -> {target}')
    if broken:
        raise SystemExit('Broken local links:\n' + '\n'.join(broken))
    forbidden = list(ROOT.rglob('query_cases.tsv')) + list(ROOT.rglob('*.safetensors'))
    if forbidden:
        raise SystemExit('Large/private artifact content entered Git tree: ' + ', '.join(map(str, forbidden)))
    print(f'PASS: {len(REQUIRED)} required files, local links, and Git/artifact separation')


if __name__ == '__main__':
    main()
