import re
import asyncio

# Regex to validate Telegram sticker set short names (only letters, numbers, underscores)
SHORTNAME_REGEX = re.compile(r"^[a-zA-Z0-9_]+$")

def validate_shortname(shortname: str) -> bool:
    """
    Validates that a shortname matches Telegram's strict naming rules.
    """
    if not shortname or len(shortname) > 64:
        return bool(False)
    return bool(SHORTNAME_REGEX.match(shortname))

async def safe_sleep(seconds: float = 1.0):
    """
    Async helper for rate-limiting delays between Telegram API calls if needed.
    """
    await asyncio.sleep(seconds)
