# Empirical and Theoretical Comparative Analysis (RE vs. DFA)

**Course:** 24CS52 — Theory of Computations | **Assignment:** SET-E Case Study

---

## 1. Benchmark Setup and Empirical Measurements

Measured across **1,000 continuous iterations** using `time.perf_counter()` on Python 3.13.3 (Windows 11, 64-bit) executing against [`data/sample.log`](file:///c:/Users/yuvan/OneDrive/Documents/5-SEMESTER/PROJECTS/TOC%20PROJECT/data/sample.log) (2,520 characters, 30 entries).

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

---

## 2. Like-for-Like Comparison Discussion

- **Measured Workload:** Workload A evaluates only the `ERROR` keyword extraction including full spatial coordinate calculation for both implementations.
- **Python Runtime Dynamics:**
  - Python's standard `re` module delegates pattern scanning to a pre-compiled native C extension (`_sre.c`).
  - The manual DFA is executed in interpreted Python bytecode, where each of the 2,520 characters incurs function calls (`classify_char`), dictionary lookups, and branch evaluations in the Python Virtual Machine.
  - The observed timing disparity reflects Python interpreter overhead rather than an inherent theoretical flaw in finite state automata.

---

## 3. Complexity and Resource Utilization

- **Time Complexity:** Both approaches operate in linear time $\mathcal{O}(n)$ where $n = 2,520$. The fixed string `\bERROR\b` does not trigger catastrophic backtracking in Python's regex engine.
- **Auxiliary Space Complexity:** Both engines operate with $\mathcal{O}(1)$ working auxiliary space during stream scanning.
- **Code Size:**
  - `src/re_analyzer.py`: 258 total lines (18 lines of core matching logic for 5 patterns).
  - `src/dfa_analyzer.py`: 377 total lines (163 lines of core recognition logic for 1 keyword).

