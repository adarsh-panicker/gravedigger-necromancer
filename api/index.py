import os
import sys

# Ensure repository root is on sys.path for serverless runtime
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from gravedigger.web_dashboard import GraveyardHandler


class handler(GraveyardHandler):
    """Vercel Serverless HTTP entrypoint for GraveDigger Cemetery Web Dashboard."""
    pass
