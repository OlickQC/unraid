# Minecraft Region Backup

## Overview

A lightweight Bash script designed to back up specific Minecraft region files (`.mca`) on a scheduled basis. It provides a practical solution for servers where full map backups are impractical due to storage or time constraints, enabling frequent and targeted backups of critical areas with extended retention and minimal disk usage.

## Problem

Minecraft world saves can grow to tens of gigabytes, making full hourly backups costly in both storage and I/O. However, not every chunk on the map holds the same value. Spawn areas, player bases, and key builds often warrant more aggressive backup schedules and longer retention than the surrounding terrain.

## Solution

This script selectively copies only the region files you specify, timestamps each backup, and automatically purges copies older than a configurable retention period. Because individual region files are small (typically a few megabytes each), the resulting backups are compact enough to run hourly with long-term retention.

## Features

- **Selective backup**: Only the region files listed in the configuration array are copied.
- **Timestamped snapshots**: Each run creates a dated directory (`YYYY-MM-DD_HH-MM-SS`) containing the backed-up files.
- **Automatic retention cleanup**: Old backups are removed after a configurable number of days.
- **Validation**: Source and destination directories are verified before processing. Missing files are skipped with a warning.

## Configuration

All configuration is done by editing variables at the top of the script.

| Variable           | Description                                                                 |
|--------------------|-----------------------------------------------------------------------------|
| `SOURCE_DIR`       | Absolute path to the Minecraft world's `region` directory.                  |
| `WATCH_DIR`        | Absolute path to the destination directory where backups will be stored.    |
| `FILES_TO_PROCESS` | Array of `.mca` region filenames to include in each backup.                 |
| `-mtime +N`        | Retention threshold in the `find` cleanup command (default: `+10` days).    |

### Identifying Region Files

Minecraft region files follow the naming convention `r.<X>.<Z>.mca`, where `<X>` and `<Z>` are region coordinates. Each region file contains a 32x32 area of chunks (512x512 blocks). To determine which region files cover a specific in-game area, divide the block coordinates by 512 and round down.

## Usage

### Manual execution

```bash
chmod +x region_backup.sh
./region_backup.sh
```

### Scheduled execution (recommended)

Add a cron entry to run the script hourly:

```
0 * * * * /path/to/region_backup.sh
```

On Unraid, this script can be scheduled through the **User Scripts** plugin.

## Directory Structure

After several runs, the backup directory will look like this:

```
region_backup/
    2026-02-13_08-00-00/
        r.2.-6_2026-02-13_08-00-00.mca
        r.3.-6_2026-02-13_08-00-00.mca
        ...
    2026-02-13_09-00-00/
        r.2.-6_2026-02-13_09-00-00.mca
        r.3.-6_2026-02-13_09-00-00.mca
        ...
```

## Requirements

- Bash 4.0 or later
- Standard POSIX utilities: `cp`, `find`, `mkdir`, `date`