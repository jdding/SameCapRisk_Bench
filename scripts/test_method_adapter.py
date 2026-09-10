import csv
import json
import subprocess
import sys
from pathlib import Path

import pytest

from run_method_adapter import read_records, validate_output

ROOT = Path(__file__).resolve().parent


@pytest.mark.parametrize('rows', [[('a', 1), ('a', 0)], [('a', 1), ('z', 0)],
                                  [('a', float('nan')), ('b', 0)], [('a', 1)]])
def test_reject_invalid_ranks(rows):
    with pytest.raises(ValueError):
        validate_output(rows, {'a', 'b'}, 2)


def test_reject_label_fields(tmp_path):
    path = tmp_path / 'queries.jsonl'
    path.write_text(json.dumps({'query_case_id': 'q', 'text': 'hello', 'helpful': 'a'}) + '\n')
    with pytest.raises(ValueError):
        read_records(path, 'query_case_id')


def test_end_to_end_and_no_overwrite(tmp_path):
    for pool in ('pool1', 'pool2'):
        directory = tmp_path / 'inference' / pool
        directory.mkdir(parents=True)
        (directory / 'queries.jsonl').write_text(json.dumps({'query_case_id': pool, 'text': 'map'}) + '\n')
        (directory / 'candidates.jsonl').write_text('\n'.join(json.dumps(r) for r in [
            {'candidate_id': 'a', 'text': 'map return'}, {'candidate_id': 'b', 'text': 'distance'}]) + '\n')
    out = tmp_path / 'ranks.tsv'
    command = [sys.executable, str(ROOT / 'run_method_adapter.py'), '--inference',
               str(tmp_path / 'inference'), '--adapter', str(ROOT / 'method_adapter_example.py'),
               '--method-id', 'example', '--out', str(out)]
    subprocess.run(command, check=True)
    with out.open(newline='') as handle:
        rows = list(csv.DictReader(handle, delimiter='\t'))
    assert len(rows) == 4
    assert rows[0]['candidate_id'] == 'a'
    assert json.loads(out.with_suffix('.receipt.json').read_text())['queries'] == 2
    assert subprocess.run(command, capture_output=True).returncode != 0
