# Agent Guidelines for Daily Photo Client

## Build/Test Commands

- **Run application**: `python3 daily_photo.py`
- **Install dependencies**: `pip install -r requirements.txt`
- **Setup environment**: `./install.sh` (creates venv and installs deps)
- **Test manually**: `source venv/bin/activate && python3 daily_photo.py`
- **Check logs**: `tail -f logs/daily-photo.log`

## Code Style Guidelines

- **Language**: Python 3 with type hints where beneficial
- **Imports**: Standard library first, then third-party (requests, PIL, inky), then local
- **Classes**: PascalCase (e.g., `DailyPhotoDisplay`)
- **Methods/Variables**: snake_case (e.g., `setup_logging`, `image_path`)
- **Constants**: UPPER_SNAKE_CASE for module-level constants
- **Error Handling**: Use try/except with specific exceptions, log errors with context
- **Logging**: Use self.logger with appropriate levels (INFO, WARNING, ERROR)
- **Configuration**: Load from config.json, provide sensible defaults
- **File Paths**: Use os.path.join() or pathlib.Path for cross-platform compatibility
- **Docstrings**: Not required for simple methods, use for complex logic
- **Line Length**: Keep reasonable (~100 chars), prioritize readability
- **Dependencies**: Minimal external deps (inky, Pillow, requests only)

## Project Structure

- Single-file application (`daily_photo.py`) with class-based architecture
- JSON configuration (`config.json`) for all settings
- Virtual environment for dependency isolation
