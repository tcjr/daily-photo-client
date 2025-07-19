# Button Setup Guide for Daily Photo Frame

This guide explains how to add a physical button to your Raspberry Pi picture frame that allows you to manually refresh the daily photo on demand.

## Hardware Requirements

- Momentary push button (normally open)
- 10kΩ pull-up resistor (optional - software pull-up is used)
- Jumper wires
- Breadboard or direct soldering

## GPIO Pin Configuration

The button monitor is configured to use **GPIO 5** (Button A) by default, which corresponds to:
- **Physical Pin 29** on the Raspberry Pi header
- **BCM GPIO 5**

### Available GPIO Pins (Inky Impression Compatible)

According to the Pimoroni example, these pins are available:
- **GPIO 5** (Pin 29) - Button A ✅ *Default*
- **GPIO 6** (Pin 31) - Button B
- **GPIO 16** (Pin 36) - Button C (GPIO 25 for 13.3" displays)
- **GPIO 24** (Pin 18) - Button D

## Wiring Instructions

### Simple Wiring (Recommended)
```
Button Pin 1 ──── GPIO 5 (Pin 29)
Button Pin 2 ──── Ground (Pin 30 or any GND pin)
```

The software uses internal pull-up resistors, so no external resistor is required.

### With External Pull-up Resistor (Optional)
```
3.3V (Pin 1) ──── 10kΩ Resistor ──── GPIO 5 (Pin 29)
                                  │
                              Button Pin 1
                                  │
                              Button Pin 2 ──── Ground (Pin 30)
```

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

### Adding Multiple Buttons

You can configure multiple buttons for different actions:

```json
{
  "buttons": {
    "refresh_button": {
      "gpio": 5,
      "label": "A",
      "action": "refresh_photo",
      "enabled": true
    },
    "future_button": {
      "gpio": 6,
      "label": "B", 
      "action": "future_action",
      "enabled": false
    }
  }
}
```

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
- Check wiring connections
- Verify GPIO pin number in config.json
- Check if another service is using the GPIO pin
- Run `gpioinfo` to see GPIO status

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

## Physical Installation Tips

1. **Button Placement**: Mount the button in an accessible location on your frame
2. **Wire Management**: Use ribbon cable or thin wires to minimize bulk
3. **Strain Relief**: Secure wires to prevent disconnection from movement
4. **Weatherproofing**: If outdoors, ensure connections are protected from moisture

The button monitor service will automatically start on boot and continuously monitor for button presses, triggering photo refreshes as needed.