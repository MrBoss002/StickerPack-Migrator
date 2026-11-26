import asyncio
from aiogram import Bot
from aiogram.types import InputSticker
from aiogram.exceptions import TelegramBadRequest

async def clone_sticker_pack(
    bot: Bot,
    user_id: int,
    source_short_name: str,
    new_title: str,
    new_short_name: str,
    icon_file_id: str = None,
    progress_callback = None
):
    """
    Core service to clone a sticker pack with built-in delays to respect Telegram flood limits.
    """
    try:
        if progress_callback:
            await progress_callback("📥 Fetching source sticker pack...")
        
        # 1. Fetch the source sticker pack
        source_pack = await bot.get_sticker_set(name=source_short_name)
        
        if not source_pack.stickers:
            raise ValueError("The source sticker pack is empty.")

        # Brief pause to respect Telegram API rate limits
        await asyncio.sleep(1.5)

        if progress_callback:
            await progress_callback("⚙️ Preparing stickers and formatting...")

        # 2. Determine sticker format type (static, animated, or video)
        if source_pack.is_animated:
            sticker_format = "animated" # .tgs
        elif source_pack.is_video:
            sticker_format = "video"    # .webm
        else:
            sticker_format = "static"   # .png / .webp

        # Construct the full internal name required by Telegram
        bot_info = await bot.get_me()
        full_short_name = f"{new_short_name}_by_{bot_info.username}"

        # 3. Map existing stickers into InputSticker objects
        input_stickers = []
        for sticker in source_pack.stickers:
            input_stickers.append(
                InputSticker(
                    sticker=sticker.file_id,
                    emoji_list=sticker.emoji_list if hasattr(sticker, 'emoji_list') else [sticker.emoji],
                    format=sticker_format
                )
            )

        if progress_callback:
            await progress_callback(f"🚀 Creating new sticker pack with {len(input_stickers)} stickers (taking a safe pause to avoid flood limits)...")

        # Give Telegram breathing room before creating the set to avoid flood control
        await asyncio.sleep(2.0)

        # 4. Create the new sticker set using the bot's account
        success = await bot.create_new_sticker_set(
            user_id=user_id,
            name=full_short_name,
            title=new_title,
            stickers=input_stickers,
            sticker_format=sticker_format,
            sticker_type=source_pack.sticker_type
        )

        if success:
            await asyncio.sleep(1.0)
            return f"https://t.me/addstickers/{full_short_name}"
        else:
            raise Exception("Telegram returned False when creating the sticker set.")

    except TelegramBadRequest as e:
        raise Exception(f"Telegram API Error: {e.message}")
    except Exception as e:
        raise Exception(f"Cloning failed: {str(e)}")
