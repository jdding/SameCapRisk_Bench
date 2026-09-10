from pathlib import Path


def test_readme_uses_existing_adapter_path():
    root = Path(__file__).resolve().parents[1]
    assert (root / 'scripts' / 'method_adapter_example.py').is_file()
    text = (root / 'README.md').read_text()
    assert '--adapter scripts/method_adapter_example.py' in text


def test_submission_states_are_not_conflated():
    root = Path(__file__).resolve().parents[1]
    text = (root / 'docs' / 'METHOD_SUBMISSION.md').read_text()
    assert 'METRIC_RECOMPUTED' in text
    assert 'not leaderboard acceptance' in text
