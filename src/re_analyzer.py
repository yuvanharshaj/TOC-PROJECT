"""
TOC SET-E Case Study: Log File Analysis Using Regular Expressions and DFA
Course Code: 24CS52 — Theory of Computations (2026–2027)

Module: src/re_analyzer.py
Description:
    Analyzes system log files using Python's standard `re` module across
    five formally defined regular expression patterns:
      1. Date in DD-MM-YYYY format
      2. Time in HH:MM format (24-hour clock)
      3. IPv4 addresses (with complete boundary and octet bounds)
      4. Keyword ERROR (word-boundary delimited)
      5. Keyword WARNING (word-boundary delimited)

Theoretical Background (Module 2 of Syllabus):
    A regular expression defines a regular language L(R) that can be
    recognized by a Finite Automaton. In practical engines (Python `re`),
    extended capabilities such as non-capturing groups (?:...), zero-width
    word boundaries (\\b), and negative lookaround assertions ((?<!...) and (?!...))
    are utilized to prevent partial/substring matching inside larger tokens.
"""

from dataclasses import dataclass
from pathlib import Path
import re
import sys
import time
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class MatchRecord:
    """
    Encapsulates a single pattern match along with precise spatial metadata.
    
    Attributes:
        pattern_name: The descriptive label of the target pattern.
        value: The exact matched substring.
        start_offset: Zero-based start character offset in the input stream.
        end_offset: Zero-based end character offset (exclusive) in the input stream.
        line_number: One-based line index in the source file.
        column_number: One-based column offset from the start of the line.
        line_text: The complete text of the line containing the match (trimmed).
    """
    pattern_name: str
    value: str
    start_offset: int
    end_offset: int
    line_number: int
    column_number: int
    line_text: str


class REAnalyzer:
    """
    Engine for executing multi-pattern log analysis using regular expressions.
    """

    # Formally specified regular expressions with exact boundary protection
    PATTERNS: Dict[str, str] = {
        "Date (DD-MM-YYYY)": (
            r"(?<!\d)(?:0[1-9]|[12]\d|3[01])-(?:0[1-9]|1[0-2])-\d{4}(?!\d)"
        ),
        "Time (HH:MM)": (
            r"(?<!\d)(?:[01]\d|2[0-3]):[0-5]\d(?!\d)"
        ),
        "IPv4 Address": (
            r"(?<![\d.])(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)"
            r"(?:\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}(?![\d.])"
        ),
        "ERROR Keyword": (
            r"\bERROR\b"
        ),
        "WARNING Keyword": (
            r"\bWARNING\b"
        ),
    }

    def __init__(self) -> None:
        """Compiles regex patterns ahead of time for deterministic execution."""
        self.compiled_patterns = {
            name: re.compile(raw_regex)
            for name, raw_regex in self.PATTERNS.items()
        }

    @staticmethod
    def _compute_line_col(text: str, offset: int) -> Tuple[int, int, str]:
        """
        Calculates 1-based line number, 1-based column number, and line text
        from a 0-based character offset.
        
        Args:
            text: The entire file contents string.
            offset: 0-based character index.
            
        Returns:
            Tuple of (line_number, column_number, line_text).
        """
        # Line number is count of preceding newlines + 1
        line_no = text.count("\n", 0, offset) + 1
        
        # Column number is offset relative to the immediately preceding newline
        last_nl = text.rfind("\n", 0, offset)
        col_no = (offset + 1) if last_nl == -1 else (offset - last_nl)
        
        # Extract full line string for display context
        line_start = 0 if last_nl == -1 else (last_nl + 1)
        next_nl = text.find("\n", offset)
        line_end = len(text) if next_nl == -1 else next_nl
        line_str = text[line_start:line_end].strip()

        return line_no, col_no, line_str

    def analyze_text(self, text: str) -> Dict[str, List[MatchRecord]]:
        """
        Scans input string against all five compiled patterns.
        
        Args:
            text: Source log text.
            
        Returns:
            Dictionary mapping pattern names to lists of MatchRecord instances.
        """
        results: Dict[str, List[MatchRecord]] = {}

        for name, compiled_regex in self.compiled_patterns.items():
            pattern_matches: List[MatchRecord] = []
            for match in compiled_regex.finditer(text):
                start, end = match.start(), match.end()
                val = match.group()
                line_no, col_no, line_str = self._compute_line_col(text, start)
                pattern_matches.append(
                    MatchRecord(
                        pattern_name=name,
                        value=val,
                        start_offset=start,
                        end_offset=end,
                        line_number=line_no,
                        column_number=col_no,
                        line_text=line_str,
                    )
                )
            results[name] = pattern_matches

        return results

    def analyze_file(
        self, filepath: str | Path
    ) -> Tuple[Dict[str, List[MatchRecord]], float, int]:
        """
        Reads a log file and executes analysis while measuring execution time.
        
        Args:
            filepath: Path to the log file.
            
        Returns:
            Tuple of (results_dict, execution_time_seconds, file_character_count).
        """
        path = Path(filepath)
        if not path.is_file():
            raise FileNotFoundError(f"Target log file not found: {path.resolve()}")

        with path.open("r", encoding="utf-8") as file_handle:
            content = file_handle.read()

        # High-resolution benchmark of pattern recognition
        start_time = time.perf_counter()
        results = self.analyze_text(content)
        elapsed_seconds = time.perf_counter() - start_time

        return results, elapsed_seconds, len(content)


