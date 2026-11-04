"""
Stage 3 Verification Test Suite: DFA Scanner for Keyword ERROR
Course Code: 24CS52 — Theory of Computations (2026–2027)

Validates:
1. Positive test cases: 'ERROR', '[ERROR]', 'ERROR:', multiple ERRORs.
2. Negative test cases: 'ERRORS', 'XERROR', 'error', 'ERROR_CODE', 'MYERROR', 'NOERROR'.
3. Boundary edge cases: Start of input, End of input, across newline boundaries, punctuation.
4. Equivalence against RE analyzer on 'data/sample.log':
   Matches, spans [start:end), lines, and columns must match 100%.
"""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.re_analyzer import REAnalyzer
from src.dfa_analyzer import DFAErrorScanner


def test_dfa_positive_and_negative_cases():
    scanner = DFAErrorScanner()

    test_vectors = [
        # (description, input_string, expected_match_values, expected_spans)
        ("1. Exact isolated keyword", "ERROR", ["ERROR"], [(0, 5)]),
        ("2. Brackets delimited", "[ERROR]", ["ERROR"], [(1, 6)]),
        ("3. Colon delimited", "ERROR:", ["ERROR"], [(0, 5)]),
        ("4. Suffix negative case", "ERRORS", [], []),
        ("5. Prefix negative case", "XERROR", [], []),
        ("6. Lowercase negative case", "error", [], []),
        ("7. Underscore negative case", "ERROR_CODE", [], []),
        ("8. Preceding keyword trap", "MYERROR", [], []),
        ("9. Multiple keywords separated", "ERROR and ERROR", ["ERROR", "ERROR"], [(0, 5), (10, 15)]),
        ("10. Start of input", "ERROR at start", ["ERROR"], [(0, 5)]),
        ("11. End of input", "at the end ERROR", ["ERROR"], [(11, 16)]),
        ("12. Across newlines", "Line1 ERROR\nERROR Line2", ["ERROR", "ERROR"], [(6, 11), (12, 17)]),
        ("13. Punctuation sandwich", "(***ERROR***)", ["ERROR"], [(4, 9)]),
        ("14. Empty string", "", [], []),
    ]

    print("=" * 80)
    print("   STAGE 3: DFA UNIT TEST SUITE (POSITIVE, NEGATIVE & BOUNDARIES)")
    print("=" * 80)
    all_passed = True

    for desc, text, expected_vals, expected_spans in test_vectors:
        records = scanner.scan_text(text)
        actual_vals = [r.value for r in records]
        actual_spans = [(r.start_offset, r.end_offset) for r in records]

        val_ok = actual_vals == expected_vals
        span_ok = actual_spans == expected_spans
        passed = val_ok and span_ok

        status = "PASS" if passed else "FAIL"
        if not passed:
            all_passed = False

        print(f"[{status}] {desc:<32} Input: {text!r:<20} -> Found: {actual_vals} Spans: {actual_spans}")

    print("-" * 80)
    print(f"DFA Unit Test Suite Status: {'ALL TESTS PASSED' if all_passed else 'FAILURES DETECTED'}")
    print("=" * 80 + "\n")
    assert all_passed, "Unit tests failed!"


def test_compare_dfa_and_re_on_sample_log():
    sample_path = Path("data/sample.log")
    assert sample_path.is_file(), f"Sample log missing: {sample_path}"

    with sample_path.open("r", encoding="utf-8") as f:
        content = f.read()

    # 1. Run RE Analyzer for ERROR Keyword
    re_analyzer = REAnalyzer()
    re_results = re_analyzer.analyze_text(content)
    re_error_matches = re_results["ERROR Keyword"]

    # 2. Run DFA Scanner
    dfa_scanner = DFAErrorScanner()
    dfa_matches = dfa_scanner.scan_text(content)

    print("=" * 80)
    print("   STAGE 3: RE vs DFA COMPARISON ON data/sample.log")
    print("=" * 80)
    print(f"RE ERROR Matches Count  : {len(re_error_matches)}")
    print(f"DFA ERROR Matches Count : {len(dfa_matches)}")
    print("-" * 80)

    count_match = len(re_error_matches) == len(dfa_matches)
    print(f"1. Occurrence Count Match   : {'PASS (Identical: ' + str(len(dfa_matches)) + ')' if count_match else 'FAIL'}")

    # Item by item comparison
    header = f"{'#':<4} {'RE Value':<10} {'DFA Value':<10} {'RE Span':<18} {'DFA Span':<18} {'Line:Col':<12} {'Status'}"
    print(header)
    print("-" * 80)

    items_match = True
    for idx, (re_m, dfa_m) in enumerate(zip(re_error_matches, dfa_matches), 1):
        re_span = f"[{re_m.start_offset}:{re_m.end_offset})"
        dfa_span = f"[{dfa_m.start_offset}:{dfa_m.end_offset})"
        re_lc = f"L{re_m.line_number}:C{re_m.column_number}"
        dfa_lc = f"L{dfa_m.line_number}:C{dfa_m.column_number}"

        match_ok = (
            re_m.value == dfa_m.value
            and re_m.start_offset == dfa_m.start_offset
            and re_m.end_offset == dfa_m.end_offset
            and re_m.line_number == dfa_m.line_number
            and re_m.column_number == dfa_m.column_number
        )

        if not match_ok:
            items_match = False

        status = "EQUAL" if match_ok else "MISMATCH"
        print(f"{idx:<4} {re_m.value:<10} {dfa_m.value:<10} {re_span:<18} {dfa_span:<18} {dfa_lc:<12} {status}")

    print("-" * 80)
    perfect_agreement = count_match and items_match
    print(f"Overall RE vs DFA Equivalence: {'PERFECT 100% AGREEMENT' if perfect_agreement else 'MISMATCH'}")
    print("=" * 80)
    assert perfect_agreement, "RE and DFA did not agree!"


if __name__ == "__main__":
    test_dfa_positive_and_negative_cases()
    test_compare_dfa_and_re_on_sample_log()

