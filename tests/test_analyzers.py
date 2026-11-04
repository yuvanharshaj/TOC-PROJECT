"""
TOC SET-E Case Study: Comprehensive Test Suite for Log Analyzers
Course Code: 24CS52 — Theory of Computations (2026–2027)

Module: tests/test_analyzers.py
Description:
    Exhaustive unit and cross-implementation test suite validating:
    1. Regular Expression Analyzer (src/re_analyzer.py):
       - All five patterns: Date, Time, IPv4, ERROR, WARNING.
       - Expected match values, counts, and zero-based half-open spans [start:end).
       - Valid inputs, invalid ranges, and boundary safeguard behavior.
    2. Deterministic Finite Automaton Scanner (src/dfa_analyzer.py):
       - Exact whole-word recognition matching \\bERROR\\b semantics.
       - Verification that 're' module is strictly not imported or used.
       - Positive delimiters, negative prefix/suffix traps, stream boundary conditions.
    3. Cross-Implementation Equivalence:
       - 1:1 parity between RE and DFA ERROR match values and spans on data/sample.log
         and edge-case synthetic test vectors.
"""

import ast
from pathlib import Path
import sys
import unittest

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.re_analyzer import REAnalyzer
from src.dfa_analyzer import DFAErrorScanner


class TestREAnalyzerPatterns(unittest.TestCase):
    """
    Validates individual regular expression patterns implemented in REAnalyzer.
    """

    @classmethod
    def setUpClass(cls):
        cls.analyzer = REAnalyzer()

    # --- 1. Date Pattern Tests (DD-MM-YYYY) ---

    def test_date_valid_samples(self):
        text = "Start 15-03-2026 mid 01-01-2027 end 31-12-2025."
        results = self.analyzer.analyze_text(text)["Date (DD-MM-YYYY)"]
        values = [m.value for m in results]
        spans = [(m.start_offset, m.end_offset) for m in results]

        self.assertEqual(values, ["15-03-2026", "01-01-2027", "31-12-2025"])
        self.assertEqual(spans, [(6, 16), (21, 31), (36, 46)])

    def test_date_invalid_and_boundaries(self):
        # Invalid day > 31, invalid month > 12, day 00, month 00, non-hyphen
        invalid_text = (
            "32-01-2026 15-13-2026 00-05-2026 15-00-2026 15/03/2026 2026-03-15"
        )
        results = self.analyzer.analyze_text(invalid_text)["Date (DD-MM-YYYY)"]
        self.assertEqual(results, [], "Invalid date values should not produce matches")

    def test_date_digit_boundary_guards(self):
        # Lookbehind (?<!\d) and lookahead (?!\d) prevent matching inside larger digit strings
        boundary_text = "115-03-2026 15-03-20261 9915-03-202699"
        results = self.analyzer.analyze_text(boundary_text)["Date (DD-MM-YYYY)"]
        self.assertEqual(results, [], "Dates embedded within adjacent digits must be rejected")

    def test_date_documented_limitation(self):
        # Pattern enforces DD in 01-31 and MM in 01-12, but does not validate month days / leap years
        # As documented in SET-E requirements, '31-02-2026' matches syntax.
        text = "Event on 31-02-2026 recorded."
        results = self.analyzer.analyze_text(text)["Date (DD-MM-YYYY)"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].value, "31-02-2026")

    # --- 2. Time Pattern Tests (HH:MM) ---

    def test_time_valid_samples(self):
        text = "Times: 00:00, 08:30, 14:15, and 23:59."
        results = self.analyzer.analyze_text(text)["Time (HH:MM)"]
        values = [m.value for m in results]
        spans = [(m.start_offset, m.end_offset) for m in results]

        self.assertEqual(values, ["00:00", "08:30", "14:15", "23:59"])
        self.assertEqual(spans, [(7, 12), (14, 19), (21, 26), (32, 37)])

    def test_time_invalid_and_boundaries(self):
        # Invalid hour >= 24, invalid min >= 60, single digits, attached digits
        invalid_text = "24:00 25:10 12:60 12:65 8:30 08:3 108:00 08:001"
        results = self.analyzer.analyze_text(invalid_text)["Time (HH:MM)"]
        self.assertEqual(results, [], "Invalid time values or embedded digits must not match")

    # --- 3. IPv4 Pattern Tests ---

    def test_ipv4_valid_samples(self):
        text = "Hosts: 192.168.1.1, 10.0.0.25, 172.16.4.102, 127.0.0.1, 255.255.255.0, 0.0.0.0"
        results = self.analyzer.analyze_text(text)["IPv4 Address"]
        values = [m.value for m in results]

        expected = [
            "192.168.1.1",
            "10.0.0.25",
            "172.16.4.102",
            "127.0.0.1",
            "255.255.255.0",
            "0.0.0.0",
        ]
        self.assertEqual(values, expected)

    def test_ipv4_invalid_and_boundaries(self):
        # Octet > 255, 5 octets, 3 octets, adjacent dots
        invalid_text = "999.300.500.1 10.256.0.1 192.168.1.256 1.2.3.4.5 192.168.1 10..0.1"
        results = self.analyzer.analyze_text(invalid_text)["IPv4 Address"]
        self.assertEqual(results, [], "Invalid IPv4 octets or boundary violations must not match")

    def test_ipv4_trailing_sentence_period_safeguard(self):
        # Lookahead (?![\d.]) correctly rejects if dot is immediately adjacent to the 4th octet
        text_with_dot = "Check IP 192.168.1.1. Done."
        results = self.analyzer.analyze_text(text_with_dot)["IPv4 Address"]
        self.assertEqual(results, [], "IP followed immediately by dot violates boundary guard")

        text_with_space = "Check IP 192.168.1.1 on lan."
        results_space = self.analyzer.analyze_text(text_with_space)["IPv4 Address"]
        self.assertEqual(len(results_space), 1)
        self.assertEqual(results_space[0].value, "192.168.1.1")

    # --- 4. ERROR and WARNING Keyword Tests (RE) ---

    def test_error_keyword_valid_and_boundaries(self):
        text = "ERROR [ERROR] ERROR: (ERROR) ERRORS MYERROR NOERROR ERROR_CODE"
        results = self.analyzer.analyze_text(text)["ERROR Keyword"]
        values = [m.value for m in results]
        spans = [(m.start_offset, m.end_offset) for m in results]

        self.assertEqual(values, ["ERROR", "ERROR", "ERROR", "ERROR"])
        self.assertEqual(spans, [(0, 5), (7, 12), (14, 19), (22, 27)])

    def test_error_keyword_case_sensitivity(self):
        text = "error Error ErRoR eRROR"
        results = self.analyzer.analyze_text(text)["ERROR Keyword"]
        self.assertEqual(results, [], "Keyword ERROR matching must be strictly uppercase")

    def test_warning_keyword_valid_and_boundaries(self):
        text = "WARNING [WARNING] WARNING: PREWARNING WARNINGS WARNING_FLAG"
        results = self.analyzer.analyze_text(text)["WARNING Keyword"]
        values = [m.value for m in results]
        spans = [(m.start_offset, m.end_offset) for m in results]

        self.assertEqual(values, ["WARNING", "WARNING", "WARNING"])
        self.assertEqual(spans, [(0, 7), (9, 16), (18, 25)])

    def test_empty_and_neutral_inputs(self):
        results_empty = self.analyzer.analyze_text("")
        for name, match_list in results_empty.items():
            self.assertEqual(match_list, [], f"Pattern {name} must have 0 matches on empty input")

        results_neutral = self.analyzer.analyze_text("Generic maintenance task running peacefully.")
        for name, match_list in results_neutral.items():
            self.assertEqual(match_list, [], f"Pattern {name} must have 0 matches on neutral text")


