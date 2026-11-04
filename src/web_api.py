"""
TOC SET-E Case Study: Web API and Local Server
Course Code: 24CS52 — Theory of Computations (2026–2027)

Module: src/web_api.py
Description:
    Lightweight Flask REST API serving the web dashboard and exposing endpoints
    that directly invoke the verified REAnalyzer and DFAErrorScanner classes
    without modifying their internal logic or CLI capabilities.

Endpoints:
    - GET  /                  : Serves the web dashboard (web/index.html)
    - GET  /api/sample-log    : Returns default sample.log content and metadata
    - POST /api/analyze/re    : Runs REAnalyzer on input text (all 5 patterns)
    - POST /api/analyze/dfa   : Runs DFAErrorScanner on input text (keyword ERROR)
    - GET  /api/dfa/metadata  : Returns formal 5-tuple and transition matrix
"""

from dataclasses import asdict
from pathlib import Path
import os
import sys
import time
from typing import Any, Dict

from flask import Flask, jsonify, request, send_from_directory

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.re_analyzer import REAnalyzer
from src.dfa_analyzer import DFAErrorScanner

def _resolve_resource(rel_path: str) -> Path:
    """Resolves path across local, container, and serverless deployment environments."""
    for base in (PROJECT_ROOT, Path.cwd(), Path(__file__).resolve().parent.parent):
        candidate = (base / rel_path).resolve()
        if candidate.exists():
            return candidate
    return (PROJECT_ROOT / rel_path).resolve()

WEB_DIR = _resolve_resource("web")
SAMPLE_LOG_PATH = _resolve_resource("data/sample.log")
MAX_PAYLOAD_CHARS = 500_000  # Safe cap for input processing (~500 KB)

app = Flask(__name__, static_folder=str(WEB_DIR), static_url_path="")

# Production security configuration
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024  # 1 MB WSGI-level body limit

# Initialize analyzers as singletons
re_analyzer = REAnalyzer()
dfa_scanner = DFAErrorScanner()


@app.after_request
def add_security_headers(response):
    """Injects standard HTTP security headers for production safety."""
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


@app.route("/", methods=["GET"])
@app.route("/index.html", methods=["GET"])
def index():
    """Serves the dashboard index page."""
    return send_from_directory(str(WEB_DIR), "index.html", mimetype="text/html")


@app.route("/styles.css", methods=["GET"])
def styles():
    """Serves the dashboard CSS stylesheet."""
    return send_from_directory(str(WEB_DIR), "styles.css", mimetype="text/css")


@app.route("/app.js", methods=["GET"])
def script():
    """Serves the dashboard JavaScript application logic."""
    return send_from_directory(str(WEB_DIR), "app.js", mimetype="application/javascript")


@app.route("/api/sample-log", methods=["GET"])
def get_sample_log():
    """Returns the verified deterministic sample log dataset."""
    if not SAMPLE_LOG_PATH.is_file():
        return jsonify({"error": "Sample log file not found"}), 404

    content = SAMPLE_LOG_PATH.read_text(encoding="utf-8")
    lines = content.splitlines()
    return jsonify({
        "status": "success",
        "filename": "data/sample.log",
        "text": content,
        "character_count": len(content),
        "line_count": len(lines),
    })