def display_results(
    results: Dict[str, List[MatchRecord]],
    elapsed_seconds: float,
    char_count: int,
    file_path: str,
) -> None:
    """
    Prints an academic, structured report suitable for project demonstration.
    """
    total_matches = sum(len(m_list) for m_list in results.values())
    elapsed_ms = elapsed_seconds * 1000.0

    print("=" * 80)
    print("   THEORY OF COMPUTATIONS (24CS52) - CASE STUDY SET-E")
    print("   LOG FILE ANALYSIS ENGINE: REGULAR EXPRESSIONS IMPLEMENTATION")
    print("=" * 80)
    print(f"Target File         : {file_path}")
    print(f"File Size (Chars)   : {char_count} characters")
    print(f"Execution Benchmark : {elapsed_seconds:.6f} s ({elapsed_ms:.3f} ms)")
    print(f"Total Matches Found : {total_matches}")
    print("-" * 80)

    # 1. Summary Table
    print("\n[1] PATTERN SUMMARY TABLE:")
    print(f"{'#':<3} {'Pattern Name':<22} {'Matches':<9} {'Formal Regular Expression'}")
    print("-" * 80)
    for idx, (name, pattern_str) in enumerate(REAnalyzer.PATTERNS.items(), 1):
        count = len(results.get(name, []))
        print(f"{idx:<3} {name:<22} {count:<9} {pattern_str}")
    print("-" * 80)

    # 2. Detailed Match Listings
    print("\n[2] DETAILED EXTRACTION METRICS:")
    print("    Note: Character offset is 0-based. Line and Column numbers are 1-based.")
    print("-" * 80)

    for idx, (name, matches) in enumerate(results.items(), 1):
        print(f"\n>>> Pattern {idx}: {name} (Total Occurrences: {len(matches)})")
        if not matches:
            print("    (No occurrences identified)")
            continue

        header = (
            f"    {'#':<4} {'Matched Value':<18} "
            f"{'Char Span [start:end)':<22} {'Line:Col':<12} {'Sample Context'}"
        )
        print(header)
        print("    " + "-" * 74)

        for m_idx, m in enumerate(matches, 1):
            span_str = f"[{m.start_offset}:{m.end_offset})"
            line_col = f"L{m.line_number}:C{m.column_number}"
            # Truncate context snippet if long
            snippet = m.line_text
            if len(snippet) > 35:
                snippet = snippet[:32] + "..."
            print(
                f"    {m_idx:<4} {m.value:<18} "
                f"{span_str:<22} {line_col:<12} {snippet}"
            )

    print("\n" + "=" * 80)
    print("   REGULAR EXPRESSIONS ANALYSIS COMPLETED SUCCESSFULLY")
    print("=" * 80)


def main() -> None:
    """CLI Entry Point."""
    # Default file path
    target_path = Path("data/sample.log")
    if len(sys.argv) > 1:
        target_path = Path(sys.argv[1])

    analyzer = REAnalyzer()
    try:
        results, elapsed, char_count = analyzer.analyze_file(target_path)
        display_results(results, elapsed, char_count, str(target_path))
    except Exception as err:
        print(f"[ERROR] Execution failed: {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

