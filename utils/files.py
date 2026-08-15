import os
import uuid
import shutil

def create_user_temp_dir() -> str:
    unique_id = str(uuid.uuid4())
    path = os.path.join("/tmp", "bot_temp", unique_id)
    os.makedirs(path, exist_ok=True)
    return path

def is_safe_filename(filename: str) -> bool:
    if not filename:
        return False
    clean_name = os.path.basename(filename)
    return clean_name == filename and ".." not in filename
