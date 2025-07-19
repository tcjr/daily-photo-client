#!/usr/bin/env python3

import json
import logging
import os
import subprocess
import sys
import time
from pathlib import Path

import gpiod
import gpiodevice
from gpiod.line import Bias, Direction, Edge


class ButtonMonitor:
    def __init__(self, config_path="config.json"):
        self.config = self.load_config(config_path)
        self.setup_logging()
        self.setup_gpio()
        
    def load_config(self, config_path):
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Config file {config_path} not found. Using defaults.")
            return self.get_default_config()
        except json.JSONDecodeError as e:
            print(f"Invalid JSON in config file: {e}")
            return self.get_default_config()
    
    def get_default_config(self):
        return {
            "buttons": {
                "refresh_button": {
                    "gpio": 5,
                    "label": "A",
                    "action": "refresh_photo",
                    "enabled": True
                },
                "button_b": {
                    "gpio": 6,
                    "label": "B",
                    "action": "future_action",
                    "enabled": False
                },
                "button_c": {
                    "gpio": 16,
                    "label": "C",
                    "action": "future_action",
                    "enabled": False
                },
                "button_d": {
                    "gpio": 24,
                    "label": "D",
                    "action": "future_action",
                    "enabled": False
                }
            },
            "button_debounce_delay": 0.5,
            "daily_photo_script": "./daily_photo.py",
            "log_level": "INFO",
            "log_file": "./logs/button-monitor.log"
        }
    
    def setup_logging(self):
        log_level = getattr(logging, self.config.get("log_level", "INFO"))
        log_file = self.config.get("log_file", "./logs/button-monitor.log")
        
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_gpio(self):
        try:
            self.logger.info("Setting up GPIO for pre-wired frame buttons")
            
            # Get enabled buttons from config
            buttons_config = self.config.get("buttons", {})
            self.enabled_buttons = {
                name: config for name, config in buttons_config.items() 
                if config.get("enabled", True)
            }
            
            if not self.enabled_buttons:
                self.logger.warning("No enabled buttons found in configuration")
                return
            
            # Extract GPIO numbers and create mappings
            self.gpio_numbers = [config["gpio"] for config in self.enabled_buttons.values()]
            self.gpio_to_button = {
                config["gpio"]: name for name, config in self.enabled_buttons.items()
            }
            
            # Find the gpiochip device
            self.chip = gpiodevice.find_chip_by_platform()
            
            # Create settings for input pins with pull-up and falling edge detection
            input_settings = gpiod.LineSettings(
                direction=Direction.INPUT, 
                bias=Bias.PULL_UP, 
                edge_detection=Edge.FALLING
            )
            
            # Build config for each pin
            self.offsets = [self.chip.line_offset_from_id(gpio) for gpio in self.gpio_numbers]
            line_config = dict.fromkeys(self.offsets, input_settings)
            
            # Request the lines
            self.request = self.chip.request_lines(
                consumer="daily-photo-button-monitor", 
                config=line_config
            )
            
            self.logger.info(f"GPIO setup complete. Monitoring buttons: {list(self.enabled_buttons.keys())}")
            
        except Exception as e:
            self.logger.error(f"Failed to setup GPIO: {e}")
            raise
    
    def handle_button_press(self, event):
        try:
            # Find which button was pressed
            gpio_number = self.gpio_numbers[self.offsets.index(event.line_offset)]
            button_name = self.gpio_to_button[gpio_number]
            button_config = self.enabled_buttons[button_name]
            
            self.logger.info(f"Button '{button_name}' pressed (GPIO {gpio_number})")
            
            # Execute the configured action
            action = button_config.get("action")
            if action == "refresh_photo":
                self.refresh_photo()
            else:
                self.logger.warning(f"Unknown action '{action}' for button '{button_name}'")
                
        except Exception as e:
            self.logger.error(f"Error handling button press: {e}")
    
    def refresh_photo(self):
        try:
            script_path = self.config.get("daily_photo_script", "./daily_photo.py")
            
            # Convert to absolute path if relative
            if not os.path.isabs(script_path):
                script_path = os.path.join(os.path.dirname(__file__), script_path)
            
            if not os.path.exists(script_path):
                self.logger.error(f"Daily photo script not found: {script_path}")
                return
            
            self.logger.info("Triggering photo refresh...")
            
            # Run the daily photo script
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                self.logger.info("Photo refresh completed successfully")
            else:
                self.logger.error(f"Photo refresh failed with return code {result.returncode}")
                if result.stderr:
                    self.logger.error(f"Error output: {result.stderr}")
                    
        except subprocess.TimeoutExpired:
            self.logger.error("Photo refresh timed out after 5 minutes")
        except Exception as e:
            self.logger.error(f"Failed to refresh photo: {e}")
    
    def run(self):
        try:
            if not hasattr(self, 'request'):
                self.logger.error("GPIO not properly initialized")
                return
                
            self.logger.info("Button monitor started. Press Ctrl+C to exit.")
            
            debounce_delay = self.config.get("button_debounce_delay", 0.5)
            last_press_time = {}
            
            while True:
                for event in self.request.read_edge_events():
                    current_time = time.time()
                    gpio_number = self.gpio_numbers[self.offsets.index(event.line_offset)]
                    
                    # Simple debouncing
                    if gpio_number in last_press_time:
                        if current_time - last_press_time[gpio_number] < debounce_delay:
                            continue
                    
                    last_press_time[gpio_number] = current_time
                    self.handle_button_press(event)
                    
        except KeyboardInterrupt:
            self.logger.info("Button monitor stopped by user")
        except Exception as e:
            self.logger.error(f"Button monitor error: {e}")
            raise
        finally:
            if hasattr(self, 'request'):
                self.request.close()


def main():
    try:
        monitor = ButtonMonitor()
        monitor.run()
    except Exception as e:
        print(f"Failed to start button monitor: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()