import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
SRC_MAIN_PYTHON = PROJECT_ROOT / "src" / "main" / "python"
SRC_TEST_PYTHON = PROJECT_ROOT / "src" / "test" / "python"

for path in (SRC_MAIN_PYTHON, SRC_TEST_PYTHON):
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)