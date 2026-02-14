# Hardlink Checker for Cross-Seed

A Python utility for identifying non-hardlinked files in a directory. This tool recursively scans a specified folder and generates detailed reports of files that lack hardlinks.

## Features

- **Recursive Directory Scanning**: Scans all files in subdirectories
- **Comprehensive Reporting**: Generates detailed text reports with file paths, sizes, link counts, inodes, and modification dates
- **Statistical Summary**: Provides overview statistics including total files scanned, hardlinked vs non-hardlinked counts, and storage metrics
- **JSON Configuration**: Easy configuration via JSON file for folder paths and output settings
- **Robust Error Handling**: Gracefully handles permission errors and missing files
- **Progress Logging**: Real-time progress updates during scanning
- **Professional Output**: Clean, formatted reports suitable for documentation and monitoring

## Requirements

- Python 3.6 or higher
- Linux operating system (uses POSIX stat functionality)

### Configuration Options

- **folder_path**: The directory to scan recursively for non-hardlinked files
- **output_path**: Where to save the generated report (text file)
- **log_level**: Logging verbosity level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

## Usage

### Basic Usage

```bash
python3 check_hardlinks.py
```

The script will:
1. Read configuration from `config.json`
2. Scan the specified directory recursively
3. Identify all files with link count = 1 (not hardlinked)
4. Generate a detailed report at the specified output path
5. Display summary statistics in the console