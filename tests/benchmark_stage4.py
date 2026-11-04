"""
Stage 4 Empirical Benchmark Script: RE vs. DFA Like-for-Like Comparison
Course Code: 24CS52 — Theory of Computations (2026–2027)

Methodology:
- Single in-memory string load from data/sample.log (2,520 characters).
- 10 warm-up runs to prime interpreter and cache structures.
- Exactly 1,000 measured iterations for each workload using time.perf_counter().
- Workload 1: RE matching for ERROR keyword only (including coordinate calculation).
- Workload 2: DFA scanning for ERROR keyword only (including coordinate calculation).
- Workload 3 (Separate Workload): Full RE analyzer executing all 5 patterns combined.
"""

from pathlib import Path
import statistics
import sys
import time

# Ensure project root is in path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.re_analyzer import REAnalyzer, MatchRecord
from src.dfa_analyzer import DFAErrorScanner


def run_benchmark():
    log_path = Path("data/sample.log")
    if not log_path.is_file():
        raise FileNotFoundError(f"Missing sample log at: {log_path.resolve()}")

    content = log_path.read_text(encoding="utf-8")
    iterations = 1000

    re_analyzer = REAnalyzer()
    error_regex = re_analyzer.compiled_patterns["ERROR Keyword"]
    dfa_scanner = DFAErrorScanner()

    def re_error_only():
        matches = []
        for match in error_regex.finditer(content):
            start, end = match.start(), match.end()
            line_no, col_no, line_str = re_analyzer._compute_line_col(content, start)
            matches.append(
                MatchRecord("ERROR Keyword", match.group(), start, end, line_no, col_no, line_str)
            )
        return matches

    def dfa_error_only():
        return dfa_scanner.scan_text(content)

    def re_all_patterns():
        return re_analyzer.analyze_text(content)

    # Priming / Warm-up (10 runs)
    for _ in range(10):
        _ = re_error_only()
        _ = dfa_error_only()
        _ = re_all_patterns()

    # 1. Benchmark RE (ERROR Keyword only)
    re_error_times = []
    for _ in range(iterations):
        t0 = time.perf_counter()
        _ = re_error_only()
        re_error_times.append(time.perf_counter() - t0)

    # 2. Benchmark DFA (ERROR Keyword)
    dfa_times = []
    for _ in range(iterations):
        t0 = time.perf_counter()
        _ = dfa_error_only()
        dfa_times.append(time.perf_counter() - t0)

    # 3. Benchmark RE (All 5 Patterns Combined) - Separate Workload
    re_all_times = []
    for _ in range(iterations):
        t0 = time.perf_counter()
        _ = re_all_patterns()
        re_all_times.append(time.perf_counter() - t0)

    def compute_stats(time_list):
        return {
            "mean_us": statistics.mean(time_list) * 1e6,
            "median_us": statistics.median(time_list) * 1e6,
            "min_us": min(time_list) * 1e6,
            "max_us": max(time_list) * 1e6,
            "stdev_us": statistics.stdev(time_list) * 1e6,
        }

    s_re_error = compute_stats(re_error_times)
    s_dfa = compute_stats(dfa_times)
    s_re_all = compute_stats(re_all_times)

    print("=" * 80)
    print("   STAGE 4 EMPIRICAL BENCHMARK: RE vs. DFA LIKE-FOR-LIKE COMPARISON")
    print("=" * 80)
    print(f"Target Input Dataset : {log_path} ({len(content)} characters, 30 lines)")
    print(f"Benchmark Repetitions: {iterations} iterations per workload")
    print(f"Measurement Clock    : time.perf_counter() (Python 3.13.3 on Windows 11)")
    print("-" * 80)

    print("\n[WORKLOAD A: LIKE-FOR-LIKE COMPARISON — KEYWORD 'ERROR' MATCHING]")
    print(f"{'Implementation':<22} {'Mean (us)':<12} {'Median (us)':<12} {'Min (us)':<12} {'Max (us)':<12} {'StdDev (us)'}")
    print("-" * 80)
    print(
        f"{'RE (ERROR only)':<22} "
        f"{s_re_error['mean_us']:<12.2f} "
        f"{s_re_error['median_us']:<12.2f} "
        f"{s_re_error['min_us']:<12.2f} "
        f"{s_re_error['max_us']:<12.2f} "
        f"{s_re_error['stdev_us']:<12.2f}"
    )
    print(
        f"{'DFA (ERROR scanner)':<22} "
        f"{s_dfa['mean_us']:<12.2f} "
        f"{s_dfa['median_us']:<12.2f} "
        f"{s_dfa['min_us']:<12.2f} "
        f"{s_dfa['max_us']:<12.2f} "
        f"{s_dfa['stdev_us']:<12.2f}"
    )
    print("-" * 80)

    print("\n[WORKLOAD B: SEPARATE WORKLOAD — RE ALL 5 PATTERNS COMBINED]")
    print(f"{'Implementation':<22} {'Mean (us)':<12} {'Median (us)':<12} {'Min (us)':<12} {'Max (us)':<12} {'StdDev (us)'}")
    print("-" * 80)
    print(
        f"{'RE (All 5 Patterns)':<22} "
        f"{s_re_all['mean_us']:<12.2f} "
        f"{s_re_all['median_us']:<12.2f} "
        f"{s_re_all['min_us']:<12.2f} "
        f"{s_re_all['max_us']:<12.2f} "
        f"{s_re_all['stdev_us']:<12.2f}"
    )
    print("=" * 80)


if __name__ == "__main__":
    run_benchmark()