@app.route("/api/analyze/re", methods=["POST"])
def analyze_re():
    """
    Executes the 5-pattern regular expression analysis on provided text.
    Directly invokes REAnalyzer.analyze_text without alterations.
    """
    if not request.is_json:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    data = request.get_json()
    text = data.get("text", "")

    if not isinstance(text, str):
        return jsonify({"error": "'text' field must be a string"}), 400

    if len(text) > MAX_PAYLOAD_CHARS:
        return jsonify({
            "error": f"Payload exceeds maximum allowed length of {MAX_PAYLOAD_CHARS} characters"
        }), 413

    # High-resolution benchmark of pattern execution
    t0 = time.perf_counter()
    raw_results = re_analyzer.analyze_text(text)
    elapsed_ms = (time.perf_counter() - t0) * 1000.0

    # Format structured response
    serialized_patterns: Dict[str, Any] = {}
    total_matches = 0

    for pattern_name, matches in raw_results.items():
        total_matches += len(matches)
        serialized_patterns[pattern_name] = {
            "count": len(matches),
            "regex": REAnalyzer.PATTERNS[pattern_name],
            "matches": [asdict(m) for m in matches],
        }

    return jsonify({
        "status": "success",
        "engine": "Regular Expression (Python re)",
        "execution_time_ms": round(elapsed_ms, 3),
        "total_matches": total_matches,
        "character_count": len(text),
        "patterns": serialized_patterns,
    })


@app.route("/api/analyze/dfa", methods=["POST"])
def analyze_dfa():
    """
    Executes pure manual DFA whole-word search for keyword ERROR.
    Directly invokes DFAErrorScanner.scan_text without regex libraries.
    """
    if not request.is_json:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    data = request.get_json()
    text = data.get("text", "")

    if not isinstance(text, str):
        return jsonify({"error": "'text' field must be a string"}), 400

    if len(text) > MAX_PAYLOAD_CHARS:
        return jsonify({
            "error": f"Payload exceeds maximum allowed length of {MAX_PAYLOAD_CHARS} characters"
        }), 413

    # High-resolution benchmark of DFA scanning
    t0 = time.perf_counter()
    raw_matches = dfa_scanner.scan_text(text)
    elapsed_ms = (time.perf_counter() - t0) * 1000.0

    serialized_matches = [asdict(m) for m in raw_matches]

    return jsonify({
        "status": "success",
        "engine": "Deterministic Finite Automaton (Manual DFA)",
        "target_token": "ERROR",
        "boundary_rule": "Complete word (\\bERROR\\b equivalent)",
        "execution_time_ms": round(elapsed_ms, 3),
        "total_matches": len(serialized_matches),
        "character_count": len(text),
        "matches": serialized_matches,
    })


@app.route("/api/compare", methods=["POST"])
def compare_engines():
    """
    Executes both RE and DFA specifically on keyword ERROR and computes
    1:1 spatial coordinate equivalence side-by-side.
    """
    if not request.is_json:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    data = request.get_json()
    text = data.get("text", "")

    if not isinstance(text, str):
        return jsonify({"error": "'text' field must be a string"}), 400

    if len(text) > MAX_PAYLOAD_CHARS:
        return jsonify({
            "error": f"Payload exceeds maximum allowed length of {MAX_PAYLOAD_CHARS} characters"
        }), 413

    # Run RE for ERROR
    t0_re = time.perf_counter()
    re_raw = re_analyzer.analyze_text(text)
    re_error_matches = re_raw.get("ERROR Keyword", [])
    re_time_ms = (time.perf_counter() - t0_re) * 1000.0

    # Run DFA
    t0_dfa = time.perf_counter()
    dfa_matches = dfa_scanner.scan_text(text)
    dfa_time_ms = (time.perf_counter() - t0_dfa) * 1000.0

    # Align side-by-side
    comparison_items = []
    max_len = max(len(re_error_matches), len(dfa_matches))
    all_equal = len(re_error_matches) == len(dfa_matches)

    for i in range(max_len):
        re_m = re_error_matches[i] if i < len(re_error_matches) else None
        dfa_m = dfa_matches[i] if i < len(dfa_matches) else None

        item_match = False
        if re_m and dfa_m:
            item_match = (
                re_m.value == dfa_m.value
                and re_m.start_offset == dfa_m.start_offset
                and re_m.end_offset == dfa_m.end_offset
                and re_m.line_number == dfa_m.line_number
                and re_m.column_number == dfa_m.column_number
            )
            if not item_match:
                all_equal = False
        else:
            all_equal = False

        comparison_items.append({
            "index": i + 1,
            "re_value": re_m.value if re_m else None,
            "dfa_value": dfa_m.value if dfa_m else None,
            "re_span": [re_m.start_offset, re_m.end_offset] if re_m else None,
            "dfa_span": [dfa_m.start_offset, dfa_m.end_offset] if dfa_m else None,
            "re_line": re_m.line_number if re_m else None,
            "dfa_line": dfa_m.line_number if dfa_m else None,
            "re_col": re_m.column_number if re_m else None,
            "dfa_col": dfa_m.column_number if dfa_m else None,
            "line_text": (re_m or dfa_m).line_text if (re_m or dfa_m) else "",
            "is_equal": item_match,
        })

    return jsonify({
        "status": "success",
        "target_token": "ERROR",
        "re_count": len(re_error_matches),
        "dfa_count": len(dfa_matches),
        "counts_equal": len(re_error_matches) == len(dfa_matches),
        "overall_parity": all_equal,
        "re_time_ms": round(re_time_ms, 3),
        "dfa_time_ms": round(dfa_time_ms, 3),
        "comparison_items": comparison_items,
    })


