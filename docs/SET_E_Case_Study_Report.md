# DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING
### ACADEMIC YEAR 2026–2027 | 5TH SEMESTER B.E.
### COURSE CODE: 24CS52 — THEORY OF COMPUTATIONS
---
# CASE STUDY REPORT: SET-E
## LOG FILE ANALYSIS USING REGULAR EXPRESSIONS AND DETERMINISTIC FINITE AUTOMATA (DFA)

```text
========================================================================================
STUDENT NAME         : [Student Name Placeholder]
USN                  : [USN Placeholder]
SEMESTER / BRANCH    : 5th Semester B.E. / Computer Science & Engineering
COURSE TITLE         : Theory of Computations (24CS52)
CASE STUDY ALLOTMENT : SET-E (Log File Analysis using RE & DFA)
FACULTY GUIDE        : [Faculty Guide / Mentor Placeholder]
INSTITUTION          : [College / Institution Name Placeholder]
SUBMISSION DATE      : [Submission Date Placeholder]
========================================================================================
```

> **Formatting & Academic Transfer Guidelines:**  
> When transferring this document to the prescribed institutional Microsoft Word report template:  
> - **Primary Font:** Times New Roman  
> - **Font Size:** 12 pt for body text, 14 pt bold for section headings, 16 pt bold for chapter titles  
> - **Line Spacing:** 1.5 line spacing  
> - **Alignment:** Justified paragraphs  
> - **Margins:** 1.25 inches (Left) for binding, 1.0 inch (Right, Top, Bottom)

---

## TABLE OF CONTENTS

