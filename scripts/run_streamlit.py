#!/usr/bin/env python3
"""Script para ejecutar la aplicación Streamlit."""

import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":
    # Obtener el directorio del proyecto
    project_root = Path(__file__).parent.parent
    streamlit_app = project_root / "streamlit_app" / "main.py"
    
    # Ejecutar Streamlit
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", str(streamlit_app),
        "--server.port", "8501",
        "--server.address", "localhost"
    ])