@app.route("/api/dfa/trace", methods=["POST"])
def trace_dfa_token():
    """
    Steps through an arbitrary input token character by character using the real
    DFAErrorScanner methods and transition table to generate an authentic trace.
    """
    if not request.is_json:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    data = request.get_json()
    token = data.get("token", "")

    if not isinstance(token, str):
        return jsonify({"error": "'token' field must be a string"}), 400

    if len(token) > 1000:
        return jsonify({"error": "Token trace input cannot exceed 1000 characters"}), 400

    from src.dfa_analyzer import DFAState, CharClass

    steps = []
    state = DFAState.Q0
    candidate_start = None
    matches_emitted = []

    for index, char in enumerate(token):
        char_class = DFAErrorScanner.classify_char(char)
        prev_state = state

        # Check Q5 boundary condition
        boundary_event = None
        if state == DFAState.Q5_ERROR:
            if char_class == CharClass.NON_WORD:
                boundary_event = f"Right boundary verified by non-word '{char}'. Match accepted!"
                matches_emitted.append({"start": candidate_start, "end": index})
                candidate_start = None
                state = DFAState.Q0
            else:
                boundary_event = f"Boundary violated by word character '{char}'. Word continues; candidate discarded."
                candidate_start = None
                state = DFAState.Q_WORD

        # Compute next state
        if state == DFAState.Q0 and char_class == CharClass.E:
            candidate_start = index
            state = DFAState.Q1_E
            action = f"Encountered 'E' at word boundary -> Recorded candidate start at index {index} -> q1"
        else:
            state = DFAErrorScanner.TRANSITION_TABLE[state][char_class]
            if state == DFAState.Q0:
                candidate_start = None
                action = f"Transitioned to q0 (boundary reset)"
            elif state == DFAState.Q_WORD:
                action = f"Inside non-matching word -> q_word"
            elif state == DFAState.Q5_ERROR:
                action = f"Sequence 'ERROR' recognized -> Entered q5 (awaiting boundary)"
            else:
                action = f"Matched prefix -> Transitioned to {state.value}"

        steps.append({
            "step": index + 1,
            "char": char,
            "char_class": char_class.value,
            "from_state": prev_state.value,
            "to_state": state.value,
            "action": action,
            "boundary_event": boundary_event,
        })

    # EOF Evaluation
    eof_event = None
    if state == DFAState.Q5_ERROR and candidate_start is not None:
        eof_event = "End-Of-File (EOF) reached while in q5. EOF acts as a valid right boundary! Match accepted."
        matches_emitted.append({"start": candidate_start, "end": len(token)})

    return jsonify({
        "status": "success",
        "token": token,
        "token_length": len(token),
        "steps": steps,
        "final_state": state.value,
        "eof_event": eof_event,
        "total_matches": len(matches_emitted),
        "matches": matches_emitted,
    })


