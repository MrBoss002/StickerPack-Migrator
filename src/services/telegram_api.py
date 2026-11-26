import asyncio
import time
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
    Core service to clone a sticker pack with live telemetry, elapsed time, and nap counters.
    """
    start_time = time.time()
    nap_count = 0
    total_nap_time = 0

    async def report(status_msg: str):
        if progress_callback:
            elapsed = round(time.time() - start_time, 1)
            await progress_callback(status_msg, elapsed, nap_count, total_nap_time)

    try:
        await report("📥 Fetching source sticker pack...")
        source_pack = await bot.get_sticker_set(name=source_short_name)
        
        if not source_pack.stickers:
            raise ValueError("The source sticker pack is empty.")

        # Take a safe anti-flood nap
        nap_start = time.time()
        nap_count += 1
        await report("💤 Taking a safe anti-flood nap (1.5s)...")
        await asyncio.sleep(1.5)
        total_nap_time += round(time.time() - nap_start, 1)

        await report("⚙️ Preparing stickers and formats...")

        if source_pack.is_animated:
            sticker_format = "animated"
        elif source_pack.is_video:
            sticker_format = "video"
        else:
            sticker_format = "static"

        bot_info = await bot.get_me()
        full_short_name = f"{new_short_name}_by_{bot_info.username}"

        input_stickers = []
        for sticker in source_pack.stickers:
            input_stickers.append(
                InputSticker(
                    sticker=sticker.file_id,
                    emoji_list=sticker.emoji_list if hasattr(sticker, 'emoji_list') else [sticker.emoji],
                    format=sticker_format
                )
            )

        # Another safe break before calling Telegram's creation endpoint
        nap_start = time.time()
        nap_count += 1
        await report(f"🚀 Preparing set with {len(input_stickers)} stickers. Taking a resting break (2.0s)...")
        await asyncio.sleep(2.0)
        total_nap_time += round(time.time() - nap_start, 1)

        success = await bot.create_new_sticker_set(
            user_id=user_id,
            name=full_short_name,
            title=new_title,
            stickers=input_stickers,
            sticker_format=sticker_format,
            sticker_type=source_pack.sticker_type
        )

        if success:
            nap_start = time.time()
            nap_count += 1
            await report("✨ Finalizing setup...")
            await asyncio.sleep(1.0)
            total_nap_time += round(time.time() - nap_start, 1)

            total_duration = round(time.time() - start_time, 1)
            return {
                "link": f"https://t.me/addstickers/{full_short_name}",
                "total_time": total_duration,
                "nap_count": nap_count,
                "nap_time": round(total_nap_time, 1)
            }
        else:
            raise Exception("Telegram returned False when creating the sticker set.")

    except TelegramBadRequest as e:
        raise Exception(f"Telegram API Error: {e.message}")
    except Exception as e:
        raise Exception(f"Cloning failed: {str(e)}")
