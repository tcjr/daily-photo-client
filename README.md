# Daily Photo Frame

A Python application for displaying daily photos on Pimoroni Inky Impression 7.3" eInk displays connected to Raspberry Pi Zero 2 W.

## Features

- Automatic daily photo downloads from HTTP endpoint
- Smart image resizing and centering for eInk display
- Robust error handling with retry logic
- Comprehensive logging
- Automatic cleanup of old cached images
- Easy configuration via JSON file
- Cron job setup for automated daily updates

## Hardware Requirements

- Raspberry Pi Zero 2 W
- Pimoroni Inky Impression 7.3" eInk display (2025/Spectra 6 edition)
- MicroSD card (8GB+ recommended)
- Internet connection (WiFi)

## Installation

### 1. Prepare Raspberry Pi

1. Flash Raspberry Pi OS Lite to SD card
2. Enable SSH and configure WiFi
3. Boot and SSH into the Pi

### 2. Clone and Install

```bash
git clone https://github.com/tcjr/daily-photo-client.git
cd daily-photo-client
chmod +x install.sh
./install.sh
```

### 3. Configure

Edit `config.json` with your image server URL:

```json
{
  "image_url": "https://your-server.com/daily-photo",
  "display_type": "auto",
  "log_level": "INFO",
  "retry_attempts": 3,
  "retry_delay": 5,
  "image_cache_dir": "./cache",
  "log_file": "./logs/daily-photo.log"
}
```

### 4. Test

```bash
source venv/bin/activate
python3 daily_photo.py
```

### 5. Setup Automatic Updates

```bash
./setup_cron.sh
```

## Configuration Options

| Option            | Description                         | Default                    |
| ----------------- | ----------------------------------- | -------------------------- |
| `image_url`       | HTTP endpoint returning daily image | Required                   |
| `display_type`    | Display detection method            | `"auto"`                   |
| `log_level`       | Logging verbosity                   | `"INFO"`                   |
| `retry_attempts`  | Download retry count                | `3`                        |
| `retry_delay`     | Seconds between retries             | `5`                        |
| `image_cache_dir` | Local image storage                 | `"./cache"`                |
| `log_file`        | Log file location                   | `"./logs/daily-photo.log"` |

## Image Requirements

Your HTTP endpoint should return:

- Valid image formats (JPEG, PNG, etc.)
- Any resolution (will be automatically resized)
- Content-Type header indicating image

The system will:

- Resize images to fit 800x480 display
- Maintain aspect ratio
- Center images with white background
- Convert to appropriate format for eInk display

## Logging

Logs are written to both file and console:

- Application logs: `./logs/daily-photo.log`
- Cron logs: `./logs/cron.log`

## Troubleshooting

### Display Not Detected

```bash
# Check SPI/I2C are enabled
sudo raspi-config

# Verify config.txt has SPI overlay
grep "dtoverlay=spi0-0cs" /boot/firmware/config.txt

# Reboot if changes were made
sudo reboot
```

### Network Issues

- Check WiFi connection
- Verify image URL is accessible
- Check firewall settings

### Permission Issues

```bash
# Ensure scripts are executable
chmod +x daily_photo.py setup_cron.sh install.sh
```

## Manual Operation

```bash
# Activate virtual environment
source venv/bin/activate

# Run once
python3 daily_photo.py

# Check logs
tail -f logs/daily-photo.log

# View cron jobs
crontab -l
```

## File Structure

```
daily-photo-client/
├── daily_photo.py      # Main application
├── config.json         # Configuration
├── requirements.txt    # Python dependencies
├── install.sh         # Installation script
├── setup_cron.sh      # Cron job setup
├── README.md          # This file
├── venv/              # Python virtual environment
├── logs/              # Log files
└── cache/             # Downloaded images
```

## License

MIT License - see LICENSE file for details.
