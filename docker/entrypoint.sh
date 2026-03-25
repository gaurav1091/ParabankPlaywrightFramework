#!/usr/bin/env bash
set -euo pipefail

mkdir -p /app/test-output/reports
mkdir -p /app/test-output/screenshots
mkdir -p /app/test-output/traces
mkdir -p /app/test-output/videos
mkdir -p /app/test-output/allure-results

SUITE="${SUITE:-smoke}"
TEST_ENV="${TEST_ENV:-qa}"
BROWSER="${BROWSER:-chrome}"
HEADLESS="${HEADLESS:-true}"
PYTEST_EXTRA_ARGS="${PYTEST_EXTRA_ARGS:-}"

if [ "$#" -gt 0 ]; then
  exec "$@"
fi

PYTEST_CMD=(
  python -m pytest
  "--suite=${SUITE}"
  "--env=${TEST_ENV}"
  "--framework-browser=${BROWSER}"
  "--framework-headless=${HEADLESS}"
)

if [ -n "${PYTEST_EXTRA_ARGS}" ]; then
  # shellcheck disable=SC2206
  EXTRA_ARGS=( ${PYTEST_EXTRA_ARGS} )
  PYTEST_CMD+=( "${EXTRA_ARGS[@]}" )
fi

echo "Running in Docker with:"
echo "  SUITE=${SUITE}"
echo "  TEST_ENV=${TEST_ENV}"
echo "  BROWSER=${BROWSER}"
echo "  HEADLESS=${HEADLESS}"
if [ -n "${PYTEST_EXTRA_ARGS}" ]; then
  echo "  PYTEST_EXTRA_ARGS=${PYTEST_EXTRA_ARGS}"
fi

exec "${PYTEST_CMD[@]}"