# Folder Backup Utility

A Python application that creates timestamped, compressed ZIP backups of a specified directory. It supports multiple backup versions, configurable retention limits, ZIP verification, and logging.

## Features

- Create compressed ZIP backups.
- Generate timestamp-based backup filenames.
- Maintain multiple backup versions.
- Automatically remove older backups based on a retention limit.
- Verify ZIP archive integrity.
- Exclude the backup destination from the source backup.
- Handle errors and log backup operations.
- Configure backup settings using JSON.

## Technologies Used

- Python
- pathlib
- shutil
- zipfile
- datetime
- JSON
- Logging
- Exception Handling

## Project Structure

```text
FolderBackupUtility/
│
├── main.py
├── config.json
├── requirements.txt
├── .gitignore
│
├── backups/
├── logs/
│
└── test_data/
```

## Configuration

Configure the default settings in `config.json`:

```json
{
    "source_folder": "",
    "backup_folder": "backups",
    "max_backups": 5
}
```

## How to Run

No external packages are required.

```bash
python main.py
```

Enter the source directory, backup destination, and maximum number of backups to retain when prompted.

## Backup Output

Generated ZIP archives are stored in the configured backup directory.

```text
backups/
├── backup_2026-11-26_10-55-33-709260.zip
└── backup_2026-11-26_10-52-43-090848.zip
```

Log records are stored in `logs/backup.log`.

## Testing

The application was tested for:

- Backup creation and ZIP verification.
- Multiple backup versions.
- Backup retention and removal of older archives.
- Empty source directories.
- Missing source directories.
- Simulated backup failure.
- Timestamp-based backup filenames.
