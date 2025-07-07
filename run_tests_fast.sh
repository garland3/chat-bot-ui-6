#!/bin/bash

# Fast test runner that skips slow browser tests
echo "Running fast test suite (excluding browser tests)..."

timeout 60s uv run pytest tests/ \
  --ignore=tests/test_frontend_basic_e2e.py \
  --ignore=tests/test_frontend_e2e_simple.py \
  --ignore=tests/test_debug_frontend.py \
  --timeout=30 \
  -v

if [ $? -eq 124 ]; then
    echo "Tests timed out after 60 seconds"
    exit 1
fi

echo "Fast tests completed. Browser tests can be run separately if needed."