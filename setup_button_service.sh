#!/bin/bash

# Setup script for Daily Photo Button Monitor Service
# This script installs and configures the button monitoring service

set -e

echo "Setting up Daily Photo Button Monitor Service..."

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "This script should not be run as root. Please run as a regular user."
   exit 1
fi

# Get the current directory (where the script is located)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_NAME="daily-photo-button"
CURRENT_USER="$(whoami)"

echo "Working directory: $SCRIPT_DIR"

# Check if required files exist
if [[ ! -f "$SCRIPT_DIR/button_monitor.py" ]]; then
    echo "Error: button_monitor.py not found in $SCRIPT_DIR"
    exit 1
fi

if [[ ! -f "$SCRIPT_DIR/daily-photo-button.service" ]]; then
    echo "Error: daily-photo-button.service not found in $SCRIPT_DIR"
    exit 1
fi

if [[ ! -f "$SCRIPT_DIR/run_button_monitor.sh" ]]; then
    echo "Error: run_button_monitor.sh not found in $SCRIPT_DIR"
    exit 1
fi

# Make scripts executable
chmod +x "$SCRIPT_DIR/button_monitor.py"
chmod +x "$SCRIPT_DIR/run_button_monitor.sh"
echo "Made scripts executable"

# Update the service file with the correct paths
SERVICE_FILE="$SCRIPT_DIR/daily-photo-button.service"
TEMP_SERVICE="/tmp/daily-photo-button.service"

# Use the wrapper script instead of direct Python execution
WRAPPER_SCRIPT="$SCRIPT_DIR/run_button_monitor.sh"

echo "Using wrapper script: $WRAPPER_SCRIPT"

# Replace placeholder paths and user with actual values
sed -e "s|/home/pi/daily-photo-client|$SCRIPT_DIR|g" \
    -e "s|User=pi|User=$CURRENT_USER|g" \
    -e "s|Group=pi|Group=$CURRENT_USER|g" \
    -e "s|/home/pi/daily-photo-client/venv/bin/python /home/pi/daily-photo-client/button_monitor.py|$WRAPPER_SCRIPT|g" \
    "$SERVICE_FILE" > "$TEMP_SERVICE"

# Install the service file
echo "Installing systemd service..."
sudo cp "$TEMP_SERVICE" /etc/systemd/system/daily-photo-button.service
sudo chown root:root /etc/systemd/system/daily-photo-button.service
sudo chmod 644 /etc/systemd/system/daily-photo-button.service

# Clean up temp file
rm "$TEMP_SERVICE"

# Reload systemd and enable the service
echo "Enabling and starting the service..."
sudo systemctl daemon-reload
sudo systemctl enable daily-photo-button.service

# Check if virtual environment exists and install dependencies
if [[ -d "$SCRIPT_DIR/venv" ]]; then
    echo "Virtual environment found, installing additional dependencies..."
    source "$SCRIPT_DIR/venv/bin/activate"
    pip install gpiod gpiodevice
    deactivate
else
    echo "Warning: Virtual environment not found at $SCRIPT_DIR/venv"
    echo "Please ensure gpiod and gpiodevice are installed in your Python environment"
fi

# Start the service
sudo systemctl start daily-photo-button.service

# Check service status
echo ""
echo "Service installation complete!"
echo ""
echo "Service status:"
sudo systemctl status daily-photo-button.service --no-pager -l

echo ""
echo "To check logs, run:"
echo "  sudo journalctl -u daily-photo-button.service -f"
echo ""
echo "To stop the service:"
echo "  sudo systemctl stop daily-photo-button.service"
echo ""
echo "To disable the service:"
echo "  sudo systemctl disable daily-photo-button.service"
echo ""
echo "Button monitor is now running and will start automatically on boot."