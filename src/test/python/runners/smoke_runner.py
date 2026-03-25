import sys

import pytest


def main() -> int:
    return pytest.main(["--suite=smoke", *sys.argv[1:]])


if __name__ == "__main__":
    raise SystemExit(main())