@app.route("/api/benchmark", methods=["POST"])
def run_live_benchmark():
    """
    Executes a bounded live empirical benchmark using time.perf_counter().
    Clearly labeled as machine- and run-dependent fresh measurements.
    """
    import statistics

    if not request.is_json:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    data = request.get_json()
    text = data.get("text", "")
    iterations = data.get("iterations", 50)

    if not isinstance(text, str):
        return jsonify({"error": "'text' field must be a string"}), 400

    if not isinstance(iterations, int) or iterations < 10 or iterations > 250:
        return jsonify({"error": "'iterations' must be an integer between 10 and 250"}), 400

    if len(text) > MAX_PAYLOAD_CHARS:
        return jsonify({"error": f"Payload exceeds maximum allowed length"}), 413

    if not text.strip():
        return jsonify({"error": "Text cannot be empty for benchmarking"}), 400

    error_regex = re_analyzer.compiled_patterns["ERROR Keyword"]

    # Workload 1: RE ERROR only
    re_times = []
    for _ in range(iterations):
        t0 = time.perf_counter()
        _ = list(error_regex.finditer(text))
        re_times.append(time.perf_counter() - t0)

    # Workload 2: DFA ERROR scanner
    dfa_times = []
    for _ in range(iterations):
        t0 = time.perf_counter()
        _ = dfa_scanner.scan_text(text)
        dfa_times.append(time.perf_counter() - t0)

    # Workload 3: Full RE (5 patterns)
    re_all_times = []
    for _ in range(iterations):
        t0 = time.perf_counter()
        _ = re_analyzer.analyze_text(text)
        re_all_times.append(time.perf_counter() - t0)

    def stats_dict(times):
        return {
            "mean_us": round(statistics.mean(times) * 1e6, 2),
            "median_us": round(statistics.median(times) * 1e6, 2),
            "min_us": round(min(times) * 1e6, 2),
            "max_us": round(max(times) * 1e6, 2),
            "stdev_us": round(statistics.stdev(times) * 1e6, 2) if len(times) > 1 else 0.0,
        }

    return jsonify({
        "status": "success",
        "disclaimer": "Live empirical measurements vary with CPU load, clock frequency, and operating system scheduling.",
        "iterations": iterations,
        "character_count": len(text),
        "workload_a_re_error_us": stats_dict(re_times),
        "workload_a_dfa_error_us": stats_dict(dfa_times),
        "workload_b_re_all_5_us": stats_dict(re_all_times),
    })


@app.route("/api/dfa/metadata", methods=["GET"])
def get_dfa_metadata():
    """
    Returns the formal 5-tuple specification and exact transition matrix
    derived directly from the DFAErrorScanner implementation.
    """
    # Build transition table dynamically from DFAErrorScanner.TRANSITION_TABLE
    transition_matrix = {}
    for state, row in DFAErrorScanner.TRANSITION_TABLE.items():
        transition_matrix[state.value] = {
            cls.value: next_state.value for cls, next_state in row.items()
        }

    return jsonify({
        "status": "success",
        "formal_definition": "M = (Q, Sigma, delta, q0, F)",
        "states": [s.value for s in DFAErrorScanner.TRANSITION_TABLE.keys()],
        "alphabet_classes": ["E", "R", "O", "OTHER_WORD", "NON_WORD"],
        "start_state": "q0",
        "accepting_state": "q5 (emits match when followed by NON_WORD or EOF)",
        "trap_state": "q_word (inside non-matching word)",
        "transition_table": transition_matrix,
    })


def create_app():
    """Factory function for testing or WSGI servers."""
    return app


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "127.0.0.1")
    debug_mode = os.environ.get("FLASK_DEBUG", "0").lower() in ("true", "1", "yes")
    print(f"Starting TOC Case Study Web Server at http://{host}:{port} (debug={debug_mode})")
    app.run(host=host, port=port, debug=debug_mode)

