# Test Cases and Validation Report

**Course:** 24CS52 — Theory of Computations | **Assignment:** SET-E Case Study

---

## 1. Test Harness Overview

Automated tests are consolidated in [`tests/test_analyzers.py`](file:///c:/Users/yuvan/OneDrive/Documents/5-SEMESTER/PROJECTS/TOC%20PROJECT/tests/test_analyzers.py) and executed via Python's standard `unittest` framework:

```powershell
python -m unittest tests/test_analyzers.py -v
```

**Result:** `Ran 21 tests in 0.053s. OK.` (with 28 subtests passing).

---

## 2. Test Case Specification Matrix

| Test ID | Module / Category | Input Vector | Expected Behavior | Result |
|:---|:---|:---|:---|:---:|
| TC-01 | Date Valid | `15-03-2026`, `01-01-2027` | Extracts 3 valid dates with exact spans | **PASS** |
| TC-02 | Date Invalid | `32-01-2026`, `15-13-2026` | 0 matches (invalid day/month ranges) | **PASS** |
| TC-03 | Date Digit Guards | `115-03-2026`, `15-03-20261` | 0 matches (lookarounds prevent partial match) | **PASS** |
| TC-04 | Date Limitation | `31-02-2026` | 1 match (syntactically valid under $DD \le 31$) | **PASS** |
| TC-05 | Time Valid | `00:00`, `08:30`, `23:59` | Extracts 4 valid times with exact spans | **PASS** |
| TC-06 | Time Invalid | `24:00`, `25:10`, `12:65` | 0 matches (invalid hour/min ranges) | **PASS** |
| TC-07 | IPv4 Valid | `192.168.1.1`, `10.0.0.25` | Extracts 6 valid IPv4 addresses | **PASS** |
| TC-08 | IPv4 Invalid | `999.300.500.1`, `1.2.3.4.5` | 0 matches (octet limits and boundary guard) | **PASS** |
| TC-09 | IPv4 Trailing Dot | `192.168.1.1.` vs `on lan` | Rejects adjacent dot; accepts with delimiter | **PASS** |
| TC-10 | RE ERROR Boundaries | `[ERROR]`, `ERRORS`, `MYERROR` | Accepts `[ERROR]`; rejects `ERRORS`, `MYERROR` | **PASS** |
| TC-11 | RE ERROR Case | `error`, `Error` | 0 matches (case-sensitive requirement) | **PASS** |
| TC-12 | RE WARNING | `[WARNING]`, `PREWARNING` | Accepts `[WARNING]`; rejects `PREWARNING` | **PASS** |
| TC-13 | RE Empty / Neutral | `""`, `"Clean system line"` | 0 matches for all patterns | **PASS** |
| TC-14 | DFA Zero-Regex Check | `src/dfa_analyzer.py` AST | Asserts no `re` or `regex` import statements | **PASS** |
| TC-15 | DFA Delimiters | `[ERROR]`, `(ERROR)`, `{ERROR}` | Accepts 10 valid delimited occurrences | **PASS** |
| TC-16 | DFA Boundary Traps | `ERRORS`, `_ERROR`, `7ERROR` | Rejects all 12 negative boundary tokens | **PASS** |
| TC-17 | DFA Stream Positions | Start of text, End of text | Correctly emits at index 0 and at EOF | **PASS** |
| TC-18 | DFA Coordinates | Multi-line text string | Accurately maps 1-based Line 2, Column 13 | **PASS** |
| TC-19 | DFA Empty String | `""`, `"   \t\n  "` | 0 matches | **PASS** |
| TC-20 | RE-DFA Log Parity | `data/sample.log` | Identical 7 occurrences, spans, and coordinates | **PASS** |
| TC-21 | RE-DFA Boundary Matrix| 21 diverse synthetic strings | 28/28 subtests show 100% equivalence | **PASS** |

