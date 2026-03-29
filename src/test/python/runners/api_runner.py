import sys

import pytest

if __name__ == "__main__":
    args = [
        "src/test/python",
        "--suite=api",
    ]

    args.extend(sys.argv[1:])

    raise SystemExit(pytest.main(args))
