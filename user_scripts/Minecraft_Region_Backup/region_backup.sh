#!/bin/bash

# Source directory containing the files to copy
SOURCE_DIR="/mnt/user/appdata/crafty-4/servers/b4a7c88a-a199-e5a687451495/Elundis/region"  # Replace with your source directory path

# Destination directory where files will be organized
WATCH_DIR="/mnt/user/data/backup/crafty/backups/b4a7c88a-a199-e5a687451495/region_backup"  # Replace with your destination directory path

# List of files to process (up to 10 files)
FILES_TO_PROCESS=(
    "r.2.-6.mca"
    "r.3.-6.mca"
    "r.4.-6.mca"
    "r.5.-6.mca"
    "r.2.-7.mca"
    "r.3.-7.mca"
    "r.4.-7.mca"
    "r.5.-7.mca"
    "r.2.-8.mca"
    "r.3.-8.mca"
    "r.4.-8.mca"
    "r.5.-8.mca"
)

# Check if the source directory exists
if [ ! -d "$SOURCE_DIR" ]; then
    echo "Error: Source directory '$SOURCE_DIR' does not exist."
    exit 1
fi

# Check if the destination directory exists
if [ ! -d "$WATCH_DIR" ]; then
    echo "Error: Destination directory '$WATCH_DIR' does not exist. Creating it now..."
    mkdir -p "$WATCH_DIR"
fi

# Get the current date and hour for folder naming
DATE_HOUR=$(date +"%Y-%m-%d_%H-%M-%S")
DEST_DIR="$WATCH_DIR/$DATE_HOUR"

# Create the destination folder
mkdir -p "$DEST_DIR"

# Process each file
for FILENAME in "${FILES_TO_PROCESS[@]}"; do
    SOURCE_FILE="$SOURCE_DIR/$FILENAME"

    # Skip if the file does not exist
    if [ ! -f "$SOURCE_FILE" ]; then
        echo "Warning: File '$SOURCE_FILE' does not exist. Skipping..."
        continue
    fi

    # Extract filename and extension
    EXTENSION="${FILENAME##*.}"
    BASENAME="${FILENAME%.*}"

    # Destination file with the date in the name
    if [ "$EXTENSION" == "$FILENAME" ]; then
        DEST_FILE="${BASENAME}_${DATE_HOUR}"
    else
        DEST_FILE="${BASENAME}_${DATE_HOUR}.${EXTENSION}"
    fi

    # Copy the file to the destination folder
    cp "$SOURCE_FILE" "$DEST_DIR/$DEST_FILE"
    echo "File '$SOURCE_FILE' copied to '$DEST_DIR/$DEST_FILE'"

    # Clean up files older than 180 days for this file's base name in the destination directory
    echo "Cleaning up files older than 180 days for '${BASENAME}_*' in '$WATCH_DIR'..."
    find "$WATCH_DIR" -type f -name "${BASENAME}_*.*" -mtime +10 -exec rm -v {} \;
done

echo "Processing complete. Files are saved in folder: $DEST_DIR"
