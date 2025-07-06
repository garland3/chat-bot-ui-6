#!/bin/bash

# Configuration
WAIT_TIME_SECONDS=30
TIMEOUT=20

while true; do
    clear
    echo -e "\033[36mTest run at $(date)\033[0m"
    python -m pytest --timeout=$TIMEOUT -v
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
