#!/usr/bin/env python3
"""
Hardlink Checker

This script scans a directory recursively to identify files that are not hardlinked.
It generates a detailed report of non-hardlinked files with statistics.

Author: OlickQC
License: MIT
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Any


class HardlinkChecker:
    """Scanner for identifying non-hardlinked files in a directory tree."""

    def __init__(self, config_path: str = "/boot/config/plugins/user.scripts/scripts/hardlink_checker/config.json"):
        """
        Initialize the HardlinkChecker.

        Args:
            config_path: Path to the JSON configuration file
        """
        self.config = self._load_config(config_path)
        self.scan_path = Path(self.config["folder_path"]).resolve()
        
        # Add timestamp to output filename
        output_base = Path(self.config["output_path"]).resolve()
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_stem = output_base.stem
        output_suffix = output_base.suffix
        output_dir = output_base.parent
        self.output_path = output_dir / f"{output_stem}_{timestamp}{output_suffix}"
        
        self._setup_logging()

    def _load_config(self, config_path: str) -> dict:
        """
        Load configuration from JSON file.

        Args:
            config_path: Path to the configuration file

        Returns:
            Dictionary containing configuration settings

        Raises:
            FileNotFoundError: If config file doesn't exist
            json.JSONDecodeError: If config file is invalid JSON
            KeyError: If required configuration keys are missing
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # Validate required keys
            required_keys = ["folder_path", "output_path"]
            missing_keys = [key for key in required_keys if key not in config]
            if missing_keys:
                raise KeyError(f"Missing required configuration keys: {missing_keys}")

            return config

        except FileNotFoundError:
            logging.error(f"Configuration file not found: {config_path}")
            raise
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON in configuration file: {e}")
            raise
        except KeyError as e:
            logging.error(str(e))
            raise

    def _setup_logging(self):
        """Configure logging based on configuration settings."""
        log_level = self.config.get("log_level", "INFO").upper()
        log_format = "%(asctime)s - %(levelname)s - %(message)s"

        logging.basicConfig(
            level=getattr(logging, log_level, logging.INFO),
            format=log_format,
            handlers=[
                logging.StreamHandler(sys.stdout)
            ]
        )

    def is_hardlinked(self, file_path: Path) -> bool:
        """
        Check if a file is hardlinked.

        Args:
            file_path: Path to the file to check

        Returns:
            True if the file has more than one hard link, False otherwise
        """
        try:
            stat_info = file_path.stat()
            # A file is considered hardlinked if its link count > 1
            return stat_info.st_nlink > 1
        except (OSError, PermissionError) as e:
            logging.warning(f"Unable to check hardlink status for {file_path}: {e}")
            return True  # Assume hardlinked to exclude from report

    def get_file_details(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a file.

        Args:
            file_path: Path to the file

        Returns:
            Dictionary containing file details or None if unable to retrieve
        """
        try:
            stat_info = file_path.stat()
            return {
                "path": str(file_path),
                "size_bytes": stat_info.st_size,
                "size_human": self._human_readable_size(stat_info.st_size),
                "link_count": stat_info.st_nlink,
                "inode": stat_info.st_ino,
                "modified": datetime.fromtimestamp(stat_info.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            }
        except (OSError, PermissionError) as e:
            logging.warning(f"Unable to get details for {file_path}: {e}")
            return None

    def _human_readable_size(self, size_bytes: int) -> str:
        """
        Convert bytes to human-readable format.

        Args:
            size_bytes: Size in bytes

        Returns:
            Human-readable size string
        """
        size: float = float(size_bytes)
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"

    def scan_directory(self) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Scan directory recursively for non-hardlinked files.

        Returns:
            Tuple containing:
                - List of non-hardlinked file details
                - Dictionary of summary statistics
        """
        if not self.scan_path.exists():
            raise FileNotFoundError(f"Scan path does not exist: {self.scan_path}")

        if not self.scan_path.is_dir():
            raise NotADirectoryError(f"Scan path is not a directory: {self.scan_path}")

        logging.info(f"Starting scan of: {self.scan_path}")

        non_hardlinked_files: List[Dict[str, Any]] = []
        total_files = 0
        total_size = 0
        non_hardlinked_size = 0
        errors = 0

        try:
            for root, dirs, files in os.walk(self.scan_path):
                for filename in files:
                    file_path = Path(root) / filename

                    # Skip symbolic links
                    if file_path.is_symlink():
                        continue

                    total_files += 1

                    try:
                        if not self.is_hardlinked(file_path):
                            details = self.get_file_details(file_path)
                            if details:
                                non_hardlinked_files.append(details)
                                non_hardlinked_size += details["size_bytes"]

                        # Track total size
                        stat_info = file_path.stat()
                        total_size += stat_info.st_size

                    except (OSError, PermissionError) as e:
                        logging.warning(f"Error processing {file_path}: {e}")
                        errors += 1
                        continue

                    # Log progress every 1000 files
                    if total_files % 1000 == 0:
                        logging.info(f"Processed {total_files} files...")

        except KeyboardInterrupt:
            logging.warning("Scan interrupted by user")
            raise

        logging.info(f"Scan complete. Processed {total_files} files.")

        summary: Dict[str, Any] = {
            "scan_path": str(self.scan_path),
            "scan_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_files_scanned": total_files,
            "non_hardlinked_count": len(non_hardlinked_files),
            "hardlinked_count": total_files - len(non_hardlinked_files) - errors,
            "errors": errors,
            "total_size": self._human_readable_size(total_size),
            "non_hardlinked_size": self._human_readable_size(non_hardlinked_size),
            "percentage_not_hardlinked": round((len(non_hardlinked_files) / total_files * 100), 2) if total_files > 0 else 0
        }

        return non_hardlinked_files, summary

    def generate_report(self, non_hardlinked_files: List[Dict[str, Any]], summary: Dict[str, Any]):
        """
        Generate a text report of non-hardlinked files.

        Args:
            non_hardlinked_files: List of non-hardlinked file details
            summary: Summary statistics dictionary
        """
        try:
            # Ensure output directory exists
            self.output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.output_path, 'w', encoding='utf-8') as f:
                # Write header
                f.write("=" * 80 + "\n")
                f.write("HARDLINK CHECK REPORT\n")
                f.write("=" * 80 + "\n\n")

                # Write summary
                f.write("SUMMARY STATISTICS\n")
                f.write("-" * 80 + "\n")
                f.write(f"Scan Path:                {summary['scan_path']}\n")
                f.write(f"Scan Timestamp:           {summary['scan_timestamp']}\n")
                f.write(f"Total Files Scanned:      {summary['total_files_scanned']}\n")
                f.write(f"Hardlinked Files:         {summary['hardlinked_count']}\n")
                f.write(f"Non-Hardlinked Files:     {summary['non_hardlinked_count']}\n")
                f.write(f"Errors Encountered:       {summary['errors']}\n")
                f.write(f"Total Size:               {summary['total_size']}\n")
                f.write(f"Non-Hardlinked Size:      {summary['non_hardlinked_size']}\n")
                f.write(f"Percentage Not Hardlinked: {summary['percentage_not_hardlinked']}%\n")
                f.write("\n")

                # Write detailed file list
                if non_hardlinked_files:
                    f.write("=" * 80 + "\n")
                    f.write("NON-HARDLINKED FILES\n")
                    f.write("=" * 80 + "\n\n")

                    for i, file_info in enumerate(non_hardlinked_files, 1):
                        f.write(f"[{i}] {file_info['path']}\n")
                        f.write(f"    Size:         {file_info['size_human']} ({file_info['size_bytes']} bytes)\n")
                        f.write(f"    Link Count:   {file_info['link_count']}\n")
                        f.write(f"    Inode:        {file_info['inode']}\n")
                        f.write(f"    Modified:     {file_info['modified']}\n")
                        f.write("\n")
                else:
                    f.write("=" * 80 + "\n")
                    f.write("All files are properly hardlinked!\n")
                    f.write("=" * 80 + "\n")

            logging.info(f"Report generated: {self.output_path}")

        except (OSError, PermissionError) as e:
            logging.error(f"Failed to write report: {e}")
            raise


def main():
    """Main entry point for the script."""
    try:
        # Initialize checker
        checker = HardlinkChecker()

        # Scan directory
        non_hardlinked_files, summary = checker.scan_directory()

        # Generate report
        checker.generate_report(non_hardlinked_files, summary)

        # Print summary to console
        print("\n" + "=" * 80)
        print("SCAN COMPLETE")
        print("=" * 80)
        print(f"Total files scanned:      {summary['total_files_scanned']}")
        print(f"Non-hardlinked files:     {summary['non_hardlinked_count']}")
        print(f"Report saved to:          {checker.output_path}")
        print("=" * 80 + "\n")

        # Exit with appropriate code
        sys.exit(0 if summary['non_hardlinked_count'] == 0 else 1)

    except FileNotFoundError as e:
        logging.error(f"File not found: {e}")
        sys.exit(2)
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON configuration: {e}")
        sys.exit(3)
    except KeyError as e:
        logging.error(f"Configuration error: {e}")
        sys.exit(4)
    except KeyboardInterrupt:
        logging.info("\nOperation cancelled by user")
        sys.exit(130)
    except Exception as e:
        logging.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
