#!/bin/bash

set -e

echo "Daily Photo Frame Installation Script"
echo "===================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Installing system dependencies..."
sudo apt update
sudo apt install -y python3-pip python3-venv git

echo "Enabling SPI and I2C interfaces..."
sudo raspi-config nonint do_spi 0
sudo raspi-config nonint do_i2c 0

echo "Adding SPI overlay to disable chip select..."
if ! grep -q "dtoverlay=spi0-0cs" /boot/firmware/config.txt; then
    echo "dtoverlay=spi0-0cs" | sudo tee -a /boot/firmware/config.txt
    echo "Added SPI overlay to config.txt"
else
    echo "SPI overlay already present in config.txt"
fi

echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Creating necessary directories..."
mkdir -p logs cache

echo "Setting up configuration..."
if [ ! -f "config.json" ]; then
    echo "Error: config.json not found. Please create it with your image URL."
    echo "Example config.json:"
    cat << 'EOF'
{
  "image_url": "https://your-server.com/daily-photo",
  "display_type": "auto",
  "log_level": "INFO",
  "retry_attempts": 3,
  "retry_delay": 5,
  "image_cache_dir": "./cache",
  "log_file": "./logs/daily-photo.log"
}
EOF
    exit 1
fi

echo "Testing display connection..."
python3 -c "
try:
    from inky.auto import auto
    display = auto()
    print(f'Display detected: {display.colour} {display.resolution}')
except Exception as e:
    print(f'Display test failed: {e}')
    print('Please check your connections and ensure SPI/I2C are enabled')
    exit(1)
"

echo ""
echo "Installation completed successfully!"
echo ""
echo "Next steps:"
echo "1. Update config.json with your image URL"
echo "2. Test the script: python3 daily_photo.py"
echo "3. Set up the cron job: ./setup_cron.sh"
echo ""
echo "Note: You may need to reboot for SPI/I2C changes to take effect"