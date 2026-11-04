# TOC SET-E Case Study: Deployment & Hosting Guide
**Course Code:** 24CS52 — Theory of Computations (2026–2027)  
**Project:** Log File Analysis Using Regular Expressions and DFA  
**Live Application URL:** [https://toc-project-ruiv.vercel.app/](https://toc-project-ruiv.vercel.app/)  
**GitHub Repository:** [https://github.com/yuvanharshaj/TOC-PROJECT](https://github.com/yuvanharshaj/TOC-PROJECT)

---

## 1. Deployment Architecture & Hosting Requirements

### Architecture Overview
The application uses a **unified single-service architecture**:
- **Backend:** Python Flask 3.x REST API (`src/web_api.py`) exposing endpoints for the verified `REAnalyzer` (`src/re_analyzer.py`) and `DFAErrorScanner` (`src/dfa_analyzer.py`).
- **Frontend:** Responsive vanilla JavaScript, CSS3, and HTML5 client (`web/index.html`, `web/styles.css`, `web/app.js`) served directly from Flask's static handler.
- **Data:** Deterministic 30-entry sample log (`data/sample.log`).
- **Database:** None required. The service is completely stateless and compute-deterministic.

```
       [ Client Browser ]
               │
               ▼ HTTPS (Port 443 / $PORT)
  ┌────────────────────────────────────────────────────────┐
  │         PaaS Container (Render / Railway / Docker)     │
  │                                                        │
  │  Gunicorn WSGI Server (src.web_api:app)               │
  │    ├── Static Handler (GET /, /styles.css, /app.js)    │
  │    └── REST API (/api/analyze/*, /api/compare, etc.)   │
  │            │                                           │
  │            ├── REAnalyzer (Python re)                  │
  │            └── DFAErrorScanner (Manual 7-state DFA)    │
  └────────────────────────────────────────────────────────┘
```

### Hosting Requirements
| Requirement | Specification |
|:---|:---|
| **Python Version** | Python 3.10+ (Tested on Python 3.13.3) |
| **RAM** | < 120 MB operating footprint (Lightweight, well within free tiers of 512 MB) |
| **CPU** | 0.1–0.5 vCPU sufficient for sub-millisecond pattern matching |
| **Storage** | < 10 MB total repository size |
| **Outbound Network** | None required (zero external API or database calls) |
| **HTTPS/TLS** | Provided automatically by hosting PaaS (e.g. Render, Railway) |

---

## 2. Recommendation: Unified Frontend + API vs. Decoupled

### Recommended Strategy: Keep Frontend and API Together
We strongly recommend deploying the frontend and Flask API as a **single unified web service** rather than decoupling them into separate hosting platforms (e.g., Vercel + backend).

#### Key Reasons:
1. **Zero CORS & Origin Fragility:** Because static assets and `/api/*` endpoints reside on the exact same domain and port, cross-origin resource sharing errors, preflight `OPTIONS` latencies, and browser privacy blocking are completely eliminated.
2. **Atomic Versioning:** Any updates to API response payloads or DFA states in Python are instantly and synchronously in sync with the frontend client without deployment race conditions.
3. **Simplicity for Evaluation & Submission:** Evaluators and college faculty need only run or visit a single URL. No environment variables need to be configured to point the frontend to a disparate backend URL.
4. **Zero Build Step:** The frontend uses standard vanilla ES6+ and CSS3 without requiring Node.js, `npm run build`, or bundling dependencies on the hosting platform.

---

## 3. Production Configuration & Security Hardening

The application is pre-configured with defensive settings in `src/web_api.py`:

| Security / Performance Control | Implementation | Purpose |
|:---|:---|:---|
| **Debug Mode** | `os.environ.get("FLASK_DEBUG", "0")` (Defaults to `False`) | Prevents interactive debugger exposure and arbitrary code execution in production. |
| **HTTP Body Limit** | `app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024` (1 MB) | Protects against memory exhaustion / HTTP flood attacks at the WSGI level. |
| **JSON Input Limit** | `MAX_PAYLOAD_CHARS = 500_000` (500 KB characters) | Protects against excessive CPU consumption on oversized inputs. |
| **Security Headers** | Injected via `@app.after_request`: `X-Content-Type-Options: nosniff`, `X-Frame-Options: SAMEORIGIN`, `Referrer-Policy: strict-origin-when-cross-origin` | Mitigates MIME-sniffing, clickjacking, and referrer leakage. |
| **CORS Policy** | Fully enabled (`*`) for cross-origin testing while pre-handling `OPTIONS` with `204 No Content`. | Allows testing API endpoints from decoupled clients or tools like Postman/curl if needed. |
| **Zero Secrets Risk** | No database passwords, API tokens, or user credentials exist in the codebase. | Eliminates credential leak risks in Git. |

---

## 4. Production Deployment Platforms

### Option A: Vercel (Live Production - Recommended)
The application is live and hosted on Vercel at **[https://toc-project-ruiv.vercel.app/](https://toc-project-ruiv.vercel.app/)**.

#### Deployment Details:
- **Runtime:** Serverless Python (`@vercel/python`)
- **Configuration File:** `vercel.json`
- **Entrypoint:** `src/web_api.py` (Flask instance `app`)
- **Included Assets:** `web/**` (HTML, CSS, JS) and `data/**` (`sample.log`)
- **Routes:** `/(.*)` &rarr; `src/web_api.py`

#### Deploying to Vercel via CLI:
```powershell
# In the project root:
vercel --prod
```

### Option B: Render PaaS
The application is also pre-configured for containerized deployment on [Render](https://render.com) using the included `Procfile` and `render.yaml`.

#### Prerequisites:
- A GitHub repository containing this project folder.
- A free account at [render.com](https://render.com).

#### Step 1: Push Code to GitHub
```powershell
git add .
git commit -m "Prepare deployment configuration for TOC case study dashboard"
git push origin main
```

#### Step 2: Create Web Service on Render
1. Log into your Render Dashboard and click **"New +" &rarr; "Web Service"**.
2. Connect your GitHub repository containing the TOC Project.
3. Configure the following service settings:
   - **Name:** `toc-log-analyzer` (or your chosen name)
   - **Region:** Any region close to your location (e.g., Singapore, Frankfurt, Oregon)
   - **Branch:** `main`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn src.web_api:app`
   - **Instance Type:** `Free`
4. Click **"Deploy Web Service"**.

Render will automatically provision the container, install requirements, run `gunicorn`, and provide a free secure URL:  
`https://toc-log-analyzer.onrender.com`

---

## 5. Alternative Cloud Options

### Option B: Railway
1. Click **"New Project" &rarr; "Deploy from GitHub repo"**.
2. Railway detects the `Procfile` (`web: gunicorn src.web_api:app`) and `requirements.txt` automatically.
3. Generates a live URL under Settings &rarr; Networking.

### Option C: PythonAnywhere (Educational Hosting)
1. Upload the files to PythonAnywhere.
2. In the "Web" tab, create a manual Flask app.
3. Point the WSGI configuration file to:
   ```python
   import sys
   path = '/home/yourusername/TOC-PROJECT'
   if path not in sys.path:
       sys.path.insert(0, path)
   from src.web_api import app as application
   ```

---

## 6. Local Production Testing

To test the application locally in production mode without the Flask development server:

### Windows / Cross-Platform:
```powershell
# Using the standard runner:
python src\web_api.py
```

### Linux / Container / WSL (using Gunicorn):
```bash
gunicorn src.web_api:app --workers=2 --threads=4 --bind 0.0.0.0:5000
```

