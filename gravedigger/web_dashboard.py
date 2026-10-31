import os
import json
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from .necromancer_engine import NecromancerEngine

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
            background-color: var(--bg-color);
            color: var(--text-main);
            padding: 30px 20px;
            background-image: radial-gradient(#1f2833 1px, transparent 1px);
            background-size: 24px 24px;
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
        async function loadCemetery() {
            const res = await fetch('/api/graveyard');
            const data = await res.json();
            
            document.getElementById('stat-deleted').innerText = data.deleted_files_count;
            document.getElementById('stat-zombies').innerText = data.zombie_functions_count;
            document.getElementById('stat-branches').innerText = data.abandoned_branches_count;
            document.getElementById('stat-loc').innerText = `~${data.dead_loc}`;

            const container = document.getElementById('tombstones-container');
            container.innerHTML = '';

            data.tombstones.forEach(t => {
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
            const res = await fetch(`/api/resurrect?id=${id}`, { method: 'POST' });
            const data = await res.json();
            
            document.getElementById('modal-msg').innerText = data.message;
            document.getElementById('modal-diff').innerText = data.diff_preview;
            document.getElementById('resurrect-modal').style.display = 'flex';
        }

        function closeModal() {
            document.getElementById('resurrect-modal').style.display = 'none';
        }

        loadCemetery();
    </script>
</body>
</html>
"""

class GraveyardHandler(BaseHTTPRequestHandler):
    engine: NecromancerEngine = None

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
            report = self.engine.run_excavation()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(report.to_dict()).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/resurrect":
            query = parse_qs(parsed.query)
            tombstone_id = query.get("id", [""])[0]
            result = self.engine.resurrect_tombstone(tombstone_id)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result.to_dict()).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

def launch_graveyard_server(repo_path: str = ".", port: int = 6660):
    engine = NecromancerEngine(repo_path)
    GraveyardHandler.engine = engine
    server = HTTPServer(("127.0.0.1", port), GraveyardHandler)
    url = f"http://127.0.0.1:{port}"
    print(f"\n[+] GraveDigger Cemetery Web Dashboard active at: {url}")
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
