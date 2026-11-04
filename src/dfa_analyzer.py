"""
TOC SET-E Case Study: Log File Analysis Using Regular Expressions and DFA
Course Code: 24CS52 — Theory of Computations (2026–2027)

Module: src/dfa_analyzer.py
Description:
    Implements a formal Deterministic Finite Automaton (DFA) scanner to detect
    the keyword 'ERROR' with strict whole-word boundary semantics (equivalent
    to the regular expression \\bERROR\\b) WITHOUT importing or using Python's
    `re` module or any regular expression library.

Mathematical Formulation:
    M = (Q, Sigma, delta, q0, F)
    
    1. Q (States):
       - q0: Initial state / preceding character was a non-word delimiter (\\W).
       - q1: Recognized prefix 'E' preceded by a word boundary.
       - q2: Recognized prefix 'ER'.
       - q3: Recognized prefix 'ERR'.
       - q4: Recognized prefix 'ERRO'.
       - q5: Recognized keyword 'ERROR' (pre-accepting candidate awaiting boundary).
       - q_word: Inside a non-matching word token (trap/sink for current word).
       
    2. Sigma (Alphabet):
       All characters, partitioned into 5 mutually disjoint equivalence classes:
       - 'E': Character 'E'
       - 'R': Character 'R'
       - 'O': Character 'O'
       - 'OTHER_WORD': Any other alphanumeric character or underscore ([0-9a-df-np-qs-z_])
       - 'NON_WORD': Any non-word delimiter ([^a-zA-Z0-9_], e.g. whitespace, punctuation, brackets)

    3. delta (Transition Function):
       Rigorous 7-state x 5-class deterministic transition matrix.

    4. q0: Initial state.

    5. F (Accepting condition):
       In streaming text search (Hopcroft & Ullman Section 1.5 & 2.2),
       state q5 accepts and emits the matched token 'ERROR' whenever followed
       by a NON_WORD character or the End-Of-File (EOF).
"""

from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
import sys
import time
from typing import Dict, List, Optional, Tuple


