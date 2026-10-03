from scanner.engine import scan_file

def test_scanner():
    result = scan_file("tests/sample_bad.py")
    assert result["total"] > 0
    assert result["counts"]["critical"] >= 1
