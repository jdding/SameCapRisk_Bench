import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from validate_method_submission import comparable, load_card


def card():
    return {
        'schema': 'samecaprisk.method-card.v1', 'method_id': 'm', 'method_name': 'M',
        'information_setting': 'public_text_only', 'code_url': 'https://example.invalid',
        'code_commit': 'abc', 'checkpoint': 'none', 'training_data': 'none',
        'development_use': 'none', 'preprocessing': 'full text', 'compute': 'cpu',
        'rank_file': 'top20.tsv', 'rank_sha256': 'abc', 'metrics_file': 'metrics.json'}


def test_card_accepts_complete_record(tmp_path):
    path = tmp_path / 'card.json'; path.write_text(json.dumps(card()))
    assert load_card(path)['method_id'] == 'm'


def test_card_rejects_missing_and_unknown_setting(tmp_path):
    value = card(); del value['compute']
    path = tmp_path / 'card.json'; path.write_text(json.dumps(value))
    with pytest.raises(ValueError): load_card(path)
    value = card(); value['information_setting'] = 'labels_hidden_sort_of'
    path.write_text(json.dumps(value))
    with pytest.raises(ValueError): load_card(path)


def test_metric_comparison_ignores_paths_not_scopes():
    base = {'method_id': 'm', 'gate_sha256': 'g', 'scopes': {'x': 1},
            'main_breakdown': {'x': 2}, 'metric_definition': {'x': 3}}
    changed = {**base, 'rank_files': ['different/path']}
    assert comparable(base, changed)
    changed['scopes'] = {'x': 9}
    assert not comparable(base, changed)

