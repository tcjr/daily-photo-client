# Button Setup Guide for Daily Photo Frame

This guide explains how to configure the 4 built-in buttons on your picture frame hardware to control various functions, including manually refreshing the daily photo on demand.

## Hardware Overview

Your picture frame hardware includes **4 pre-wired buttons** that are already connected to the Raspberry Pi GPIO pins:

- **Button A** - GPIO 5 (Pin 29)
- **Button B** - GPIO 6 (Pin 31) 
- **Button C** - GPIO 16 (Pin 36)
- **Button D** - GPIO 24 (Pin 18)

All buttons are wired with proper pull-up resistors and are ready to use with the button monitoring service.

## Software Installation

1. **Install the button monitoring service:**
   ```bash
   ./setup_button_service.sh
   ```

2. **Check service status:**
   ```bash
   sudo systemctl status daily-photo-button.service
   ```

3. **View logs:**
   ```bash
   sudo journalctl -u daily-photo-button.service -f
   ```

4. **Test all buttons:**
   ```bash
   # Stop the service temporarily to test manually
   sudo systemctl stop daily-photo-button.service
   python3 button_monitor.py
   # Press each button to verify detection, then Ctrl+C to exit
   sudo systemctl start daily-photo-button.service
   ```

## Configuration

The button configuration is stored in `config.json`:

```json
{
  "buttons": {
    "refresh_button": {
      "gpio": 5,
      "label": "A",
      "action": "refresh_photo",
      "enabled": true
    }
  },
  "button_debounce_delay": 0.5,
  "daily_photo_script": "./daily_photo.py"
}
```

### Configuration Options

- **gpio**: GPIO pin number (BCM numbering)
- **label**: Human-readable label for the button
- **action**: Action to perform (`refresh_photo` is currently the only supported action)
- **enabled**: Whether this button is active
- **button_debounce_delay**: Minimum time between button presses (seconds)
- **daily_photo_script**: Path to the daily photo script

### Using All 4 Buttons

You can configure all 4 hardware buttons for different actions:

```json
{
  "buttons": {
    "refresh_button": {
      "gpio": 5,
      "label": "A",
      "action": "refresh_photo",
      "enabled": true
    },
    "button_b": {
      "gpio": 6,
      "label": "B", 
      "action": "future_action",
      "enabled": false
    },
    "button_c": {
      "gpio": 16,
      "label": "C",
      "action": "future_action", 
      "enabled": false
    },
    "button_d": {
      "gpio": 24,
      "label": "D",
      "action": "future_action",
      "enabled": false
    }
  }
}
```

Currently only the `refresh_photo` action is implemented. Additional actions can be added to the `button_monitor.py` service as needed.

## Testing

1. **Test button detection:**
   ```bash
   # Stop the service temporarily
   sudo systemctl stop daily-photo-button.service
   
   # Run manually to see button presses
   python3 button_monitor.py
   
   # Press the button - you should see log output
   # Press Ctrl+C to exit
   
   # Restart the service
   sudo systemctl start daily-photo-button.service
   ```

2. **Test photo refresh:**
   - Press the button
   - Check logs: `sudo journalctl -u daily-photo-button.service -f`
   - Verify the display updates with a new photo

## Troubleshooting

### Button Not Detected
- Verify GPIO pin number in config.json matches your hardware
- Check if another service is using the GPIO pin
- Run `gpioinfo` to see GPIO status
- Ensure the button monitoring service has proper GPIO permissions

### Service Won't Start
- Check logs: `sudo journalctl -u daily-photo-button.service`
- Verify file permissions: `ls -la button_monitor.py`
- Check Python dependencies: `pip list | grep -E "(gpiod|gpiodevice)"`

### Photo Refresh Fails
- Check daily_photo.py path in config.json
- Verify daily_photo.py is executable
- Check network connectivity
- Review daily photo logs: `tail -f logs/daily-photo.log`

### Permission Issues
- Ensure the service runs as the correct user (pi)
- Check file ownership: `ls -la /etc/systemd/system/daily-photo-button.service`
- Verify GPIO access permissions

## Service Management

```bash
# Start service
sudo systemctl start daily-photo-button.service

# Stop service  
sudo systemctl stop daily-photo-button.service

# Restart service
sudo systemctl restart daily-photo-button.service

# Enable auto-start on boot
sudo systemctl enable daily-photo-button.service

# Disable auto-start
sudo systemctl disable daily-photo-button.service

# View status
sudo systemctl status daily-photo-button.service

# View logs
sudo journalctl -u daily-photo-button.service -f
```

## Button Functions

With your 4 pre-wired buttons, you can implement various frame control functions:

- **Button A (GPIO 5)**: Photo refresh (currently implemented)
- **Button B (GPIO 6)**: Available for future features
- **Button C (GPIO 16)**: Available for future features  
- **Button D (GPIO 24)**: Available for future features

Potential future button functions could include:
- Display brightness control
- Sleep/wake display
- Cycle through recent photos
- Network status display
- Configuration mode

The button monitor service will automatically start on boot and continuously monitor all configured buttons for presses.