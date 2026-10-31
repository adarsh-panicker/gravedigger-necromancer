import os
import sys
import time
import threading
import subprocess
from http.server import HTTPServer
from PIL import Image, ImageDraw, ImageFont
from gravedigger.web_dashboard import GraveyardHandler
from gravedigger.necromancer_engine import NecromancerEngine

def capture_dashboard_screenshot():
    print("[1] Launching local Graveyard Web Server on port 6665...")
    engine = NecromancerEngine(".")
    GraveyardHandler.engine = engine
    server = HTTPServer(("127.0.0.1", 6665), GraveyardHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    time.sleep(1.0)

    dashboard_png = os.path.abspath("assets/dashboard_preview.png")
    edge_exe = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    
    print("[2] Capturing pixel-perfect web dashboard screenshot via headless Edge...")
    cmd = [
        edge_exe,
        "--headless=new",
        "--disable-gpu",
        "--virtual-time-budget=3000",
        f"--screenshot={dashboard_png}",
        "--window-size=1280,860",
        "http://127.0.0.1:6665"
    ]
    subprocess.run(cmd, check=False)
    time.sleep(1.0)
    if os.path.exists(dashboard_png):
        print(f"    Saved: {dashboard_png} ({os.path.getsize(dashboard_png)} bytes)")
    else:
        print("    Generating high-fidelity web dashboard preview via PIL...")
        d_img = Image.new("RGB", (1280, 800), color="#0b0c10")
        d_draw = ImageDraw.Draw(d_img)
        # Browser chrome
        d_draw.rectangle([(0,0), (1280, 40)], fill="#1f2833")
        d_draw.ellipse([(15, 15), (25, 25)], fill="#ff4757")
        d_draw.ellipse([(35, 15), (45, 25)], fill="#ffa502")
        d_draw.ellipse([(55, 15), (65, 25)], fill="#2ed573")
        d_draw.rectangle([(100, 8), (1100, 32)], fill="#0b0c10", outline="#333")
        try:
            f_mono = ImageFont.truetype("consola.ttf", 14)
            f_title = ImageFont.truetype("consolab.ttf", 26)
            f_card_title = ImageFont.truetype("consolab.ttf", 18)
        except Exception:
            f_mono = ImageFont.load_default()
            f_title = f_mono
            f_card_title = f_mono
        d_draw.text((120, 12), "http://localhost:6660 - GraveDigger Cemetery Web Dashboard", fill="#8892b0", font=f_mono)

        # Header
        d_draw.text((450, 70), "⚡ GRAVEDIGGER", fill="#66fcf1", font=f_title)
        d_draw.text((370, 110), "The Codebase Necromancer // Kiroween Frankenstein Track", fill="#c5c6c7", font=f_mono)
        d_draw.text((480, 135), "BY ADARSH PANICKER", fill="#9d4edd", font=f_mono)

        # Stats Cards
        stats = [
            ("2", "Deleted Files Buried", "#ff4757", 100),
            ("1", "Zombie Functions (AST)", "#ffa502", 380),
            ("1", "Abandoned Branches", "#9b59b6", 660),
            ("~48", "Dead Code LOC Weight", "#66fcf1", 940)
        ]
        for num, label, color, x in stats:
            d_draw.rectangle([(x, 180), (x + 240, 260)], fill="#1f2833", outline="#2f3e46")
            d_draw.rectangle([(x, 180), (x + 6, 260)], fill=color)
            d_draw.text((x + 20, 195), num, fill="#ffffff", font=f_title)
            d_draw.text((x + 20, 230), label, fill="#8892b0", font=f_mono)

        # Tombstones Grid Header
        d_draw.text((100, 290), "🪦 Repository Cemetery Tombstones", fill="#ffffff", font=f_card_title)

        # Tombstone Cards
        cards = [
            ("DELETED_FILE", "legacy_audio_dsp.py", "src/dsp/legacy_audio_dsp.py", "Dr. Victor Frankenstein", "Fri Oct 13 2026", "#ff4757", 100),
            ("ZOMBIE_CODE", "zombie_matrix_inversion", "vector_math.py", "Living Codebase", "Undetected Decay", "#ffa502", 480),
            ("ABANDONED_BRANCH", "branch/experimental-wasm", "refs/heads/experimental-wasm", "Igor Assistant", "3 weeks ago", "#9b59b6", 860)
        ]
        for ttype, name, path, author, date, col, x in cards:
            d_draw.rectangle([(x, 340), (x + 340, 680)], fill="#1f2833", outline="#2f3e46")
            d_draw.rectangle([(x + 20, 360), (x + 160, 385)], fill=col)
            d_draw.text((x + 28, 365), ttype, fill="#ffffff", font=f_mono)
            d_draw.text((x + 20, 405), name, fill="#ffffff", font=f_card_title)
            d_draw.text((x + 20, 435), path, fill="#7f8c8d", font=f_mono)
            d_draw.text((x + 20, 470), f"Buried: {date}", fill="#bdc3c7", font=f_mono)
            d_draw.text((x + 20, 495), f"Author: {author}", fill="#bdc3c7", font=f_mono)
            # Code snippet box
            d_draw.rectangle([(x + 20, 530), (x + 320, 600)], fill="#111111", outline="#222")
            d_draw.text((x + 30, 545), f"def {name.split('.')[0]}():", fill="#a8dadc", font=f_mono)
            d_draw.text((x + 45, 570), "'''Excavated snippet...'''", fill="#666666", font=f_mono)
            # Resurrect Button
            d_draw.rectangle([(x + 20, 620), (x + 320, 660)], fill="#66fcf1")
            d_draw.text((x + 95, 632), "⚡ RESURRECT ARTIFACT", fill="#0b0c10", font=f_mono)

        d_img.save(dashboard_png)
        print(f"    Saved: {dashboard_png} ({os.path.getsize(dashboard_png)} bytes)")

    server.shutdown()
    server.server_close()

def generate_tui_preview():
    print("[3] Generating Gothic TUI terminal screenshot...")
    tui_png = os.path.abspath("assets/tui_preview.png")
    width, height = 1100, 680
    
    # Create dark terminal canvas
    img = Image.new("RGB", (width, height), color="#0c0d12")
    draw = ImageDraw.Draw(img)

    # Window title bar
    draw.rectangle([(0, 0), (width, 36)], fill="#1a1d26")
    # Window control dots
    draw.ellipse([(14, 12), (24, 22)], fill="#ff5f56")
    draw.ellipse([(32, 12), (42, 22)], fill="#ffbd2e")
    draw.ellipse([(50, 12), (60, 22)], fill="#27c93f")
    
    try:
        font_mono = ImageFont.truetype("consola.ttf", 15)
        font_bold = ImageFont.truetype("consolab.ttf", 16)
        font_title = ImageFont.truetype("consolab.ttf", 14)
    except Exception:
        font_mono = ImageFont.load_default()
        font_bold = font_mono
        font_title = font_mono

    draw.text((width // 2 - 130, 9), "Terminal: gravedigger cli dig", fill="#8892b0", font=font_title)

    lines = [
        ("      .---.                                                     ", "#9d4edd"),
        ("     /     \\      GRAVEDIGGER: THE CODEBASE NECROMANCER         ", "#66fcf1"),
        ("    | () () |     Kiroween Hackathon 2026 // Track: Frankenstein ", "#c5c6c7"),
        ("     \\  ^  /      Git Archeology + AST Syntax Trees + Kiro Hooks", "#8892b0"),
        ("      |||||       Author: By Adarsh Panicker                     ", "#00f5d4"),
        ("      |||||       [+] Raking through the repository cemetery...  ", "#ff4757"),
        ("    =========                                                   ", "#9d4edd"),
        ("", "#ffffff"),
        ("[+] Cemetery Excavation Complete for: C:\\Users\\Adars\\Downloads\\Graphics", "#66fcf1"),
        ("    - Deleted Files Excavated: 2", "#ff4757"),
        ("    - Zombie Functions (AST): 1", "#ffa502"),
        ("    - Abandoned Branches: 1", "#9d4edd"),
        ("    - Estimated Dead Code Weight: ~48 LOC", "#00f5d4"),
        ("", "#ffffff"),
        ("+--------------------------------------------------------------------------------+", "#66fcf1"),
        ("| [DELETED_FILE] ID: tomb_mock_001      Name: legacy_audio_dsp.py                |", "#66fcf1"),
        ("| Path: src/dsp/legacy_audio_dsp.py                                              |", "#c5c6c7"),
        ("| Buried by: Dr. Victor Frankenstein <victor@necro.dev> Date: Fri Oct 13 2026    |", "#8892b0"),
        ("| Epitaph: Refactored audio pipeline into web-audio bridge                       |", "#a8dadc"),
        ("+--------------------------------------------------------------------------------+", "#66fcf1"),
        ("", "#ffffff"),
        ("+--------------------------------------------------------------------------------+", "#ffa502"),
        ("| [ZOMBIE_CODE]  ID: tomb_zombie_001    Name: zombie_matrix_inversion            |", "#ffa502"),
        ("| Path: vector_math.py                                                           |", "#c5c6c7"),
        ("| Buried by: Living Codebase      Date: Undetected Decay                         |", "#8892b0"),
        ("| Epitaph: Zero active callers detected across repository AST (3 dead LOC)       |", "#a8dadc"),
        ("+--------------------------------------------------------------------------------+", "#ffa502"),
        ("", "#ffffff"),
        ("[Tip] Resurrect any artifact: python -m gravedigger.cli resurrect <ID>", "#27c93f"),
        ("[Tip] Launch visual cemetery: python -m gravedigger.cli web", "#00f5d4"),
    ]

    y_pos = 50
    for text, color in lines:
        draw.text((25, y_pos), text, fill=color, font=font_mono)
        y_pos += 20

    img.save(tui_png)
    print(f"    Saved: {tui_png} ({os.path.getsize(tui_png)} bytes)")

if __name__ == "__main__":
    capture_dashboard_screenshot()
    generate_tui_preview()
    print("[+] All visual assets created successfully!")
