#!/usr/bin/env bash

# Wrapper script for Daily Photo Button Monitor
# This script activates the virtual environment and runs the button monitor

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the project directory
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [[ ! -d "venv" ]]; then
    echo "Error: Virtual environment not found at $SCRIPT_DIR/venv"
    exit 1
fi

# Check if button_monitor.py exists
if [[ ! -f "button_monitor.py" ]]; then
    echo "Error: button_monitor.py not found in $SCRIPT_DIR"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Verify Python is available
if ! command -v python &> /dev/null; then
    echo "Error: Python not found in virtual environment"
    exit 1
fi

# Run the button monitor
echo "Starting button monitor..."
exec python button_monitor.py