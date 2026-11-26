import os
import aiofiles

TEMP_DIR = "temp_downloads"

async def ensure_temp_dir():
    """Ensure the temporary download directory exists."""
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)

async def save_temp_file(file_bytes: bytes, filename: str) -> str:
    """
    Saves binary file content temporarily to disk.
    """
    await ensure_temp_dir()
    file_path = os.path.join(TEMP_DIR, filename)
    
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(file_bytes)
        
    return file_path

async def cleanup_temp_file(file_path: str):
    """
    Safely deletes a temporary file from disk.
    """
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception:
            pass
