# opens streamlit on port 8501

import subprocess
import sys

if __name__ == "__main__":
    print("demo -> http://localhost:8501")
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", "ui/app.py",
        "--server.port", "8501",
        "--browser.gatherUsageStats", "false",
    ])
