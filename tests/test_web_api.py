"""
Unit Test Suite for TOC Case Study Web API (src/web_api.py)
Course Code: 24CS52 — Theory of Computations (2026–2027)

Validates:
1. Static dashboard serving (GET /)
2. Sample log retrieval endpoint (GET /api/sample-log)
3. Regular Expression analysis endpoint (POST /api/analyze/re)
4. DFA Scanner analysis endpoint (POST /api/analyze/dfa)
5. DFA formal metadata endpoint (GET /api/dfa/metadata)
6. Defensive payload validation and HTTP error codes (400, 413)
"""

import json
from pathlib import Path
import sys
import unittest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.web_api import app, MAX_PAYLOAD_CHARS


class TestWebAPI(unittest.TestCase):
    """Test cases for Flask REST API endpoints."""

    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        cls.client = app.test_client()

    def test_get_index_html(self):
        """Verifies that root URL successfully serves the dashboard HTML."""
        with self.client.get("/") as response:
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Log File Analysis Engine", response.data)
            self.assertIn(b"24CS52", response.data)

    def test_get_sample_log(self):
        """Verifies retrieval of the verified 30-entry sample log."""
        response = self.client.get("/api/sample-log")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["character_count"], 2520)
        self.assertEqual(data["line_count"], 30)
        self.assertIn("15-03-2026", data["text"])

    def test_analyze_re_endpoint_valid(self):
        """Verifies that POST /api/analyze/re executes REAnalyzer across 5 patterns."""
        sample_text = (
            "15-03-2026 08:15: ERROR Database failure at 192.168.1.1 on lan.\n"
            "15-03-2026 08:20: WARNING High CPU temperature."
        )
        response = self.client.post(
            "/api/analyze/re",
            data=json.dumps({"text": sample_text}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "success")
        self.assertIn("patterns", data)
        patterns = data["patterns"]
        self.assertEqual(patterns["Date (DD-MM-YYYY)"]["count"], 2)
        self.assertEqual(patterns["Time (HH:MM)"]["count"], 2)
        self.assertEqual(patterns["IPv4 Address"]["count"], 1)
        self.assertEqual(patterns["ERROR Keyword"]["count"], 1)
        self.assertEqual(patterns["WARNING Keyword"]["count"], 1)
        self.assertEqual(data["total_matches"], 7)

    def test_analyze_dfa_endpoint_valid(self):
        """Verifies that POST /api/analyze/dfa executes DFA whole-word search for ERROR."""
        sample_text = "ERROR [ERROR] ERRORS XERROR ERROR_CODE ERROR:"
        response = self.client.post(
            "/api/analyze/dfa",
            data=json.dumps({"text": sample_text}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["target_token"], "ERROR")
        # Should match ERROR, [ERROR], and ERROR: (3 valid whole-word matches)
        # Should reject ERRORS, XERROR, ERROR_CODE
        self.assertEqual(data["total_matches"], 3)
        self.assertEqual(len(data["matches"]), 3)
        for m in data["matches"]:
            self.assertEqual(m["value"], "ERROR")

    def test_dfa_metadata_endpoint(self):
        """Verifies that GET /api/dfa/metadata returns the 7 formal states and matrix."""
        response = self.client.get("/api/dfa/metadata")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(
            data["states"],
            ["q0", "q1", "q2", "q3", "q4", "q5", "q_word"],
        )
        self.assertIn("transition_table", data)
        self.assertEqual(len(data["transition_table"]), 7)

    def test_compare_endpoint(self):
        """Verifies side-by-side comparison between RE and DFA on keyword ERROR."""
        sample_text = "ERROR [ERROR] ERRORS XERROR (ERROR) ERROR:"
        response = self.client.post(
            "/api/compare",
            data=json.dumps({"text": sample_text}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["re_count"], 4)
        self.assertEqual(data["dfa_count"], 4)
        self.assertTrue(data["counts_equal"])
        self.assertTrue(data["overall_parity"])
        self.assertEqual(len(data["comparison_items"]), 4)

    def test_dfa_trace_endpoint(self):
        """Verifies step-by-step trace generation for valid and invalid tokens."""
        # Valid token [ERROR]
        resp_valid = self.client.post(
            "/api/dfa/trace",
            data=json.dumps({"token": "[ERROR]"}),
            content_type="application/json",
        )
        self.assertEqual(resp_valid.status_code, 200)
        data_valid = resp_valid.get_json()
        self.assertEqual(data_valid["total_matches"], 1)
        self.assertEqual(len(data_valid["steps"]), 7)

        # Invalid token ERRORS (should transition to q_word)
        resp_invalid = self.client.post(
            "/api/dfa/trace",
            data=json.dumps({"token": "ERRORS"}),
            content_type="application/json",
        )
        self.assertEqual(resp_invalid.status_code, 200)
        data_invalid = resp_invalid.get_json()
        self.assertEqual(data_invalid["total_matches"], 0)
        self.assertEqual(data_invalid["final_state"], "q_word")

    def test_benchmark_endpoint(self):
        """Verifies live empirical benchmark execution with valid iterations."""
        response = self.client.post(
            "/api/benchmark",
            data=json.dumps({"text": "15-03-2026 ERROR 192.168.1.1", "iterations": 15}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "success")
        self.assertIn("workload_a_re_error_us", data)
        self.assertIn("workload_a_dfa_error_us", data)
        self.assertIn("workload_b_re_all_5_us", data)
        self.assertGreater(data["workload_a_re_error_us"]["mean_us"], 0)

    def test_api_validation_non_json(self):
        """Verifies that non-JSON requests are rejected with 400 Bad Request."""
        response = self.client.post("/api/analyze/re", data="plain text not json")
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("error", data)

    def test_api_validation_non_string_field(self):
        """Verifies that non-string 'text' fields are rejected with 400 Bad Request."""
        response = self.client.post(
            "/api/analyze/dfa",
            data=json.dumps({"text": 12345}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_api_validation_payload_too_large(self):
        """Verifies that inputs exceeding MAX_PAYLOAD_CHARS are rejected with 413."""
        huge_text = "E" * (MAX_PAYLOAD_CHARS + 10)
        response = self.client.post(
            "/api/analyze/re",
            data=json.dumps({"text": huge_text}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 413)

    def test_get_static_assets(self):
        """Verifies that static assets (styles.css and app.js) and /index.html are served properly."""
        with self.client.get("/styles.css") as resp_css:
            self.assertEqual(resp_css.status_code, 200)
            self.assertIn("text/css", resp_css.headers.get("Content-Type", ""))
            self.assertIn(b"--bg-base", resp_css.data)

        with self.client.get("/app.js") as resp_js:
            self.assertEqual(resp_js.status_code, 200)
            self.assertIn("application/javascript", resp_js.headers.get("Content-Type", ""))
            self.assertIn(b"runEquivalenceComparison", resp_js.data)

        with self.client.get("/index.html") as resp_idx:
            self.assertEqual(resp_idx.status_code, 200)
            self.assertIn(b"Log File Analysis Engine", resp_idx.data)

    def test_security_headers(self):
        """Verifies that production security headers are injected on responses."""
        with self.client.get("/") as resp:
            self.assertEqual(resp.headers.get("X-Content-Type-Options"), "nosniff")
            self.assertEqual(resp.headers.get("X-Frame-Options"), "SAMEORIGIN")
            self.assertEqual(resp.headers.get("Referrer-Policy"), "strict-origin-when-cross-origin")

    def test_dfa_trace_boundary_cases(self):
        """Verifies step-by-step trace generation on boundary rejection cases."""
        resp_prefix = self.client.post(
            "/api/dfa/trace",
            data=json.dumps({"token": "_ERROR"}),
            content_type="application/json",
        )
        self.assertEqual(resp_prefix.status_code, 200)
        self.assertEqual(resp_prefix.get_json()["total_matches"], 0)

        resp_suffix = self.client.post(
            "/api/dfa/trace",
            data=json.dumps({"token": "ERROR_"}),
            content_type="application/json",
        )
        self.assertEqual(resp_suffix.status_code, 200)
        self.assertEqual(resp_suffix.get_json()["total_matches"], 0)

    def test_benchmark_validation(self):
        """Verifies benchmark parameter constraints and error responses."""
        resp_low = self.client.post(
            "/api/benchmark",
            data=json.dumps({"text": "sample", "iterations": 5}),
            content_type="application/json",
        )
        self.assertEqual(resp_low.status_code, 400)

        resp_empty = self.client.post(
            "/api/benchmark",
            data=json.dumps({"text": "   ", "iterations": 20}),
            content_type="application/json",
        )
        self.assertEqual(resp_empty.status_code, 400)


if __name__ == "__main__":
    unittest.main(verbosity=2)
