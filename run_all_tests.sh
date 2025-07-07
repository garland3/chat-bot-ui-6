#!/bin/bash

echo "🧪 Comprehensive Test Suite"
echo "=========================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

TOTAL_TESTS=0
PASSED_TESTS=0

run_test() {
    local test_name="$1"
    local test_command="$2"
    local timeout_duration="$3"
    
    echo -e "\n${YELLOW}Running: $test_name${NC}"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if timeout "$timeout_duration" bash -c "$test_command"; then
        echo -e "${GREEN}✓ $test_name PASSED${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        exit_code=$?
        if [ $exit_code -eq 124 ]; then
            echo -e "${RED}✗ $test_name TIMED OUT${NC}"
        else
            echo -e "${RED}✗ $test_name FAILED${NC}"
        fi
    fi
}

# 1. Backend Core tests
run_test "Backend Core Tests" \
    "cd /app && uv run pytest tests/backend/ -v" \
    "45s"

# 2. API tests
run_test "API Tests" \
    "cd /app && uv run pytest tests/api/ -v" \
    "60s"

# 3. Integration tests
run_test "Integration Tests" \
    "cd /app && uv run pytest tests/integration/ -v" \
    "120s"

# 4. Simple browser integration test
run_test "Browser Integration Test" \
    "python3 /app/test_browser_simple.py" \
    "60s"

# 5. Frontend build test
run_test "Frontend Build" \
    "cd /app/frontend && npm run build" \
    "60s"

# Summary
echo -e "\n🏁 Test Summary"
echo "==============="
echo -e "Passed: ${GREEN}$PASSED_TESTS${NC}"
echo -e "Total:  $TOTAL_TESTS"

if [ $PASSED_TESTS -eq $TOTAL_TESTS ]; then
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    exit 0
else
    failed=$((TOTAL_TESTS - PASSED_TESTS))
    echo -e "${RED}❌ $failed test(s) failed${NC}"
    exit 1
fi