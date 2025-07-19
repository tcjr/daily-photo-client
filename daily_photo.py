#!/usr/bin/env python3

import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import requests
from PIL import Image
from inky.auto import auto


class DailyPhotoDisplay:
    def __init__(self, config_path="config.json"):
        self.config = self.load_config(config_path)
        self.setup_logging()
        self.setup_directories()
        
        try:
            self.display = auto()
            self.logger.info(f"Detected display: {self.display.colour} {self.display.resolution}")
        except Exception as e:
            self.logger.error(f"Failed to initialize display: {e}")
            if self.config.get("display_type") != "auto":
                self.logger.info("Falling back to manual display configuration")
                raise
            sys.exit(1)

    def load_config(self, config_path):
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Config file {config_path} not found. Please create it with your settings.")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Invalid JSON in config file: {e}")
            sys.exit(1)

    def setup_logging(self):
        log_level = getattr(logging, self.config.get("log_level", "INFO"))
        log_file = self.config.get("log_file", "./logs/daily-photo.log")
        
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

    def setup_directories(self):
        cache_dir = self.config.get("image_cache_dir", "./cache")
        os.makedirs(cache_dir, exist_ok=True)

    def download_image(self, url, max_retries=None):
        if max_retries is None:
            max_retries = self.config.get("retry_attempts", 3)
        
        retry_delay = self.config.get("retry_delay", 5)
        
        for attempt in range(max_retries):
            try:
                self.logger.info(f"Downloading image from {url} (attempt {attempt + 1}/{max_retries})")
                
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                
                if not response.headers.get('content-type', '').startswith('image/'):
                    raise ValueError(f"URL did not return an image (content-type: {response.headers.get('content-type')})")
                
                cache_dir = self.config.get("image_cache_dir", "./cache")
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                image_path = os.path.join(cache_dir, f"daily_photo_{timestamp}.jpg")
                
                with open(image_path, 'wb') as f:
                    f.write(response.content)
                
                self.logger.info(f"Image downloaded successfully: {image_path}")
                return image_path
                
            except requests.RequestException as e:
                self.logger.warning(f"Download attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    self.logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    self.logger.error(f"Failed to download image after {max_retries} attempts")
                    raise
            except Exception as e:
                self.logger.error(f"Unexpected error during download: {e}")
                raise

    def process_image(self, image_path):
        try:
            self.logger.info(f"Processing image: {image_path}")
            
            with Image.open(image_path) as img:
                img = img.convert('RGB')
                
                display_width, display_height = self.display.resolution
                self.logger.info(f"Display resolution: {display_width}x{display_height}")
                
                img_ratio = img.width / img.height
                display_ratio = display_width / display_height
                
                if img_ratio > display_ratio:
                    new_width = display_width
                    new_height = int(display_width / img_ratio)
                else:
                    new_height = display_height
                    new_width = int(display_height * img_ratio)
                
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                final_img = Image.new('RGB', (display_width, display_height), (255, 255, 255))
                
                x_offset = (display_width - new_width) // 2
                y_offset = (display_height - new_height) // 2
                final_img.paste(img, (x_offset, y_offset))
                
                self.logger.info(f"Image processed: resized to {new_width}x{new_height}, centered on {display_width}x{display_height}")
                return final_img
                
        except Exception as e:
            self.logger.error(f"Failed to process image: {e}")
            raise

    def display_image(self, image):
        try:
            self.logger.info("Updating display...")
            self.display.set_image(image)
            self.display.show()
            self.logger.info("Display updated successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to update display: {e}")
            raise

    def cleanup_old_images(self, keep_count=5):
        try:
            cache_dir = self.config.get("image_cache_dir", "./cache")
            cache_path = Path(cache_dir)
            
            if not cache_path.exists():
                return
            
            image_files = sorted(
                [f for f in cache_path.glob("daily_photo_*.jpg")],
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            
            files_to_delete = image_files[keep_count:]
            
            for file_path in files_to_delete:
                file_path.unlink()
                self.logger.info(f"Deleted old image: {file_path}")
                
        except Exception as e:
            self.logger.warning(f"Failed to cleanup old images: {e}")

    def run(self):
        try:
            self.logger.info("Starting daily photo update")
            
            image_url = self.config.get("image_url")
            if not image_url:
                self.logger.error("No image_url configured")
                return False
            
            image_path = self.download_image(image_url)
            processed_image = self.process_image(image_path)
            self.display_image(processed_image)
            self.cleanup_old_images()
            
            self.logger.info("Daily photo update completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Daily photo update failed: {e}")
            return False


def main():
    display = DailyPhotoDisplay()
    success = display.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()