@dataclass(frozen=True)
class DFAMatchRecord:
    """
    Encapsulates a single DFA pattern match along with spatial coordinates.
    
    Attributes:
        pattern_name: The descriptive label of the target pattern ('ERROR Keyword (DFA)').
        value: The exact matched token substring.
        start_offset: Zero-based start character offset in the stream.
        end_offset: Zero-based end character offset (exclusive, half-open interval).
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


class DFAState(str, Enum):
    """Formal states of the keyword recognition automaton."""
    Q0 = "q0"           # Initial / Word boundary
    Q1_E = "q1"         # Prefix 'E'
    Q2_ER = "q2"        # Prefix 'ER'
    Q3_ERR = "q3"       # Prefix 'ERR'
    Q4_ERRO = "q4"      # Prefix 'ERRO'
    Q5_ERROR = "q5"     # Candidate 'ERROR' matched
    Q_WORD = "q_word"   # Inside non-matching word


class CharClass(str, Enum):
    """Equivalence classes of the input alphabet."""
    E = "E"
    R = "R"
    O = "O"
    OTHER_WORD = "OTHER_WORD"
    NON_WORD = "NON_WORD"


class DFAErrorScanner:
    """
    Pure Deterministic Finite Automaton scanner for whole-word 'ERROR'.
    Strictly avoids any regular expression libraries.
    """

    # Complete transition table delta: Q x Sigma -> Q
    TRANSITION_TABLE: Dict[DFAState, Dict[CharClass, DFAState]] = {
        DFAState.Q0: {
            CharClass.E: DFAState.Q1_E,
            CharClass.R: DFAState.Q_WORD,
            CharClass.O: DFAState.Q_WORD,
            CharClass.OTHER_WORD: DFAState.Q_WORD,
            CharClass.NON_WORD: DFAState.Q0,
        },
        DFAState.Q1_E: {
            CharClass.E: DFAState.Q_WORD,
            CharClass.R: DFAState.Q2_ER,
            CharClass.O: DFAState.Q_WORD,
            CharClass.OTHER_WORD: DFAState.Q_WORD,
            CharClass.NON_WORD: DFAState.Q0,
        },
        DFAState.Q2_ER: {
            CharClass.E: DFAState.Q_WORD,
            CharClass.R: DFAState.Q3_ERR,
            CharClass.O: DFAState.Q_WORD,
            CharClass.OTHER_WORD: DFAState.Q_WORD,
            CharClass.NON_WORD: DFAState.Q0,
        },
        DFAState.Q3_ERR: {
            CharClass.E: DFAState.Q_WORD,
            CharClass.R: DFAState.Q_WORD,
            CharClass.O: DFAState.Q4_ERRO,
            CharClass.OTHER_WORD: DFAState.Q_WORD,
            CharClass.NON_WORD: DFAState.Q0,
        },
        DFAState.Q4_ERRO: {
            CharClass.E: DFAState.Q_WORD,
            CharClass.R: DFAState.Q5_ERROR,
            CharClass.O: DFAState.Q_WORD,
            CharClass.OTHER_WORD: DFAState.Q_WORD,
            CharClass.NON_WORD: DFAState.Q0,
        },
        DFAState.Q5_ERROR: {
            CharClass.E: DFAState.Q_WORD,
            CharClass.R: DFAState.Q_WORD,
            CharClass.O: DFAState.Q_WORD,
            CharClass.OTHER_WORD: DFAState.Q_WORD,
            CharClass.NON_WORD: DFAState.Q0,
        },
        DFAState.Q_WORD: {
            CharClass.E: DFAState.Q_WORD,
            CharClass.R: DFAState.Q_WORD,
            CharClass.O: DFAState.Q_WORD,
            CharClass.OTHER_WORD: DFAState.Q_WORD,
            CharClass.NON_WORD: DFAState.Q0,
        },
    }

    @staticmethod
    def classify_char(char: str) -> CharClass:
        """
        Maps an arbitrary character to its corresponding alphabet equivalence class.
        Word characters are alphanumeric characters and underscore: [0-9a-zA-Z_].
        """
        # Check if word character
        is_word = (
            ("a" <= char <= "z")
            or ("A" <= char <= "Z")
            or ("0" <= char <= "9")
            or (char == "_")
        )
        if not is_word:
            return CharClass.NON_WORD
        
        # Word character classification
        if char == "E":
            return CharClass.E
        if char == "R":
            return CharClass.R
        if char == "O":
            return CharClass.O
        return CharClass.OTHER_WORD

    @staticmethod
    def _compute_line_col(text: str, offset: int) -> Tuple[int, int, str]:
        """
        Calculates 1-based line number, 1-based column number, and line text
        from a 0-based character offset without using regex.
        """
        line_no = text.count("\n", 0, offset) + 1
        last_nl = text.rfind("\n", 0, offset)
        col_no = (offset + 1) if last_nl == -1 else (offset - last_nl)
        
        line_start = 0 if last_nl == -1 else (last_nl + 1)
        next_nl = text.find("\n", offset)
        line_end = len(text) if next_nl == -1 else next_nl
        line_str = text[line_start:line_end].strip()

        return line_no, col_no, line_str

    def scan_text(self, text: str) -> List[DFAMatchRecord]:
        """
        Executes character-by-character DFA text scanning across the input stream.
        
        Args:
            text: Raw input string to analyze.
            
        Returns:
            List of DFAMatchRecord instances representing confirmed occurrences.
        """
        matches: List[DFAMatchRecord] = []
        state = DFAState.Q0
        candidate_start: Optional[int] = None

        for index, char in enumerate(text):
            char_class = self.classify_char(char)

            # Pre-acceptance check for state Q5_ERROR:
            # We have recognized 'E-R-R-O-R'. The current character determines
            # whether this is a legitimate whole-word token or an extended word (e.g. ERRORS).
            if state == DFAState.Q5_ERROR:
                if char_class == CharClass.NON_WORD:
                    # Valid right boundary confirmed! Accept and emit match.
                    assert candidate_start is not None
                    line_no, col_no, line_str = self._compute_line_col(text, candidate_start)
                    matches.append(
                        DFAMatchRecord(
                            pattern_name="ERROR Keyword (DFA)",
                            value=text[candidate_start:index],
                            start_offset=candidate_start,
                            end_offset=index,
                            line_number=line_no,
                            column_number=col_no,
                            line_text=line_str,
                        )
                    )
                    candidate_start = None
                    state = DFAState.Q0
                else:
                    # Trailing character is a word character (e.g. 'S' in 'ERRORS')
                    # Word boundary condition violated; discard candidate and enter trap state.
                    candidate_start = None
                    state = DFAState.Q_WORD

            # Standard deterministic transition
            if state == DFAState.Q0 and char_class == CharClass.E:
                # Potential start of keyword 'ERROR' at a valid left boundary
                candidate_start = index
                state = DFAState.Q1_E
            else:
                next_state = self.TRANSITION_TABLE[state][char_class]
                if next_state == DFAState.Q0:
                    candidate_start = None
                state = next_state

        # Stream Termination / EOF Processing:
        # If the stream ends while in Q5_ERROR, EOF acts as a valid right boundary.
        if state == DFAState.Q5_ERROR and candidate_start is not None:
            end_index = len(text)
            line_no, col_no, line_str = self._compute_line_col(text, candidate_start)
            matches.append(
                DFAMatchRecord(
                    pattern_name="ERROR Keyword (DFA)",
                    value=text[candidate_start:end_index],
                    start_offset=candidate_start,
                    end_offset=end_index,
                    line_number=line_no,
                    column_number=col_no,
                    line_text=line_str,
                )
            )

        return matches

    def scan_file(
        self, filepath: str | Path
    ) -> Tuple[List[DFAMatchRecord], float, int]:
        """
        Reads a log file and executes DFA analysis with high-precision timing.
        """
        path = Path(filepath)
        if not path.is_file():
            raise FileNotFoundError(f"Target log file not found: {path.resolve()}")

        with path.open("r", encoding="utf-8") as file_handle:
            content = file_handle.read()

        start_time = time.perf_counter()
        matches = self.scan_text(content)
        elapsed_seconds = time.perf_counter() - start_time

        return matches, elapsed_seconds, len(content)


def display_dfa_results(
    matches: List[DFAMatchRecord],
    elapsed_seconds: float,
    char_count: int,
    file_path: str,
) -> None:
    """Prints a structured academic report of the DFA scan results."""
    elapsed_ms = elapsed_seconds * 1000.0

    print("=" * 80)
    print("   THEORY OF COMPUTATIONS (24CS52) - CASE STUDY SET-E")
    print("   LOG FILE ANALYSIS ENGINE: DETERMINISTIC FINITE AUTOMATON (DFA)")
    print("=" * 80)
    print(f"Target File         : {file_path}")
    print(f"File Size (Chars)   : {char_count} characters")
    print(f"Execution Benchmark : {elapsed_seconds:.6f} s ({elapsed_ms:.3f} ms)")
    print(f"Total Matches Found : {len(matches)}")
    print("-" * 80)

    print("\n[1] FORMAL 5-TUPLE DEFINITION M = (Q, Sigma, delta, q0, F):")
    print("    Q     = {q0, q1(E), q2(ER), q3(ERR), q4(ERRO), q5(ERROR), q_word}")
    print("    Sigma = {E, R, O, Other_Word_Chars, Non_Word_Chars}")
    print("    q0    = q0 (Word boundary / Initial state)")
    print("    F     = {q5} (Accepts and emits match upon delimiter or EOF)")
    print("    delta = Complete 7x5 deterministic transition matrix")
    print("-" * 80)

    print("\n[2] COMPLETE TRANSITION TABLE (delta):")
    header = f"    {'State':<10} {'E':<10} {'R':<10} {'O':<10} {'OtherWord':<12} {'NonWord':<10}"
    print(header)
    print("    " + "-" * 62)
    for state, row in DFAErrorScanner.TRANSITION_TABLE.items():
        print(
            f"    {state.value:<10} "
            f"{row[CharClass.E].value:<10} "
            f"{row[CharClass.R].value:<10} "
            f"{row[CharClass.O].value:<10} "
            f"{row[CharClass.OTHER_WORD].value:<12} "
            f"{row[CharClass.NON_WORD].value:<10}"
        )
    print("-" * 80)

    print("\n[3] DETAILED EXTRACTION METRICS FOR 'ERROR':")
    print("    Note: Character span uses [start:end) 0-based half-open indexing.")
    print("    Line and Column use 1-based indexing.")
    print("-" * 80)

    if not matches:
        print("    (No occurrences of keyword 'ERROR' identified)")
    else:
        metric_header = (
            f"    {'#':<4} {'Matched Value':<16} "
            f"{'Char Span [start:end)':<22} {'Line:Col':<12} {'Sample Context'}"
        )
        print(metric_header)
        print("    " + "-" * 74)
        for idx, m in enumerate(matches, 1):
            span_str = f"[{m.start_offset}:{m.end_offset})"
            line_col = f"L{m.line_number}:C{m.column_number}"
            snippet = m.line_text
            if len(snippet) > 35:
                snippet = snippet[:32] + "..."
            print(
                f"    {idx:<4} {m.value:<16} "
                f"{span_str:<22} {line_col:<12} {snippet}"
            )

    print("\n" + "=" * 80)
    print("   DFA SCANNER EXECUTION COMPLETED SUCCESSFULLY")
    print("=" * 80)


def main() -> None:
    """CLI Entry Point."""
    target_path = Path("data/sample.log")
    if len(sys.argv) > 1:
        target_path = Path(sys.argv[1])

    scanner = DFAErrorScanner()
    try:
        matches, elapsed, char_count = scanner.scan_file(target_path)
        display_dfa_results(matches, elapsed, char_count, str(target_path))
    except Exception as err:
        print(f"[ERROR] DFA execution failed: {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
