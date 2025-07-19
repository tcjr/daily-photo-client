#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/daily_photo.py"

echo "Setting up daily photo cron job..."

if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "Error: daily_photo.py not found at $PYTHON_SCRIPT"
    exit 1
fi

chmod +x "$PYTHON_SCRIPT"

CRON_JOB="0 6 * * * cd $SCRIPT_DIR && /usr/bin/python3 $PYTHON_SCRIPT >> $SCRIPT_DIR/logs/cron.log 2>&1"

(crontab -l 2>/dev/null | grep -v "$PYTHON_SCRIPT"; echo "$CRON_JOB") | crontab -

echo "Cron job added successfully!"
echo "The photo will update daily at 6:00 AM"
echo "Logs will be written to:"
echo "  - Application logs: $SCRIPT_DIR/logs/daily-photo.log"
echo "  - Cron logs: $SCRIPT_DIR/logs/cron.log"
echo ""
echo "To view current cron jobs: crontab -l"
echo "To remove this cron job: crontab -e (then delete the line)"
echo ""
echo "You can test the script manually by running:"
echo "  cd $SCRIPT_DIR && python3 daily_photo.py"