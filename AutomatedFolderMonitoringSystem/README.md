# Automated Folder Monitoring System

A Python application that continuously monitors a folder and automatically organizes incoming files into categorized folders based on their file extensions.

## Features

- Continuously monitors a folder using Watchdog.
- Automatically categorizes files based on their extensions.
- Moves files into category-specific folders.
- Supports JSON-based category configuration.
- Handles unsupported files and duplicate filenames.
- Waits for files to stabilize before processing.
- Retries file movement when files are temporarily locked.
- Logs processing activities and errors.
- Handles graceful shutdown.

## Technologies Used

- Python
- Watchdog
- pathlib
- shutil
- logging
- JSON

## Project Structure

```text
AutomatedFolderMonitoringSystem/
├── main.py
├── file_monitor.py
├── file_processor.py
├── config.json
├── requirements.txt
├── incoming/
├── processed/
└── monitoring.log
```

## Installation

```bash
python -m venv venv
```

Activate the virtual environment:

**Windows:**

```powershell
venv\Scripts\Activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the application:

```bash
python main.py
```

Add files to the `incoming` folder. The application automatically organizes them into the appropriate folders inside `processed`.

Press `Ctrl + C` to stop monitoring.

## Output Categories

Files are organized into folders such as:

- Documents
- Spreadsheets
- Images
- Videos
- Audio
