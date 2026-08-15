import os
import shutil
import logging

logger = logging.getLogger(__name__)

def cleanup_directory(dir_path: str):
    if dir_path and os.path.exists(dir_path):
        try:
            shutil.rmtree(dir_path)
        except Exception as e:
            logger.error(f"Error cleaning directory {dir_path}: {e}")

def cleanup_file(file_path: str):
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            logger.error(f"Error removing file {file_path}: {e}")
