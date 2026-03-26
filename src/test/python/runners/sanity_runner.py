import sys

import pytest


if __name__ == "__main__":
    args = [
        "--suite=sanity",
    ]

    args.extend(sys.argv[1:])

    raise SystemExit(pytest.main(args))