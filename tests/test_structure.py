import os

def test_expected_directories_exist():
    base = os.path.dirname(os.path.dirname(__file__))
    expected = ["data", "src", "docs", "reports", "models"]
    for d in expected:
        assert os.path.isdir(os.path.join(base, d))