1. [Abstract](#1-abstract)
2. [Introduction and Problem Statement](#2-introduction-and-problem-statement)
3. [Project Objectives](#3-project-objectives)
4. [Scope and Limitations](#4-scope-and-limitations)
5. [Theoretical Concepts and Background](#5-theoretical-concepts-and-background)
6. [Dataset Description and Sample Log Design](#6-dataset-description-and-sample-log-design)
7. [Regular Expression Analyzer Design](#7-regular-expression-analyzer-design)
8. [Deterministic Finite Automaton (DFA) Design](#8-deterministic-finite-automaton-dfa-design)
9. [Software Implementation and Project Architecture](#9-software-implementation-and-project-architecture)
10. [Testing Methodology and Validation Results](#10-testing-methodology-and-validation-results)
11. [Comparative Analysis (RE vs. DFA)](#11-comparative-analysis-re-vs-dfa)
12. [Experimental Results and Discussion](#12-experimental-results-and-discussion)
13. [Limitations and Future Enhancements](#13-limitations-and-future-enhancements)
14. [Conclusion](#14-conclusion)
15. [References](#15-references)
16. [Appendix: Execution and Reproduction Instructions](#16-appendix-execution-and-reproduction-instructions)

---

## 1. Abstract

Modern computing systems generate extensive transaction and diagnostic logs that are critical for cybersecurity auditing, system diagnostics, and operational performance telemetry. The formal classification and extraction of tokens from unstructured or semi-structured log streams constitute a fundamental practical application of formal language theory. This case study, completed for the Theory of Computations course (24CS52, SET-E), investigates and contrasts two formal computational approaches for log file analysis: (1) practical declarative pattern matching using extended Regular Expressions (RE) implemented via Python's standard `re` module, and (2) a manually constructed, state-driven Deterministic Finite Automaton (DFA) scanner implemented in pure Python without importing or utilizing any regular expression engine.

The system extracts five critical operational log tokens: Dates (`DD-MM-YYYY`), Times (`HH:MM`), IPv4 addresses, and severity keywords (`ERROR` and `WARNING`). To prevent false substring matches within larger identifiers, explicit boundary assertions are applied. For the keyword `ERROR`, an equivalent 7-state deterministic automaton $M = (Q, \Sigma, \delta, q_0, F)$ over a partitioned alphabet was formally designed and implemented. Both analyzers were evaluated against a deterministic benchmark dataset of 30 log records (2,520 characters) containing valid entries, repeated tokens, and deliberate negative boundary traps. In empirical testing, both implementations exhibited 100% spatial identity, extracting the identical 7 occurrences of `ERROR` with matching character spans and line/column indices. An empirical benchmark over 1,000 iterations measured a median execution time of $214.55\ \mu\text{s}$ for the regex `ERROR` matcher versus $1,671.70\ \mu\text{s}$ for the manual DFA scanner. This difference is analyzed in terms of Python Virtual Machine bytecode interpretation overhead versus native C-runtime execution. The test suite, comprising 21 automated test methods and 28 subtests, confirmed total functional compliance.

---

## 2. Introduction and Problem Statement

### 2.1 Background
In enterprise software environments, operating systems, database engines, and network appliances continuously append operational telemetry into log files. Analyzing these logs requires isolating specific tokens—such as timestamps, host internet protocol (IP) addresses, and error classifications—from arbitrary diagnostic text. In computational linguistics and automata theory, such token extraction corresponds to membership verification in formal regular languages.

### 2.2 Problem Statement
Given an unstructured text stream $T \in \Sigma^*$ representing system log output, develop an automated analysis system that:
1. Formulates formal regular expressions to detect five distinct token patterns: Date, Time, IPv4 Address, the keyword `ERROR`, and the keyword `WARNING`.
2. Employs boundary safeguards to eliminate substring false positives (e.g., rejecting `ERRORS`, `XERROR`, `32-01-2026`, or `1.2.3.4.5`).
3. Formally models, constructs, and executes a Deterministic Finite Automaton (DFA) to recognize the whole-word keyword `ERROR` without importing or relying on regular expression libraries.
4. Reports the extracted tokens, occurrence frequencies, zero-based half-open character spans $[start:end)$, and one-based line and column coordinates.
5. Evaluates both implementations on an identical dataset and conducts a rigorous comparative study analyzing complexity, execution timing, code architecture, accuracy, and operational maintainability.

---

## 3. Project Objectives

The primary engineering and theoretical objectives of this case study are:
- **Theoretical Modeling:** Express system log patterns as regular languages and design an equivalent Deterministic Finite Automaton $M$ as a formal 5-tuple $(Q, \Sigma, \delta, q_0, F)$ for token search with word boundaries.
- **Dual Implementation:**
  - Implement a multi-pattern log analyzer in Python (`src/re_analyzer.py`) using the standard library `re` module.
  - Implement a pure, state-driven DFA scanner in Python (`src/dfa_analyzer.py`) that strictly avoids regex libraries.
- **Dataset Construction:** Build a deterministic, representative sample dataset (`data/sample.log`) containing at least 20 log entries that incorporates valid targets, repeated occurrences, non-target text, and negative boundary traps.
- **Verification and Benchmarking:**
  - Validate equivalence between RE and DFA on the target pattern `ERROR`.
  - Execute an automated test suite verifying edge cases, boundary rejections, and coordinate calculations.
  - Conduct a like-for-like empirical benchmark (1,000 iterations) using high-resolution hardware counters.
- **Academic Synthesis:** Document the mathematical proofs, state diagrams, transition matrices, empirical findings, and curriculum-aligned conclusions for B.E. Computer Science evaluation.

---

## 4. Scope and Limitations

### 4.1 Scope
- The system is designed to process standard ASCII-encoded and UTF-8 text log files.
- Five targeted token types are covered: Gregorian dates in `DD-MM-YYYY` notation, 24-hour time in `HH:MM` notation, dotted-decimal IPv4 addresses, and severity markers `ERROR` and `WARNING`.
- Whole-word boundary semantics correspond to Python's `\b` definition, where word characters are defined as alphanumeric characters and underscore: $[0\text{--}9\text{a}\text{--}\text{z}\text{A}\text{--}\text{Z}\_]$.

### 4.2 Limitations
1. **Date Semantic Range vs. Calendar Validity:**  
   The regular expression for date validation enforces structural format and numerical ranges ($DD \in [01, 31]$, $MM \in [01, 12]$, $YYYY \in [0000, 9999]$). However, it does not validate variable month lengths (e.g., April having 30 days) or leap years (e.g., February 29th validity). A string such as `31-02-2026` is accepted by the regular expression as syntactically compliant with the $DD \le 31$ rule. In production systems, semantic calendar validation requires post-processing via datetime libraries.
2. **IPv4 Trailing Delimiter Behavior:**  
   The IPv4 regular expression employs the negative lookahead assertion `(?![\d.])` to prevent false positive matches on five-octet candidates (e.g., rejecting `1.2.3.4` inside `1.2.3.4.5`). Consequently, if an IPv4 address is placed immediately prior to an English grammatical period without an intervening delimiter (e.g., `192.168.1.1.`), the period triggers the lookahead rejection. Log formats must ensure IP addresses are followed by standard delimiters (whitespace, colons, brackets, or context text).
3. **Equivalence Scope:**  
   Functional equivalence between the RE and DFA implementations is empirically verified across the provided benchmark log and the 21 test vectors. This represents empirical verification over defined operational inputs rather than a formal universal mathematical proof for all arbitrary input strings.

---

## 5. Theoretical Concepts and Background

### 5.1 Regular Languages and Regular Expressions
In the Chomsky hierarchy of formal languages, a language $L$ is regular (Type-3) if it can be generated by a regular grammar or defined by a regular expression. According to Kleene's Theorem, regular languages are precisely the languages recognized by Finite Automata:
$$\mathcal{L}(\text{DFA}) = \mathcal{L}(\text{NFA}) = \mathcal{L}(\text{RE})$$

In practical software engineering, regular expression engines extend classical regular expressions with zero-width assertions:
- **Zero-Width Word Boundary ($\backslash\text{b}$):** Matches at a position where one side is a word character ($\backslash\text{w}$) and the other is a non-word character ($\backslash\text{W}$) or the string boundary.
- **Negative Lookbehind ($(?<!\dots)$):** Asserts that the subpattern does not match immediately preceding the current cursor.
- **Negative Lookahead ($(?!\dots)$):** Asserts that the subpattern does not match immediately following the current cursor.

### 5.2 Deterministic Finite Automata (DFA)
A Deterministic Finite Automaton (DFA) is a theoretical model of computation formally defined as a 5-tuple:
$$M = (Q, \Sigma, \delta, q_0, F)$$
where:
- $Q$ is a finite, non-empty set of states.
- $\Sigma$ is a finite input alphabet.
- $\delta: Q \times \Sigma \to Q$ is the transition function mapping a state and an input symbol to a unique successor state.
- $q_0 \in Q$ is the designated start state.
- $F \subseteq Q$ is the set of accepting (or final) states.

### 5.3 DFA in Text Search and Lexical Analysis
In compiler design (Hopcroft & Ullman Section 1.5, 2.2), finite automata are deployed as scanning transducers. Rather than merely deciding whether an entire string belongs to $L$, a scanning automaton traverses an input stream $T = c_0 c_1 \dots c_{n-1}$, tracks candidate match start offsets, evaluates word boundaries, and emits recognized token spans $[start:end)$ upon encountering acceptance conditions.

---

## 6. Dataset Description and Sample Log Design

To ensure reproducible, deterministic evaluation, a benchmark log file was constructed at [`data/sample.log`](file:///c:/Users/yuvan/OneDrive/Documents/5-SEMESTER/PROJECTS/TOC%20PROJECT/data/sample.log). The dataset consists of **30 log entries** spanning **2,520 bytes**, meeting the curriculum requirement of $\ge 20$ entries.

### 6.1 Dataset Composition
- **Timestamps:** Standard server timestamps formatted as `DD-MM-YYYY HH:MM`.
- **Severity Levels:** Operational log records categorized by `INFO`, `[WARNING]`, and `ERROR`.
- **Network Identifiers:** Valid IPv4 addresses across Class A (`10.0.0.25`), Class B (`172.16.4.102`), Class C (`192.168.1.1`), Loopback (`127.0.0.1`), and Broadcast/Subnet (`255.255.255.0`).
- **Multiple Occurrences on a Single Line:**
  - Line 6 features two distinct occurrences of `ERROR` (at columns 19 and 60).
  - Line 8 features two distinct occurrences of `WARNING` (at columns 20 and 74).
- **Neutral / Non-Target Entries:** System banner lines and operational text devoid of target tokens (Lines 15, 16, 29, 30).
- **Deliberate Negative Boundary Traps:**
  - *Embedded keywords:* `ERRORS`, `MYERROR`, `NOERROR`, `PREWARNING`, `WARNINGS`.
  - *Invalid IPv4 addresses:* `999.300.500.1` (octet $> 255$), `10.256.0.1` (octet $> 255$), `1.2.3.4.5` (5 octets).
  - *Malformed timestamps:* `32-01-2026` (invalid day), `25:70` (invalid hour/minute), `2026-03-15` (non-matching format), `15/03/2026` (slash delimiters).

---

## 7. Regular Expression Analyzer Design

The regular expression analyzer is implemented in [`src/re_analyzer.py`](file:///c:/Users/yuvan/OneDrive/Documents/5-SEMESTER/PROJECTS/TOC%20PROJECT/src/re_analyzer.py) using Python's standard `re` library.

### 7.1 Formal Pattern Specifications

```text
+---+-------------------+-------------------------------------------------------------------------------------------------+------------------------------------------+
| # | Pattern Name      | Formal Regular Expression                                                                       | Boundary & Validation Safeguard          |
+---+-------------------+-------------------------------------------------------------------------------------------------+------------------------------------------+
| 1 | Date (DD-MM-YYYY) | (?<!\d)(?:0[1-9]|[12]\d|3[01])-(?:0[1-9]|1[0-2])-\d{4}(?!\d)                                    | Lookarounds (?<!\d) and (?!\d)           |
| 2 | Time (HH:MM)      | (?<!\d)(?:[01]\d|2[0-3]):[0-5]\d(?!\d)                                                          | Lookarounds (?<!\d) and (?!\d)           |
| 3 | IPv4 Address      | (?<![\d.])(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(?:\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}(?![\d.]) | Octet limits 0-255, lookaround (?<![\d.])|
| 4 | ERROR Keyword     | \bERROR\b                                                                                       | Word boundary \b anchors                 |
| 5 | WARNING Keyword   | \bWARNING\b                                                                                     | Word boundary \b anchors                 |
+---+-------------------+-------------------------------------------------------------------------------------------------+------------------------------------------+
```

### 7.2 Pattern Analysis and Component Breakdown

1. **Date Pattern:**
   $$\mathtt{(?<!\backslash d)(?:0[1-9]|[12]\backslash d|3[01])-(?:0[1-9]|1[0-2])-\backslash d\{4\}(?!\backslash d)}$$
   - `(?<!\d)`: Negative lookbehind asserting the preceding character is not a digit (prevents matching `15-03-2026` inside `915-03-2026`).
   - `(?:0[1-9]|[12]\d|3[01])`: Non-capturing group restricting day numbers to $01\text{--}09$, $10\text{--}29$, or $30\text{--}31$.
   - `-`: Literal hyphen delimiter.
   - `(?:0[1-9]|1[0-2])`: Non-capturing group restricting months to $01\text{--}09$ or $10\text{--}12$.
   - `-\d{4}`: Literal hyphen followed by exactly four calendar year digits.
   - `(?!\d)`: Negative lookahead ensuring trailing characters are not digits.

2. **Time Pattern:**
   $$\mathtt{(?<!\backslash d)(?:[01]\backslash d|2[0-3]):[0-5]\backslash d(?!\backslash d)}$$
   - `(?<!\d)`: Ensures no preceding digit.
   - `(?:[01]\d|2[0-3])`: Restricts hours to $00\text{--}19$ or $20\text{--}23$.
   - `:`: Literal colon delimiter.
   - `[0-5]\d`: Restricts minutes to $00\text{--}59$.
   - `(?!\d)`: Ensures no trailing digit.

3. **IPv4 Address Pattern:**
   $$\mathtt{(?<![\backslash d.])(?:25[0-5]|2[0-4]\backslash d|1\backslash d\backslash d|[1-9]?\backslash d)(?:\.(?:25[0-5]|2[0-4]\backslash d|1\backslash d\backslash d|[1-9]?\backslash d))\{3\}(?![\backslash d.])}$$
   - Validates four octets in the range $0\text{--}255$:
     - `25[0-5]`: Matches $250\text{--}255$.
     - `2[0-4]\d`: Matches $200\text{--}249$.
     - `1\d\d`: Matches $100\text{--}199$.
     - `[1-9]?\d`: Matches $0\text{--}99$ without leading zeroes.
   - Boundaries `(?<![\d.])` and `(?![\d.])` prevent matching sub-segments of invalid multi-dot addresses like `1.2.3.4.5`.

4. **ERROR and WARNING Patterns:**
   - Anchor `\b` asserts a zero-width word boundary between a word character $[0\text{--}9\text{A}\text{--}\text{Z}\text{a}\text{--}\text{z}\_]$ and a non-word delimiter.

---

## 8. Deterministic Finite Automaton (DFA) Design

To recognize the keyword `ERROR` with whole-word boundary semantics without regular expression libraries, a custom DFA scanner was designed in [`src/dfa_analyzer.py`](file:///c:/Users/yuvan/OneDrive/Documents/5-SEMESTER/PROJECTS/TOC%20PROJECT/src/dfa_analyzer.py).

### 8.1 Mathematical 5-Tuple Formulation
$$M = (Q, \Sigma, \delta, q_0, F)$$

1. **State Set $Q = \{q_0, q_1, q_2, q_3, q_4, q_5, q_{\text{word}}\}$**:
   - $q_0$: Start / Word Boundary State. Represents initial stream position or the state immediately following a non-word character ($\backslash\text{W}$).
   - $q_1$ ($q_E$): Prefix `'E'` recognized at a valid left boundary.
   - $q_2$ ($q_{ER}$): Prefix `'ER'` recognized.
   - $q_3$ ($q_{ERR}$): Prefix `'ERR'` recognized.
   - $q_4$ ($q_{ERRO}$): Prefix `'ERRO'` recognized.
   - $q_5$ ($q_{ERROR}$): Pre-accepting / Candidate Recognized State. The sequence `'ERROR'` has been parsed.
   - $q_{\text{word}}$: Inside-Word Trap State. An active word has begun that is not `ERROR` (e.g., `ERRORS`, `XERROR`). Absorbs word characters until reset by a delimiter.

2. **Input Alphabet Equivalence Classes ($\Sigma$)**:
   The character universe is partitioned into five disjoint equivalence classes:
   - $C_E = \{ \mathtt{'E'} \}$
   - $C_R = \{ \mathtt{'R'} \}$
   - $C_O = \{ \mathtt{'O'} \}$
   - $C_{\text{other\_word}} = \{ \mathtt{'a'}\text{--}\mathtt{'z'}, \mathtt{'A'}\text{--}\mathtt{'Z'}, \mathtt{'0'}\text{--}\mathtt{'9'}, \mathtt{'\_'} \} \setminus \{ \mathtt{'E'}, \mathtt{'R'}, \mathtt{'O'} \}$
   - $C_{\text{non\_word}} = \Sigma \setminus \text{WordChars}$ (delimiters, whitespace, brackets, punctuation)

3. **Start State:** $q_0 \in Q$

4. **Accepting Condition ($F$):**
   When the scanner is in candidate state $q_5$:
   - If the next symbol $c \in C_{\text{non\_word}}$: The right word boundary is verified. A match is emitted for span $[start:end)$, and the automaton transitions to $q_0$.
   - If the next symbol $c \in \text{WordChars}$: The word continues (e.g. `ERRORS`). The boundary is violated; the candidate is discarded, and the automaton transitions to $q_{\text{word}}$.
   - If the stream reaches End-Of-File ($\text{EOF}$) while in $q_5$: $\text{EOF}$ acts as a valid boundary. The match is emitted.

### 8.2 Complete State Transition Table ($\delta: Q \times \Sigma \to Q$)

```text
+-------------------+------------+------------+------------+--------------------+-------------------+
| Current State     | Input: 'E' | Input: 'R' | Input: 'O' | Other Word Char    | Non-Word Char     |
+-------------------+------------+------------+------------+--------------------+-------------------+
| q0 (Boundary)     | q1         | q_word     | q_word     | q_word             | q0                |
| q1 (Saw 'E')      | q_word     | q2         | q_word     | q_word             | q0                |
| q2 (Saw 'ER')     | q_word     | q3         | q_word     | q_word             | q0                |
| q3 (Saw 'ERR')    | q_word     | q_word     | q4         | q_word             | q0                |
| q4 (Saw 'ERRO')   | q_word     | q5         | q_word     | q_word             | q0                |
| q5 (Saw 'ERROR')  | q_word     | q_word     | q_word     | q_word             | q0 [EMIT MATCH]   |
| q_word (Trap)     | q_word     | q_word     | q_word     | q_word             | q0                |
+-------------------+------------+------------+------------+--------------------+-------------------+
```

### 8.3 State Transition Diagram

```text
   +------------------------------------[ Non-Word Delimiter ]<------------------------------------+
   |                                                                                               |
   v       'E'            'R'            'R'            'O'            'R'                         |
 ( q0 ) --------> ( q1 ) -----> ( q2 ) -----> ( q3 ) -----> ( q4 ) -----> (( q5 ))                 |
   | |              |              |              |              |           |                     |
   | | WordChars    | Non-Word     | Non-Word     | Non-Word     | Non-Word  | Non-Word (EMIT)     |
   | | except 'E'   |              |              |              |           +---------------------+
   | v              v              v              v              v           |
   | +-----------> ( q0 ) <------- + <----------- + <----------- +           | WordChar
   |                                                                         | (ERRORS)
   |       WordChars except valid prefix                                     v
   +-------------------------------------------------------------------> [ q_word ] <---+
                                                                           |     ^      |
                                                                           |     +------+ WordChars
                                                                           | Non-Word
                                                                           v
                                                                         ( q0 )
```

---

## 9. Software Implementation and Project Architecture

### 9.1 Project Directory Structure

```text
TOC PROJECT/
├── data/
│   └── sample.log              # Deterministic 30-entry test log dataset (2,520 bytes)
├── src/
│   ├── re_analyzer.py          # 5-pattern regex analyzer module (Python re)
│   └── dfa_analyzer.py         # Pure manual DFA scanner module (zero regex imports)
├── tests/
│   ├── test_analyzers.py       # Comprehensive unit & cross-validation test suite
│   ├── benchmark_stage4.py     # 1,000-iteration empirical benchmark harness
│   └── test_dfa_stage3.py      # Focused DFA unit tests & stage 3 comparator
├── docs/
│   ├── SET_E_Case_Study_Report.md  # Formal academic master case study report (17 sections)
│   ├── regular_expressions.md      # Formal RE specifications and regex breakdown
│   ├── dfa_design.md               # Formal 5-tuple M = (Q, Sigma, delta, q0, F) & transition table
│   ├── comparative_analysis.md     # RE vs. DFA computational complexity & benchmark
│   ├── test_cases.md               # Exhaustive test matrix and validation outputs
│   └── conclusion.md               # Academic synthesis and case study conclusion
├── outputs/
│   └── .gitkeep                # Output artifacts and log dumps
├── README.md                   # Operational guide and execution instructions
└── requirements.txt            # Project dependencies (pytest)
```

### 9.2 Verification of Non-Use of Regular Expressions in DFA
To comply strictly with the SET-E specification ("Implement the DFA without using regular expression libraries"), the module [`src/dfa_analyzer.py`](file:///c:/Users/yuvan/OneDrive/Documents/5-SEMESTER/PROJECTS/TOC%20PROJECT/src/dfa_analyzer.py) was verified statically and dynamically:
1. **Static AST Analysis:** An Abstract Syntax Tree (AST) inspection confirms no `import re`, `import regex`, `from re import ...`, or `from regex import ...` statements exist in the file.
2. **Runtime Namespace Inspection:** Inspection of `sys.modules["src.dfa_analyzer"].__dict__` confirms no `re` symbol is bound in the module scope.
3. **Core Scanning Mechanism:** The scanner operates via iterative character classification, enum indexing, and dictionary table lookup over `TRANSITION_TABLE[state][char_class]`.

---

## 10. Testing Methodology and Validation Results

Automated testing was conducted via [`tests/test_analyzers.py`](file:///c:/Users/yuvan/OneDrive/Documents/5-SEMESTER/PROJECTS/TOC%20PROJECT/tests/test_analyzers.py) using Python's standard `unittest` framework and verified with `pytest 9.2.0`.

### 10.1 Test Categories and Results

```text
========================================================================================
Test Class / Module              Test Method Name                              Status
========================================================================================
TestREAnalyzerPatterns           test_date_valid_samples                       PASSED
TestREAnalyzerPatterns           test_date_invalid_and_boundaries              PASSED
TestREAnalyzerPatterns           test_date_digit_boundary_guards               PASSED
TestREAnalyzerPatterns           test_date_documented_limitation              PASSED
TestREAnalyzerPatterns           test_time_valid_samples                       PASSED
TestREAnalyzerPatterns           test_time_invalid_and_boundaries              PASSED
TestREAnalyzerPatterns           test_ipv4_valid_samples                       PASSED
TestREAnalyzerPatterns           test_ipv4_invalid_and_boundaries              PASSED
TestREAnalyzerPatterns           test_ipv4_trailing_sentence_period_safeguard  PASSED
TestREAnalyzerPatterns           test_error_keyword_valid_and_boundaries      PASSED
TestREAnalyzerPatterns           test_error_keyword_case_sensitivity           PASSED
TestREAnalyzerPatterns           test_warning_keyword_valid_and_boundaries    PASSED
TestREAnalyzerPatterns           test_empty_and_neutral_inputs                 PASSED
----------------------------------------------------------------------------------------
TestDFAErrorScanner              test_dfa_does_not_import_or_use_re_library    PASSED
TestDFAErrorScanner              test_dfa_positive_delimiters                  PASSED
TestDFAErrorScanner              test_dfa_rejected_word_boundaries             PASSED
TestDFAErrorScanner              test_dfa_stream_positions                    PASSED
TestDFAErrorScanner              test_dfa_multiline_coordinates               PASSED
TestDFAErrorScanner              test_dfa_empty_and_whitespace_input          PASSED
----------------------------------------------------------------------------------------
TestCrossImplementationValidation test_parity_on_sample_log                   PASSED
TestCrossImplementationValidation test_parity_on_synthetic_boundary_matrix    PASSED (21/21 subtests)
========================================================================================
TOTAL: 21 Passed, 0 Failed, 28 Subtests Passed (Execution time: 0.053s)
========================================================================================
```

### 10.2 Empirical Parity on Benchmark Dataset (`data/sample.log`)
Both engines extracted exactly **7 occurrences** of `ERROR` from `sample.log` with identical spatial coordinates:

```text
+---+---------------+-----------------------+------------------+----------+----------+
| # | Matched Value | Zero-Based Span [s:e) | Line & Column    | RE State | DFA State|
+---+---------------+-----------------------+------------------+----------+----------+
| 1 | ERROR         | [338:343)             | Line 5, Col 19   | MATCHED  | MATCHED  |
| 2 | ERROR         | [435:440)             | Line 6, Col 19   | MATCHED  | MATCHED  |
| 3 | ERROR         | [476:481)             | Line 6, Col 60   | MATCHED  | MATCHED  |
| 4 | ERROR         | [962:967)             | Line 12, Col 19  | MATCHED  | MATCHED  |
| 5 | ERROR         | [1500:1505)           | Line 19, Col 19  | MATCHED  | MATCHED  |
| 6 | ERROR         | [1976:1981)           | Line 24, Col 19  | MATCHED  | MATCHED  |
| 7 | ERROR         | [2348:2353)           | Line 28, Col 19  | MATCHED  | MATCHED  |
+---+---------------+-----------------------+------------------+----------+----------+
```

---

## 11. Comparative Analysis (RE vs. DFA)

An empirical benchmark was executed via [`tests/benchmark_stage4.py`](file:///c:/Users/yuvan/OneDrive/Documents/5-SEMESTER/PROJECTS/TOC%20PROJECT/tests/benchmark_stage4.py) running on Python 3.13.3 (Windows 11, 64-bit). The benchmark recorded 1,000 iterations using `time.perf_counter()`.

### 11.1 Empirical Timing Measurements

```text
+------------------------------------+------------+--------------+------------+--------------+-------------+
| Workload / Implementation          | Mean (us)  | Median (us)  | Min (us)   | Max (us)     | StdDev (us) |
+------------------------------------+------------+--------------+------------+--------------+-------------+
| Workload A: RE (ERROR only)        | 220.74 us  | 214.55 us    | 82.80 us   | 1,415.90 us  | 138.33 us   |
| Workload A: DFA (ERROR scanner)    | 2,510.49 us| 1,671.70 us  | 1,091.20 us| 18,834.40 us | 1,784.08 us |
+------------------------------------+------------+--------------+------------+--------------+-------------+
| Workload B: RE (All 5 Patterns)    | 1,484.60 us| 924.40 us    | 679.80 us  | 31,429.50 us | 1,539.88 us |
+------------------------------------+------------+--------------+------------+--------------+-------------+
```

### 11.2 In-Depth Evaluation Dimensions

1. **Like-for-Like Runtime Comparison (Workload A):**
   - In Workload A, both engines extracted only the token `ERROR` from the identical 2,520-character input stream, including full spatial coordinate calculation (`line`, `column`, `span`).
   - The RE matcher achieved a median runtime of **$214.55\ \mu\text{s}$**, whereas the manual DFA scanner achieved a median runtime of **$1,671.70\ \mu\text{s}$**.
   - *Technical Explanation:* This empirical difference reflects runtime implementation architecture rather than an inherent algorithmic disparity. In Python, the `re` module delegates searching to a compiled native C engine (`_sre.c`). Its tight scanning loop runs directly on bare-metal processor registers. Conversely, the manual DFA is executed inside the Python Virtual Machine (PVM). For each of the 2,520 characters, the PVM dispatches multiple bytecode instructions: function invocation (`classify_char`), comparison checks, hash lookups (`TRANSITION_TABLE[state][char_class]`), and loop overhead.

2. **Multi-Pattern Workload Context (Workload B):**
   - Workload B evaluates the complete multi-pattern regular expression suite (Date, Time, IPv4, ERROR, WARNING) across the text.
   - Processing all five patterns simultaneously yielded a median execution time of **$924.40\ \mu\text{s}$**.

3. **Algorithmic and Memory Complexity:**
   - *Time Complexity:* For the fixed token `\bERROR\b`, Python's regex engine operates without catastrophic backtracking in $\mathcal{O}(n)$ time. The DFA scanner evaluates exactly one transition per input character, guaranteeing strict deterministic $\mathcal{O}(n)$ time.
   - *Auxiliary Space Complexity:* Both implementations require strictly $\mathcal{O}(1)$ working auxiliary space during stream traversal (excluding the storage buffer for emitted matches).

4. **Code Architecture and Maintainability:**

```text
+---------------------------------------+---------------------+---------------------+
| Structural Dimension                  | RE Analyzer (re)    | DFA Scanner (pure)  |
+---------------------------------------+---------------------+---------------------+
| Total File Lines                      | 258 lines           | 377 lines           |
| Core Recognition Logic Lines          | 18 lines            | 163 lines           |
| Number of Target Patterns Implemented | 5 patterns          | 1 pattern (ERROR)   |
| Extensibility Overhead                | 1 line of regex     | Re-architect matrix |
+---------------------------------------+---------------------+---------------------+
```
Adding a pattern to `re_analyzer.py` requires adding a single declarative string. Conversely, scaling `dfa_analyzer.py` to match multiple arbitrary tokens manually requires constructing a product automaton or implementing an algorithm such as Aho-Corasick.

---

## 12. Experimental Results and Discussion

Execution of both analyzers on the benchmark log produced the following pattern extraction metrics:

```text
+---+-------------------+-------------------+---------------------------------------------------------------+
| # | Target Pattern    | Matches Identified| Representative Extracted Values                               |
+---+-------------------+-------------------+---------------------------------------------------------------+
| 1 | Date (DD-MM-YYYY) | 26                | 15-03-2026                                                    |
| 2 | Time (HH:MM)      | 26                | 08:00, 08:02, 08:05, 08:12, 08:15, 09:55                      |
| 3 | IPv4 Address      | 10                | 192.168.1.1, 10.0.0.25, 172.16.4.102, 127.0.0.1, 255.255.255.0|
| 4 | ERROR Keyword     | 7                 | ERROR (L5:C19, L6:C19, L6:C60, L12:C19, L19:C19, L24:C19, L28)|
| 5 | WARNING Keyword   | 6                 | WARNING (L3:C20, L8:C20, L8:C74, L17:C19, L23:C20, L27:C19)   |
+---+-------------------+-------------------+---------------------------------------------------------------+
|   | Total Tokens      | 75                | Benchmark log size: 2,520 characters (30 entries)             |
+---+-------------------+-------------------+---------------------------------------------------------------+
```

### Discussion of Boundary Traps
1. **Rejection of Negative Keywords:** The tokens `ERRORS` (line 11), `MYERROR` (line 11), `NOERROR` (line 11), `PREWARNING` (line 10), and `WARNINGS` (line 10) were completely rejected by both engines, proving that boundary safeguards functioned properly.
2. **Rejection of Invalid IPv4 Addresses:** `999.300.500.1` (line 13) and `10.256.0.1` (line 18) were rejected due to octet ranges exceeding 255. `1.2.3.4.5` (line 25) was rejected due to boundary assertions `(?<![\d.])` and `(?![\d.])`.
3. **Rejection of Malformed Timestamps:** `32-01-2026` and `25:70` (line 20) were correctly ignored by numerical sub-pattern constraints.

---

## 13. Limitations and Future Enhancements

1. **Semantic Calendar Post-Processor:**  
   Future revisions should pair the date regular expression with a semantic post-processor (or an expanded finite state transition tree) to validate month lengths ($28, 29, 30, 31$ days) and leap-year divisibility ($year \pmod 4 = 0$).
2. **Multi-Pattern Automaton Architecture:**  
   The manual DFA was implemented specifically for the keyword `ERROR`. Future iterations can incorporate an Aho-Corasick trie-based DFA to scan for `ERROR`, `WARNING`, and `INFO` simultaneously in a single pass.
3. **Compiled Native DFA Execution:**  
   To evaluate the theoretical performance of finite automata without Python interpreter overhead, future work could implement the transition matrix in C or Rust via Python C-FFI bindings.

---

## 14. Conclusion

This case study successfully achieved all curricular and technical requirements defined under the Theory of Computations (24CS52) SET-E syllabus:
1. Formulated and validated five distinct regular expressions with boundary protection against substring false positives.
2. Mathematically designed an equivalent 7-state Deterministic Finite Automaton $M = (Q, \Sigma, \delta, q_0, F)$ over five alphabet equivalence classes to recognize the whole-word keyword `ERROR`.
3. Implemented both the RE engine (`src/re_analyzer.py`) and the pure DFA scanner (`src/dfa_analyzer.py`) without using regex libraries in the DFA.
4. Demonstrated 100% spatial parity on the active benchmark log, extracting the identical 7 occurrences of `ERROR` with matching character spans and line/column indices.
5. Confirmed functional correctness through an automated test suite comprising 21 test methods and 28 subtests passing under both `unittest` and `pytest`.
6. Conducted an empirical 1,000-iteration benchmark that clarified the distinction between theoretical $O(n)$ complexity and runtime interpreter dispatch overhead.

---

## 15. References

1. **Hopcroft, John E., Rajeev Motwani, and Jeffrey D. Ullman.** *Introduction to Automata Theory, Languages, and Computation.* 2nd/3rd Edition, Pearson Education, 2007. [Prescribed Textbook for 24CS52 Module 1 & 2].
2. **Sipser, Michael.** *Introduction to the Theory of Computation.* 3rd Edition, Cengage Learning, 2013. [Reference Book for 24CS52].
3. **Academic Board of Studies.** *Theory of Computations (24CS52) Course Curriculum and Assessment Guidelines.* Academic Year 2026–2027.
4. **Python Software Foundation.** *Python 3.13 Standard Library Documentation: `re` — Regular expression operations.* Available online: `https://docs.python.org/3/library/re.html`.
5. **Python Software Foundation.** *Python 3.13 Standard Library Documentation: `unittest` — Unit testing framework.* Available online: `https://docs.python.org/3/library/unittest.html`.

---

## 16. Appendix: Execution and Reproduction Instructions

All commands must be executed from the project root directory in PowerShell or Command Prompt.

### 16.1 Environment Check
```powershell
# Verify Python installation (Requires Python 3.10+)
python --version
```
*Expected Output:* `Python 3.13.3` (or 3.10+)

### 16.2 Running the Regular Expression Analyzer
```powershell
python src\re_analyzer.py
```
*Purpose:* Scans `data/sample.log`, extracts all 5 patterns, and prints summary and detailed metrics.

### 16.3 Running the Manual DFA Analyzer
```powershell
python src\dfa_analyzer.py
```
*Purpose:* Scans `data/sample.log` for keyword `ERROR` using the 7-state DFA and prints the formal transition matrix and match metrics.

### 16.4 Running the Automated Test Suite
```powershell
# Method 1: Using standard Python unittest framework
python -m unittest tests/test_analyzers.py -v

# Method 2: Using pytest (if installed)
python -m pytest tests/test_analyzers.py -v
```
*Expected Output:* `Ran 21 tests ... OK` / `21 passed, 28 subtests passed`.

### 16.5 Running the Empirical Benchmark
```powershell
python tests\benchmark_stage4.py
```
*Purpose:* Executes the 1,000-iteration like-for-like benchmark comparing RE (`ERROR` only) and DFA (`ERROR`), reporting mean, median, min, max, and standard deviation.

---
*End of Report — Prepared for Theory of Computations (24CS52) SET-E Case Study Evaluation.*

