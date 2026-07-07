# run notebook from terminal if you dont want to open jupyter gui
# python run_notebook.py notebooks/random_forest.ipynb

import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python run_notebook.py notebooks/your_model.ipynb")
        sys.exit(1)

    nb = Path(sys.argv[1])
    subprocess.run([
        sys.executable, "-m", "jupyter", "nbconvert",
        "--execute", str(nb),
        "--to", "notebook",
        "--output", nb.stem + "_executed.ipynb",
        "--output-dir", str(nb.parent),
    ], check=True)
