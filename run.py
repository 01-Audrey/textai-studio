#!/usr/bin/env python3
"""
TextAI Studio Launcher
Run this script to start the application.
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Launch the Streamlit app."""
    # Check Python version
    if sys.version_info < (3, 10):
        print("Error: Python 3.10 or higher is required")
        sys.exit(1)

    # Check if requirements are installed
    try:
        import streamlit
        import transformers
    except ImportError:
        print("Error: Dependencies not installed")
        print("Run: pip install -r requirements.txt")
        sys.exit(1)

    # Launch app
    app_path = Path(__file__).parent / "textai_studio_app.py"

    if not app_path.exists():
        print(f"Error: App file not found: {app_path}")
        sys.exit(1)

    print("🚀 Starting TextAI Studio...")
    subprocess.run([
        "streamlit", "run", str(app_path),
        "--server.port=8501",
        "--server.address=0.0.0.0"
    ])

if __name__ == "__main__":
    main()
