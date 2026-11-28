import os
import json
import tempfile
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from .necromancer_engine import NecromancerEngine
from .github_scanner import GitHubRepoScanner, parse_github_repo, scan_pasted_code
from .models import ResurrectionResult

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GraveDigger: Codebase Cemetery Dashboard</title>
    <style>
        :root {
            --bg-color: #0b0c10;
            --card-bg: #1f2833;
            --accent-green: #66fcf1;
            --accent-cyan: #45a29e;
            --tomb-red: #ff4757;
            --tomb-gold: #ffa502;
            --tomb-purple: #9b59b6;
            --text-main: #c5c6c7;
            --text-bright: #ffffff;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', system-ui, sans-serif; }
        body {
            background-color: #14110b;
            color: var(--text-main);
            padding: 30px 20px;
            min-height: 100vh;
            background-image:
                radial-gradient(circle at 12% 18%, rgba(255, 71, 87, 0.38), transparent 45%),
                radial-gradient(circle at 88% 22%, rgba(46, 213, 115, 0.34), transparent 45%),
                radial-gradient(circle at 50% 85%, rgba(255, 195, 18, 0.32), transparent 50%),
                linear-gradient(135deg, #2d0a10 0%, #0d2617 50%, #2b2207 100%);
            background-attachment: fixed;
        }
        .container { max-width: 1100px; margin: 0 auto; }
        header {
            text-align: center;
            margin-bottom: 40px;
            border-bottom: 1px solid #333;
            padding-bottom: 25px;
        }
        .logo { font-size: 2.6rem; color: var(--accent-green); font-weight: 800; letter-spacing: 2px; }
        .tagline { color: #888; font-size: 1.05rem; margin-top: 6px; }
        .badge {
            display: inline-block;
            background: #222;
            color: var(--accent-cyan);
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            margin-top: 10px;
            border: 1px solid var(--accent-cyan);
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 20px;
            margin-bottom: 35px;
        }
        .stat-card {
            background: var(--card-bg);
            border-radius: 12px;
            padding: 20px;
            border-left: 4px solid var(--accent-green);
            box-shadow: 0 4px 20px rgba(0,0,0,0.5);
        }
        .stat-num { font-size: 2.2rem; font-weight: bold; color: var(--text-bright); }
        .stat-label { font-size: 0.9rem; color: #aaa; text-transform: uppercase; letter-spacing: 1px; }

        .cemetery-section h2 {
            font-size: 1.6rem;
            color: var(--text-bright);
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .tombstone-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(330px, 1fr));
            gap: 20px;
        }
        .tomb-card {
            background: var(--card-bg);
            border-radius: 12px;
            border: 1px solid #2f3e46;
            padding: 20px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: transform 0.2s, border-color 0.2s;
            box-shadow: 0 6px 15px rgba(0,0,0,0.4);
        }
        .tomb-card:hover {
            transform: translateY(-4px);
            border-color: var(--accent-green);
        }
        .tomb-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }
        .tomb-type {
            font-size: 0.75rem;
            font-weight: bold;
            padding: 3px 8px;
            border-radius: 4px;
            text-transform: uppercase;
        }
        .type-deleted { background: rgba(255, 71, 87, 0.2); color: var(--tomb-red); border: 1px solid var(--tomb-red); }
        .type-zombie { background: rgba(255, 165, 2, 0.2); color: var(--tomb-gold); border: 1px solid var(--tomb-gold); }
        .type-branch { background: rgba(155, 89, 182, 0.2); color: var(--tomb-purple); border: 1px solid var(--tomb-purple); }

        .tomb-title { font-size: 1.25rem; font-weight: bold; color: var(--text-bright); word-break: break-all; }
        .tomb-path { font-size: 0.85rem; color: #7f8c8d; margin-top: 4px; font-family: monospace; }
        .tomb-meta { margin: 14px 0; font-size: 0.85rem; line-height: 1.5; color: #bdc3c7; }
        .code-snippet {
            background: #111;
            padding: 10px;
            border-radius: 6px;
            font-family: monospace;
            font-size: 0.8rem;
            overflow-x: auto;
            max-height: 110px;
            color: #a8dadc;
            margin-bottom: 15px;
            white-space: pre;
        }
        .btn-resurrect {
            background: linear-gradient(135deg, var(--accent-green), var(--accent-cyan));
            color: #0b0c10;
            border: none;
            padding: 10px 16px;
            font-weight: bold;
            border-radius: 6px;
            cursor: pointer;
            width: 100%;
            transition: opacity 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }
        .btn-resurrect:hover { opacity: 0.9; }

        /* Modal */
        .modal {
            display: none;
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.85);
            align-items: center;
            justify-content: center;
            z-index: 999;
        }
        .modal-content {
            background: #161b22;
            border: 1px solid var(--accent-green);
            padding: 25px;
            border-radius: 10px;
            max-width: 650px;
            width: 90%;
            box-shadow: 0 0 30px rgba(102, 252, 241, 0.2);
        }
        .modal-title { color: var(--accent-green); font-size: 1.4rem; margin-bottom: 12px; }
        .modal-diff { background: #000; padding: 12px; border-radius: 6px; font-family: monospace; font-size: 0.85rem; max-height: 250px; overflow-y: auto; white-space: pre; color: #2ecc71; margin: 15px 0; }
        .btn-close { background: #333; color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; float: right; }

        /* Interactive Scanner Bar */
        .scanner-panel {
            background: rgba(20, 24, 31, 0.9);
            border: 1px solid #2f3e46;
            border-radius: 12px;
            padding: 18px 20px;
            margin-bottom: 28px;
            box-shadow: 0 6px 20px rgba(0,0,0,0.45);
        }
        .scanner-row {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            align-items: center;
        }
        .scanner-input {
            flex: 1;
            min-width: 260px;
            background: #0d1117;
            border: 1px solid #30363d;
            color: #fff;
            padding: 10px 14px;
            border-radius: 8px;
            font-size: 0.95rem;
            outline: none;
        }
        .scanner-input:focus { border-color: var(--accent-green); }
        .btn-scan {
            background: linear-gradient(135deg, var(--accent-green), var(--accent-cyan));
            color: #0b0c10;
            border: none;
            padding: 10px 18px;
            border-radius: 8px;
            font-weight: 700;
            cursor: pointer;
            font-size: 0.92rem;
        }
        .btn-scan:hover { opacity: 0.9; }
        .btn-secondary {
            background: #232a34;
            color: #e6edf3;
            border: 1px solid #3b4654;
            padding: 10px 14px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.88rem;
        }
        .btn-secondary:hover { border-color: var(--accent-green); }
        .quick-pills {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            align-items: center;
            margin-top: 12px;
            font-size: 0.82rem;
            color: #9aa5b1;
        }
        .pill-btn {
            background: rgba(102, 252, 241, 0.1);
            color: var(--accent-green);
            border: 1px solid rgba(102, 252, 241, 0.35);
            padding: 4px 10px;
            border-radius: 999px;
            cursor: pointer;
            font-size: 0.8rem;
        }
        .pill-btn:hover { background: rgba(102, 252, 241, 0.22); }
        .paste-box {
            display: none;
            margin-top: 14px;
            border-top: 1px solid #2b323d;
            padding-top: 14px;
        }
        .code-textarea {
            width: 100%;
            min-height: 150px;
            background: #0b0e14;
            color: #a8dadc;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 12px;
            font-family: 'Courier New', monospace;
            font-size: 0.86rem;
            resize: vertical;
            margin-bottom: 10px;
        }
        .scan-status {
            margin-top: 10px;
            font-size: 0.86rem;
            color: #9ecbff;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="logo">⚡ GRAVEDIGGER</div>
            <div class="tagline">The Codebase Necromancer // Kiroween Frankenstein Track</div>
            <div class="badge" style="background: rgba(155, 89, 182, 0.3); border-color: #9b59b6; color: #ffffff; font-weight: bold;">
                BY ADARSH PANICKER
            </div>
            <br>
            <div class="badge" style="margin-top: 6px;">Powered by Git Plumbing + AST Syntax Trees + Kiro Hooks</div>
        </header>

        <div class="scanner-panel">
            <div class="scanner-row">
                <input id="repo-input" class="scanner-input" type="text" placeholder="Paste any public GitHub repo URL (e.g. https://github.com/pallets/flask) or leave blank for local...">
                <button class="btn-scan" onclick="scanGitHubRepo()">⛏️ Excavate GitHub Repo</button>
                <button class="btn-secondary" onclick="togglePasteBox()">📝 Paste Python Code</button>
            </div>
            <div class="quick-pills">
                <span>Try live targets:</span>
                <button class="pill-btn" onclick="quickScan('pallets/flask')">pallets/flask</button>
                <button class="pill-btn" onclick="quickScan('psf/requests')">psf/requests</button>
                <button class="pill-btn" onclick="quickScan('fastapi/fastapi')">fastapi/fastapi</button>
                <button class="pill-btn" onclick="quickScan('local')">Local GraveDigger</button>
            </div>
            <div class="paste-box" id="paste-box">
                <textarea id="code-input" class="code-textarea">def active_helper(x):
    return x * 2

def forgotten_zombie_parser(payload):
    # Legacy parser left behind after v2 migration.
    return {"parsed": payload}

print(active_helper(21))</textarea>
                <button class="btn-scan" onclick="scanPastedCode()">🧟 Scan Pasted Python Code</button>
            </div>
            <div class="scan-status" id="scan-status">Target: Local GraveDigger Repository</div>
        </div>

        <div class="stats-grid">
            <div class="stat-card" style="border-left-color: var(--tomb-red);">
                <div class="stat-num" id="stat-deleted">0</div>
                <div class="stat-label">Deleted Files Buried</div>
            </div>
            <div class="stat-card" style="border-left-color: var(--tomb-gold);">
                <div class="stat-num" id="stat-zombies">0</div>
                <div class="stat-label">Zombie Functions (AST)</div>
            </div>
            <div class="stat-card" style="border-left-color: var(--tomb-purple);">
                <div class="stat-num" id="stat-branches">0</div>
                <div class="stat-label">Abandoned Branches</div>
            </div>
            <div class="stat-card" style="border-left-color: var(--accent-green);">
                <div class="stat-num" id="stat-loc">~0</div>
                <div class="stat-label">Dead Code LOC Weight</div>
            </div>
        </div>

        <section class="cemetery-section">
            <h2>🪦 Repository Cemetery Tombstones</h2>
            <div class="tombstone-grid" id="tombstones-container">
                <!-- Dynamically populated -->
            </div>
        </section>
    </div>

    <div class="modal" id="resurrect-modal">
        <div class="modal-content">
            <h3 class="modal-title">⚡ Ritual Complete: Code Resurrected!</h3>
            <p id="modal-msg" style="color: #ccc; font-size: 0.95rem;"></p>
            <div class="modal-diff" id="modal-diff"></div>
            <p style="font-size: 0.85rem; color: #888;">Generated Unified Patch saved into <code>resurrected/</code> directory.</p>
            <button class="btn-close" onclick="closeModal()">Close</button>
        </div>
    </div>

    <script>
        let currentTarget = 'local';

        function togglePasteBox() {
            const box = document.getElementById('paste-box');
            box.style.display = box.style.display === 'block' ? 'none' : 'block';
        }

        function quickScan(target) {
            if (target === 'local') {
                document.getElementById('repo-input').value = '';
                loadCemetery('local');
            } else {
                document.getElementById('repo-input').value = 'https://github.com/' + target;
                scanGitHubRepo();
            }
        }

        function scanGitHubRepo() {
            const val = document.getElementById('repo-input').value.trim();
            loadCemetery(val || 'local');
        }

        async function scanPastedCode() {
            const code = document.getElementById('code-input').value;
            const status = document.getElementById('scan-status');
            status.innerText = 'Scanning pasted Python AST for zombie functions...';
            try {
                const res = await fetch('/api/scan-code', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ code, filename: 'pasted_snippet.py' })
                });
                const data = await res.json();
                if (data.error) {
                    status.innerText = 'Error: ' + data.error;
                    return;
                }
                currentTarget = 'custom';
                renderDashboard(data);
                status.innerText = 'Target: Custom Pasted Python Code (' + data.total_tombstones + ' tombstones found)';
            } catch (e) {
                status.innerText = 'Scan failed: ' + e;
            }
        }

        async function loadCemetery(repo = 'local') {
            const status = document.getElementById('scan-status');
            status.innerText = repo === 'local'
                ? 'Excavating Local GraveDigger Repository...'
                : 'Excavating GitHub repository ' + repo + ' (Git commits + Python AST)...';
            try {
                const url = repo && repo !== 'local'
                    ? '/api/graveyard?repo=' + encodeURIComponent(repo)
                    : '/api/graveyard';
                const res = await fetch(url);
                const data = await res.json();
                if (data.error) {
                    status.innerText = 'Error: ' + data.error;
                    return;
                }
                currentTarget = repo || 'local';
                renderDashboard(data);
                status.innerText = 'Target: ' + data.repo_path + ' (' + data.total_tombstones + ' tombstones found)';
            } catch (e) {
                status.innerText = 'Failed to load cemetery: ' + e;
            }
        }

        function renderDashboard(data) {
            document.getElementById('stat-deleted').innerText = data.deleted_files_count;
            document.getElementById('stat-zombies').innerText = data.zombie_functions_count;
            document.getElementById('stat-branches').innerText = data.abandoned_branches_count;
            document.getElementById('stat-loc').innerText = `~${data.dead_loc}`;

            const container = document.getElementById('tombstones-container');
            container.innerHTML = '';
            window._tombstoneMap = {};

            if (!data.tombstones || data.tombstones.length === 0) {
                container.innerHTML = '<div style="color:#aaa; padding:20px;">No dead files or unreferenced zombie functions detected in this target!</div>';
                return;
            }

            data.tombstones.forEach(t => {
                window._tombstoneMap[t.id] = { tombstone: t, repo_path: data.repo_path };
                const card = document.createElement('div');
                card.className = 'tomb-card';
                
                let badgeClass = 'type-deleted';
                if (t.artifact_type.includes('ZOMBIE')) badgeClass = 'type-zombie';
                if (t.artifact_type.includes('BRANCH')) badgeClass = 'type-branch';

                card.innerHTML = `
                    <div>
                        <div class="tomb-header">
                            <span class="tomb-type ${badgeClass}">${t.artifact_type}</span>
                            <span style="font-size: 0.75rem; color: #666;">${t.id}</span>
                        </div>
                        <div class="tomb-title">${t.name}</div>
                        <div class="tomb-path">${t.path}</div>
                        <div class="tomb-meta">
                            <strong>Buried:</strong> ${t.death_date}<br>
                            <strong>Author:</strong> ${t.author}<br>
                            <strong>Cause:</strong> ${t.cause_of_death}
                        </div>
                        <div class="code-snippet">${t.content_snippet}</div>
                    </div>
                    <button class="btn-resurrect" onclick="resurrectTombstone('${t.id}')">
                        ⚡ Resurrect Artifact
                    </button>
                `;
                container.appendChild(card);
            });
        }

        async function resurrectTombstone(id) {
            const meta = (window._tombstoneMap && window._tombstoneMap[id]) || {};
            const res = await fetch(`/api/resurrect?id=${encodeURIComponent(id)}&target=${encodeURIComponent(currentTarget)}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(meta)
            });
            const data = await res.json();
            
            document.getElementById('modal-msg').innerText = data.message;
            document.getElementById('modal-diff').innerText = data.diff_preview;
            document.getElementById('resurrect-modal').style.display = 'flex';
        }

        function closeModal() {
            document.getElementById('resurrect-modal').style.display = 'none';
        }

        loadCemetery('local');
    </script>
</body>
</html>
"""

class GraveyardHandler(BaseHTTPRequestHandler):
    engine: NecromancerEngine = None
    remote_cache: dict = {}

    def _get_engine(self) -> NecromancerEngine:
        if GraveyardHandler.engine is None:
            repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            GraveyardHandler.engine = NecromancerEngine(repo_root)
        return GraveyardHandler.engine

    def _send_json(self, payload: dict, status: int = 200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode("utf-8"))

    def log_message(self, format, *args):
        # Quiet standard HTTP access logs
        return

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path in ["/", "/index.html"]:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode("utf-8"))

        elif parsed.path == "/api/graveyard":
            query = parse_qs(parsed.query)
            repo_param = query.get("repo", [""])[0].strip()
            if not repo_param or repo_param == "local":
                report = self._get_engine().run_excavation()
                self._send_json(report.to_dict())
                return

            parsed_repo = parse_github_repo(repo_param)
            if not parsed_repo:
                self._send_json({"error": "Invalid GitHub URL. Use format: https://github.com/owner/repo"}, status=400)
                return

            owner, repo_name = parsed_repo
            try:
                report, blobs = GitHubRepoScanner(owner, repo_name).run_excavation()
                GraveyardHandler.remote_cache[repo_param] = {"report": report, "blobs": blobs}
                self._send_json(report.to_dict())
            except Exception as exc:
                self._send_json({"error": f"Could not scan {owner}/{repo_name}: {exc}"}, status=502)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/scan-code":
            length = int(self.headers.get("Content-Length", "0"))
            raw_body = self.rfile.read(length).decode("utf-8", errors="replace") if length > 0 else "{}"
            try:
                body = json.loads(raw_body)
            except json.JSONDecodeError:
                self._send_json({"error": "Invalid JSON payload"}, status=400)
                return
            code = body.get("code", "")
            filename = body.get("filename", "pasted_snippet.py")
            if not code.strip():
                self._send_json({"error": "Please paste Python code to scan."}, status=400)
                return
            report, blobs = scan_pasted_code(code, filename=filename)
            GraveyardHandler.remote_cache["custom"] = {"report": report, "blobs": blobs}
            self._send_json(report.to_dict())

        elif parsed.path == "/api/resurrect":
            query = parse_qs(parsed.query)
            tombstone_id = query.get("id", [""])[0]
            target = query.get("target", ["local"])[0]

            length = int(self.headers.get("Content-Length", "0"))
            body = {}
            if length > 0:
                try:
                    body = json.loads(self.rfile.read(length).decode("utf-8", errors="replace"))
                except Exception:
                    body = {}

            if target != "local":
                tomb_obj = None
                repo_label = body.get("repo_path", target)
                raw_src = None
                if target in GraveyardHandler.remote_cache:
                    cached = GraveyardHandler.remote_cache[target]
                    tomb_obj = next((t for t in cached["report"].tombstones if t.id == tombstone_id), None)
                    if tomb_obj:
                        raw_src = cached["blobs"].get(tombstone_id, tomb_obj.content_snippet)
                        repo_label = cached["report"].repo_path
                elif body.get("tombstone"):
                    td = body["tombstone"]
                    from .models import Tombstone
                    tomb_obj = Tombstone(
                        id=td.get("id", tombstone_id),
                        artifact_type=td.get("artifact_type", "ZOMBIE_CODE"),
                        name=td.get("name", tombstone_id),
                        path=td.get("path", "recovered.py"),
                        death_commit=td.get("death_commit", "HEAD"),
                        author=td.get("author", "Unknown"),
                        death_date=td.get("death_date", "Unknown"),
                        cause_of_death=td.get("cause_of_death", ""),
                        content_snippet=td.get("content_snippet", ""),
                    )
                    raw_src = tomb_obj.content_snippet

                if tomb_obj:
                    resurrected_content = (
                        f"# ====================================================================\n"
                        f"# RESURRECTED ARTIFACT: {tomb_obj.name}\n"
                        f"# Original Path: {tomb_obj.path}\n"
                        f"# Source: {repo_label}\n"
                        f"# Raised by: GraveDigger (Kiroween Necromancer Engine)\n"
                        f"# ====================================================================\n\n"
                        f"{raw_src}\n"
                    )
                    lines = resurrected_content.splitlines()
                    patch_lines = [
                        "--- /dev/null",
                        f"+++ b/{tomb_obj.path}",
                        f"@@ -0,0 +1,{len(lines)} @@",
                    ] + [f"+{line}" for line in lines]
                    patch_text = "\n".join(patch_lines)
                    out_dir = os.path.join(tempfile.gettempdir(), "gravedigger_resurrected")
                    os.makedirs(out_dir, exist_ok=True)
                    safe_name = os.path.basename(tomb_obj.path)
                    out_path = os.path.join(out_dir, safe_name)
                    patch_path = os.path.join(out_dir, f"{safe_name}.patch")
                    with open(out_path, "w", encoding="utf-8") as f:
                        f.write(resurrected_content)
                    with open(patch_path, "w", encoding="utf-8") as pf:
                        pf.write(patch_text)
                    res = ResurrectionResult(
                        tombstone_id=tomb_obj.id,
                        success=True,
                        resurrected_path=out_path,
                        patch_path=patch_path,
                        diff_preview=patch_text[:1000],
                        message=f"Successfully resurrected '{tomb_obj.name}' from {repo_label}!",
                    )
                    self._send_json(res.to_dict())
                    return

            result = self._get_engine().resurrect_tombstone(tombstone_id)
            self._send_json(result.to_dict())
        else:
            self.send_response(404)
            self.end_headers()

def launch_graveyard_server(repo_path: str = ".", port: int = 6660):
    env_port = os.environ.get("PORT")
    bind_port = int(env_port) if env_port else port
    bind_host = "0.0.0.0" if env_port else "127.0.0.1"
    engine = NecromancerEngine(repo_path)
    GraveyardHandler.engine = engine
    server = HTTPServer((bind_host, bind_port), GraveyardHandler)
    url = f"http://{bind_host}:{bind_port}"
    print(f"\n[+] GraveDigger Cemetery Web Dashboard active at: {url}")
    if not env_port:
        print("[+] Press Ctrl+C to close server.\n")
        try:
            webbrowser.open(url)
        except Exception:
            pass
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[+] Graveyard Dashboard closed.")
        server.server_close()
