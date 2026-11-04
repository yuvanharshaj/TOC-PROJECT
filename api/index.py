"""
Vercel Serverless Entrypoint for TOC SET-E Case Study Flask App.
Imports and exposes the WSGI app instance for serverless edge execution.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.web_api import app