class TestDFAErrorScanner(unittest.TestCase):
    """
    Validates manual Deterministic Finite Automaton implementation.
    """

    @classmethod
    def setUpClass(cls):
        cls.scanner = DFAErrorScanner()

    def test_dfa_does_not_import_or_use_re_library(self):
        """
        Statically and dynamically verifies that src/dfa_analyzer.py does not
        import Python's 're' module or any regex library.
        """
        # 1. AST verification of source code
        dfa_file = PROJECT_ROOT / "src" / "dfa_analyzer.py"
        self.assertTrue(dfa_file.is_file(), "src/dfa_analyzer.py missing")

        tree = ast.parse(dfa_file.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.assertNotEqual(alias.name, "re", "DFA module must not import 're'")
                    self.assertFalse(alias.name.startswith("regex"), "DFA module must not import 'regex'")
            elif isinstance(node, ast.ImportFrom):
                self.assertNotEqual(node.module, "re", "DFA module must not import from 're'")
                self.assertFalse(
                    node.module is not None and node.module.startswith("regex"),
                    "DFA module must not import from 'regex'",
                )

        # 2. Module namespace check
        import src.dfa_analyzer as dfa_module
        self.assertNotIn("re", dfa_module.__dict__, "'re' symbol found in dfa_analyzer namespace")

    def test_dfa_positive_delimiters(self):
        text = "ERROR [ERROR] (ERROR) {ERROR} <ERROR> ERROR: ERROR, ERROR! 'ERROR' \"ERROR\""
        matches = self.scanner.scan_text(text)
        self.assertEqual(len(matches), 10)
        for m in matches:
            self.assertEqual(m.value, "ERROR")

    def test_dfa_rejected_word_boundaries(self):
        # Letters, digits, and underscores attached to prefix or suffix must reject
        reject_cases = [
            "ERRORS",
            "ERROR_CODE",
            "ERROR1",
            "ERROR7",
            "XERROR",
            "MYERROR",
            "NOERROR",
            "_ERROR",
            "7ERROR",
            "error",
            "Error",
            "ERRORERROR",
        ]
        for token in reject_cases:
            matches = self.scanner.scan_text(token)
            self.assertEqual(
                matches,
                [],
                f"DFA must reject '{token}' as a whole-word match",
            )

    def test_dfa_stream_positions(self):
        # Start of text
        m_start = self.scanner.scan_text("ERROR at the beginning")
        self.assertEqual(len(m_start), 1)
        self.assertEqual((m_start[0].start_offset, m_start[0].end_offset), (0, 5))

        # End of text (EOF boundary check)
        m_end = self.scanner.scan_text("at the end ERROR")
        self.assertEqual(len(m_end), 1)
        self.assertEqual((m_end[0].start_offset, m_end[0].end_offset), (11, 16))

        # Both start and end
        m_both = self.scanner.scan_text("ERROR middle ERROR")
        self.assertEqual(len(m_both), 2)
        self.assertEqual(
            [(m.start_offset, m.end_offset) for m in m_both],
            [(0, 5), (13, 18)],
        )

    def test_dfa_multiline_coordinates(self):
        text = "First line OK\nSecond line ERROR here\nThird line"
        matches = self.scanner.scan_text(text)
        self.assertEqual(len(matches), 1)
        m = matches[0]

        # Verify 1-based Line & Col
        self.assertEqual(m.line_number, 2)
        self.assertEqual(m.column_number, 13)
        self.assertEqual(m.start_offset, 26)
        self.assertEqual(m.end_offset, 31)
        self.assertEqual(m.value, "ERROR")

    def test_dfa_empty_and_whitespace_input(self):
        self.assertEqual(self.scanner.scan_text(""), [])
        self.assertEqual(self.scanner.scan_text("   \t  \n  "), [])


class TestCrossImplementationValidation(unittest.TestCase):
    """
    Validates 1:1 cross-implementation parity between Regular Expression
    and Deterministic Finite Automaton on identical inputs.
    """

    @classmethod
    def setUpClass(cls):
        cls.re_analyzer = REAnalyzer()
        cls.dfa_scanner = DFAErrorScanner()

    def test_parity_on_sample_log(self):
        sample_path = PROJECT_ROOT / "data" / "sample.log"
        self.assertTrue(sample_path.is_file(), f"sample.log missing at {sample_path}")

        content = sample_path.read_text(encoding="utf-8")

        # RE ERROR matches
        re_matches = self.re_analyzer.analyze_text(content)["ERROR Keyword"]
        # DFA ERROR matches
        dfa_matches = self.dfa_scanner.scan_text(content)

        # 1. Total occurrence count agreement
        self.assertEqual(
            len(re_matches),
            len(dfa_matches),
            f"Occurrence count mismatch: RE={len(re_matches)}, DFA={len(dfa_matches)}",
        )
        self.assertEqual(len(re_matches), 7, "Expected exactly 7 occurrences in sample.log")

        # 2. Field-by-field spatial coordinate agreement
        for idx, (re_m, dfa_m) in enumerate(zip(re_matches, dfa_matches), 1):
            with self.subTest(match_index=idx):
                self.assertEqual(
                    re_m.value,
                    dfa_m.value,
                    f"Match {idx} value mismatch: RE='{re_m.value}' vs DFA='{dfa_m.value}'",
                )
                self.assertEqual(
                    re_m.start_offset,
                    dfa_m.start_offset,
                    f"Match {idx} start offset mismatch at span",
                )
                self.assertEqual(
                    re_m.end_offset,
                    dfa_m.end_offset,
                    f"Match {idx} end offset mismatch at span",
                )
                self.assertEqual(
                    re_m.line_number,
                    dfa_m.line_number,
                    f"Match {idx} line number mismatch",
                )
                self.assertEqual(
                    re_m.column_number,
                    dfa_m.column_number,
                    f"Match {idx} column number mismatch",
                )

    def test_parity_on_synthetic_boundary_matrix(self):
        """
        Evaluates RE and DFA across a diverse matrix of positive, negative,
        and boundary test strings.
        """
        test_strings = [
            "ERROR",
            "[ERROR]",
            "(ERROR)",
            "ERROR:",
            "ERROR_",
            "_ERROR",
            "ERROR7",
            "7ERROR",
            "ERRORS",
            "XERROR",
            "error",
            "MYERROR",
            "NOERROR",
            "ERROR_CODE",
            "ERRORERROR",
            "ERROR\nERROR",
            "ERROR and then ERROR",
            "Line 1: ERROR\nLine 2: OK\nLine 3: ERROR",
            "No problems detected on this host.",
            "",
            "   ",
        ]

        for s in test_strings:
            with self.subTest(input_text=s):
                re_m = self.re_analyzer.analyze_text(s)["ERROR Keyword"]
                dfa_m = self.dfa_scanner.scan_text(s)

                re_spans = [(m.value, m.start_offset, m.end_offset) for m in re_m]
                dfa_spans = [(m.value, m.start_offset, m.end_offset) for m in dfa_m]

                self.assertEqual(
                    re_spans,
                    dfa_spans,
                    f"RE and DFA diverged on input {s!r}: RE={re_spans}, DFA={dfa_spans}",
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)

