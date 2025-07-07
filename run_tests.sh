#!/bin/bash

# Configuration
WAIT_TIME_SECONDS=30
TIMEOUT=20
PARALLEL_WORKERS=4
LOG_FILE="test_results/test_run_$(date +%Y%m%d_%H%M%S).log"
# LOG_FILE="test_results/recent.log"
# make an alias from # LOG_FILE="test_results/recent.log" to the actual log file. 
# This will allow you to always have the latest log file available as 'recent.log'
ln -sf "$LOG_FILE" test_results/recent.log


# Create test_results directory if it doesn't exist
mkdir -p test_results

while true; do
    clear
    echo -e "\033[36mTest run at $(date)\033[0m"
    echo -e "\033[32mSaving results to: $LOG_FILE\033[0m"
    
    # Run tests in parallel and save to file while showing on stdout
    # -n $PARALLEL_WORKERS: use configured number of parallel workers
    # -vv: extra verbose output, --tb=short: shorter traceback format
    python -m pytest tests/ -n $PARALLEL_WORKERS --timeout=$TIMEOUT -x -vv --tb=short 2>&1 | tee -a "$LOG_FILE"
    
    echo -e "\033[33m\nNext run in $WAIT_TIME_SECONDS seconds... (Press Ctrl+C to stop)\033[0m"
    
    # Bash progress bar
    for ((i=1; i<=WAIT_TIME_SECONDS; i++)); do
        percent=$((i * 100 / WAIT_TIME_SECONDS))
        remaining=$((WAIT_TIME_SECONDS - i))
        
        # Create progress bar
        bar_length=50
        filled_length=$((percent * bar_length / 100))
        bar=$(printf "%*s" $filled_length | tr ' ' '=')
        spaces=$(printf "%*s" $((bar_length - filled_length)) | tr ' ' ' ')
        
        printf "\rWaiting for next test run [%s%s] %d%% (%d seconds remaining)" "$bar" "$spaces" "$percent" "$remaining"
        sleep 1
    done
    printf "\n"
done
