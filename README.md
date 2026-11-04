# Log File Analysis Using Regular Expressions and DFA

**Course:** Theory of Computations (24CS52)  
**Case Study:** SET-E — Log File Analysis Engine  
**Live Application URL:** [https://toc-project-ruiv.vercel.app/](https://toc-project-ruiv.vercel.app/)  
**GitHub Repository:** [https://github.com/yuvanharshaj/TOC-PROJECT](https://github.com/yuvanharshaj/TOC-PROJECT)

---

## 1. Project Overview

This project is an automated system log analysis tool and interactive web dashboard developed for the **Theory of Computations (24CS52)** case study. It explores two foundational computational paradigms for processing semi-structured text:

1. **Extended Regular Expressions:** Declarative pattern specifications using Python's standard regular expression engine (`re`) to extract five distinct log token types with strict lookaround boundary guards.
2. **Deterministic Finite Automaton (DFA):** A hand-crafted, 7-state deterministic finite state machine implemented in pure Python (`src/dfa_analyzer.py`) without importing or using any regex libraries. It scans text and identifies the keyword `ERROR` strictly at complete word boundaries.

The repository includes standalone command-line scripts, a verified 30-entry sample log dataset, an automated test suite, an empirical benchmark harness, and a responsive web dashboard served by a lightweight Flask backend.

---

## 2. Key Features

- **Multi-Pattern Declarative Extraction:** Simultaneously extracts Dates (`DD-MM-YYYY`), 24-hour Times (`HH:MM`), IPv4 addresses (`0-255` octets), `ERROR` keywords, and `WARNING` keywords.
- **Pure Manual DFA Scanner:** Evaluates characters sequentially across 5 character equivalence classes and 7 formal states without external dependencies or regex engines.
- **Coordinate Tracking:** Every match records its extracted string, zero-based half-open character span `[start:end)`, and 1-based `line:column` coordinates.
- **Side-by-Side Equivalence Comparator:** Performs an automated head-to-head check between the regex `\bERROR\b` matcher and the manual DFA scanner, confirming 100% spatial parity on the sample log.
- **Interactive DFA Visualizer & Token Tracer:** Features a live $7 \times 5$ transition matrix derived directly from the Python automaton class and a step-by-step simulator with preset test chips.
- **Live Empirical Benchmark Lab:** Runs repeatable, high-resolution timing comparisons using `time.perf_counter()`, clearly separating like-for-like single-token workloads from multi-pattern extraction.
- **Self-Contained Web Dashboard:** A responsive dark-themed UI served directly from the Flask app with zero external npm build dependencies.

---

## 3. How Regular Expressions and the Manual DFA Differ

| Dimension | Regular Expression Engine (`src/re_analyzer.py`) | Manual DFA Scanner (`src/dfa_analyzer.py`) |
|:---|:---|:---|
| **Paradigm** | **Declarative:** You define *what* string pattern to accept using pattern syntax; the engine handles compilation and traversal. | **Procedural/Automaton:** You explicitly construct the 5-tuple $M = (Q, \Sigma, \delta, q_0, F)$ and execute state transitions step-by-step. |
| **Pattern Scope** | Extracts **5 heterogeneous patterns** (Date, Time, IPv4, ERROR, WARNING) in a single pass. | Specialized for **one keyword (`ERROR`)** honoring complete word boundaries. |
| **Underlying Engine** | Implemented in **compiled C** inside CPython's internal `_sre` engine. | Implemented in **pure Python bytecode** with sequential loop execution. |
| **Algorithmic Time** | $O(N)$ linear scan on non-backtracking patterns. | Guaranteed deterministic $O(N)$ linear time under all input sequences. |
| **Memory Footprint** | Compiled regex bytecode cached in heap memory. | Constant $O(1)$ auxiliary memory using simple state integer tracking. |
| **Extensibility** | High: Adding a pattern requires only writing a new regex string. | Moderate: Adding patterns requires recalculating the state set and transition table. |

---

## 4. Five Target Patterns

| Pattern # | Target Description | Regular Expression | Boundary Protection |
|:---:|:---|:---|:---|
| 1 | Date (`DD-MM-YYYY`) | `(?<!\d)(?:0[1-9]\|[12]\d\|3[01])-(?:0[1-9]\|1[0-2])-\d{4}(?!\d)` | Negative lookaround for digit boundaries |
| 2 | Time (`HH:MM`) | `(?<!\d)(?:[01]\d\|2[0-3]):[0-5]\d(?!\d)` | Negative lookaround for digit boundaries |
| 3 | IPv4 Address | `(?<![\d.])(?:25[0-5]\|2[0-4]\d\|1\d\d\|[1-9]?\d)(?:\.(?:25[0-5]\|2[0-4]\d\|1\d\d\|[1-9]?\d)){3}(?![\d.])` | Octet bounds with dot and digit lookaround |
| 4 | Keyword `ERROR` | `\bERROR\b` | Word boundary anchors matching DFA behavior |
| 5 | Keyword `WARNING` | `\bWARNING\b` | Word boundary anchors |

---

## 5. Technology Stack

- **Language:** Python 3.10+ (Standard Library: `re`, `time`, `unittest`, `dataclasses`, `pathlib`, `statistics`)
- **Web Backend:** Flask 3.x (REST API and static asset delivery)
- **Production Server:** Gunicorn (for Linux cloud deployments)
- **Frontend:** Vanilla HTML5, CSS3 (modern dark theme), and ES6+ JavaScript
- **Test Runners:** Python `unittest` and `pytest`

---

## 6. Directory Structure

```text
TOC PROJECT/
├── .gitignore                      # Git exclusion rules (caches, virtualenvs, logs)
├── Procfile                        # Production process declaration for PaaS (Gunicorn)
├── README.md                       # Comprehensive project documentation
├── render.yaml                     # Infrastructure-as-Code deployment blueprint
├── requirements.txt                # Environment dependencies (Flask, Gunicorn, pytest)
├── data/
│   └── sample.log                  # Deterministic 30-entry test log dataset (2,520 bytes)
├── src/
│   ├── re_analyzer.py              # 5-pattern regular expression analyzer module
│   ├── dfa_analyzer.py             # Pure 7-state manual DFA scanner (zero regex imports)
│   └── web_api.py                  # Flask REST API and static file web server
├── tests/
│   ├── test_analyzers.py           # Core analyzer test suite (21 tests, 28 subtests)
│   ├── test_web_api.py             # REST API and web endpoint test suite (15 tests)
│   ├── test_dfa_stage3.py          # Focused DFA unit tests and stage 3 validation
│   └── benchmark_stage4.py         # 1,000-iteration empirical benchmark script
├── docs/
│   ├── SET_E_Case_Study_Report.md  # Comprehensive academic master report
│   ├── deployment_guide.md         # Step-by-step production hosting instructions
│   ├── regular_expressions.md      # Detailed RE pattern specifications
│   ├── dfa_design.md               # DFA 5-tuple, state diagram, and transition table
│   ├── comparative_analysis.md     # Complexity and benchmark findings
│   ├── test_cases.md               # Test case matrix and verification output
│   └── conclusion.md               # Summary of theoretical findings
├── outputs/
│   └── .gitkeep                    # Directory placeholder for output logs
└── web/
    ├── index.html                  # Dashboard layout with tab navigation
    ├── styles.css                  # Restrained dark theme styles and responsive layout
    └── app.js                      # Client logic connecting UI to backend API
```

---

## 7. Prerequisites and Local Setup

### Prerequisites
- **Operating System:** Windows 10/11, macOS, or Linux
- **Python:** Version 3.10 or higher installed and added to `PATH`

### Step 1: Open PowerShell or Terminal
Open Windows PowerShell in the project root directory:
```powershell
cd "C:\Users\yuvan\OneDrive\Documents\5-SEMESTER\PROJECTS\TOC PROJECT"
```

### Step 2: Install Dependencies
Install the required packages using pip:
```powershell
pip install -r requirements.txt
```
*(Note: On Windows, `gunicorn` is automatically skipped via an environment marker; on Linux, it installs for production hosting.)*

### Step 3: Run Standalone CLI Analyzers
Run the regular expression analyzer on the sample log:
```powershell
python src\re_analyzer.py
```

Run the manual DFA scanner on the sample log:
```powershell
python src\dfa_analyzer.py
```

### Step 4: Run the Test Suites
Run all tests using Python's standard `unittest` module:
```powershell
python -m unittest discover tests -v
```

Or using `pytest`:
```powershell
python -m pytest tests -v
```

### Step 5: Launch the Web Dashboard
Start the local server:
```powershell
python src\web_api.py
```
Open your web browser and navigate to:
```text
http://127.0.0.1:5000
```

---

## 8. Beginner-Friendly Guide to the Web Dashboard

The web dashboard is organized into five focused tabs:

### 1. Stream Analyzer (`#panel-analyzer`)
- **What it does:** Allows you to test any raw log text against both analysis engines.
- **How to use it:** Click **Load Sample Log** to populate the text area with the 30-entry test log, or paste your own log lines. Click **Run Regex Analyzer** to view matches for all five pattern types, or **Run DFA Scanner** to scan specifically for `ERROR`.
- **Understanding results:** A metric summary shows total matches, execution time, and counts. Below it, an interactive table lists each match's pattern type, exact token value, character span `[start:end)`, line/column number, and context snippet. You can filter the table by pattern type or search by keyword.

### 2. Equivalence Comparator (`#panel-compare`)
- **What it does:** Evaluates whether Python's regex engine (`\bERROR\b`) and the manual 7-state DFA produce identical results on the exact same input.
- **How to use it:** Click **Run Equivalence Verification**.
- **Understanding results:** The top card displays the parity status (e.g., "100% Coordinate Parity Confirmed"). The side-by-side table lines up each regex match with its corresponding DFA match, showing their respective character spans and coordinates with an `IDENTICAL` badge.

### 3. DFA Visualizer & Token Tracer (`#panel-dfa`)
- **What it does:** Illustrates how the 7-state automaton functions mathematically and lets you step through strings character by character.
- **How to use it:** Review the formal 5-tuple and the live $7 \times 5$ transition table. In the Token Tracer section, click any of the preset test chips (e.g., `[ERROR]`, `ERRORS`, `ERROR_`, `(ERROR)`) or type a custom string and click **Trace Automaton**.
- **Understanding results:** A status banner displays whether the token was `ACCEPTED` or `REJECTED`. The trace table shows each character, its classified category, the transition ($q_{\text{from}} \to q_{\text{to}}$), and explanatory boundary notes.

### 4. Live Benchmark (`#panel-benchmark`)
- **What it does:** Executes repeated search runs to provide fresh empirical execution measurements on your machine.
- **How to use it:** Choose an iteration count ($25, 50, 100, 200$) and click **Run Fresh Benchmark**.
- **Understanding results:** Displays statistical cards (median, mean, min, max, standard deviation) for:
  - **Workload A (Like-for-Like):** RE `ERROR` vs. DFA `ERROR`.
  - **Workload B (Separate Task):** RE across all 5 patterns combined.
  An accompanying explanation details why the C-based regex engine runs faster in CPU cycles while the DFA offers guaranteed linear bounds.

### 5. Theory & Course Reference (`#panel-theory`)
- **What it does:** Provides the formal theoretical background for the case study.
- **How to use it:** Read through the formal definitions, regular grammar rules, time/space complexity comparisons, and documented engineering trade-offs.

---

## 9. Example Input and Expected Output

### Sample Input Log Line:
```text
15-03-2026 08:15: ERROR Database connection timeout to 192.168.1.50
```

### Extracted Patterns and Outputs:
| Extracted Value | Pattern Type | Span `[start:end)` | Line:Column | Extraction Engine |
|:---|:---|:---:|:---:|:---:|
| `15-03-2026` | Date (DD-MM-YYYY) | `[0:10)` | L1:C1 | Regex Analyzer |
| `08:15` | Time (HH:MM) | `[11:16)` | L1:C12 | Regex Analyzer |
| `ERROR` | ERROR Keyword | `[18:23)` | L1:C19 | Regex & Manual DFA (Identical) |
| `192.168.1.50` | IPv4 Address | `[56:68)` | L1:C57 | Regex Analyzer |

### Sample Boundary Test Cases:
- `[ERROR]` &rarr; **Accepted** by DFA (brackets are non-word delimiter boundaries).
- `(ERROR)` &rarr; **Accepted** by DFA (parentheses are valid word boundaries).
- `ERRORS` &rarr; **Rejected** by DFA (trailing word character 'S' routes to trap state $q_{\text{word}}$).
- `XERROR` &rarr; **Rejected** by DFA (leading word character 'X' routes to trap state $q_{\text{word}}$).
- `ERROR_` &rarr; **Rejected** by DFA (underscore is classified as a word character in standard identifier syntax).
- `_ERROR` &rarr; **Rejected** by DFA (underscore prefix prevents start-state activation).

---

## 10. Automated Tests and Empirical Benchmarks

### Running the Test Suite
The project contains 38 unit tests and 28 subtests validating regex patterns, DFA states, multiline coordinate math, boundary rejection matrices, and REST API endpoints:

```powershell
python -m unittest discover tests -v
```

All 36 discoverable unit tests run and pass in ~0.06 seconds.

### Running the Stage 4 Benchmark Script
```powershell
python tests\benchmark_stage4.py
```

### Important Note on Benchmark Measurements:
Benchmark timings are strictly machine-dependent and subject to host CPU clock frequency, operating system background scheduling, and Python interpreter overhead. They measure this specific implementation on your machine, not an inherent theoretical limit of finite automata.

---

## 11. Known Limitations

To maintain academic rigor, the implementation documents the following specific limitations:

1. **Calendar Validation:** The date regex validates syntactic structure (`01-31` for days, `01-12` for months, `1900-2099` for years) with boundary guards. It does not perform semantic calendar calculations (e.g., accepting `31-02-2026` as syntactically valid). Full calendar validation requires a calendar library.
2. **IP Address Coverage:** The IPv4 regex validates standard dotted-decimal octets (`0-255`). It intentionally does not parse CIDR subnet masks (e.g., `/24`) or IPv6 addresses.
3. **DFA Keyword Specialization:** The manual DFA is constructed specifically for the whole-word keyword `ERROR`. Extending manual DFA recognition to all five patterns simultaneously would require an automated lexer generator or an Aho-Corasick automaton.

---

## 12. Deployment Instructions

The application is deployed live and configured for multiple hosting environments:

### Live Production Deployment (Vercel)
The dashboard is deployed on Vercel at:  
👉 **[https://toc-project-ruiv.vercel.app/](https://toc-project-ruiv.vercel.app/)**

The deployment uses [`vercel.json`](vercel.json) to route all requests directly to `src/web_api.py` via `@vercel/python`, bundling `web/` and `data/` assets with zero-config serverless execution.

### Container Deployment (Render)
The application is also pre-configured for deployment as a single service on [Render](https://render.com) using the included `Procfile` and `render.yaml`.

#### Steps to Deploy on Render:
1. Push your repository to GitHub.
2. Sign in to [Render](https://render.com) and click **"New +" &rarr; "Web Service"**.
3. Connect your GitHub repository.
4. Render will read the repository configuration:
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn src.web_api:app`
5. Select the **Free Tier** and click **Deploy Web Service**.

Render will deploy the application and provide a secure public URL (e.g., `https://<your-service-name>.onrender.com`).  
For comprehensive hosting details, refer to [`docs/deployment_guide.md`](docs/deployment_guide.md).

---

## 13. Academic Context

- **Course:** Theory of Computations (24CS52)
- **Allotment:** Case Study SET-E
- **Title:** Log File Analysis Using Regular Expressions and DFA
- **Topic Coverage:** Regular Languages, Regular Expressions, Deterministic Finite Automata (DFA), State Transition Functions, Equivalence Verification, and Computational Complexity.
