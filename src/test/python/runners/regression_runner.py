import sys

import pytest


def main() -> int:
    return pytest.main(["--suite=regression", *sys.argv[1:]])


if __name__ == "__main__":
    raise SystemExit(main())