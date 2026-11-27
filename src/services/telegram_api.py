import asyncio
import time
import logging
from aiogram import Bot
from aiogram.types import InputSticker
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter

logger = logging.getLogger(__name__)

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
    Core service to clone a sticker pack capped at a single set (max 50 stickers),
    with full traceback logging, clean naming, and safe anti-flood handling.
    """
    start_time = time.time()
    nap_count = 0
    total_nap_time = 0

    async def report(status_msg: str):
        if progress_callback:
            elapsed = round(time.time() - start_time, 1)
            await progress_callback(status_msg, elapsed, nap_count, total_nap_time)

    try:
        logger.info(f"[CLONE START] User {user_id} requested cloning of source pack '{source_short_name}' -> new suffix '{new_short_name}'")
        await report("📥 Fetching source sticker pack...")
        
        source_pack = await bot.get_sticker_set(name=source_short_name)
        if not source_pack.stickers:
            raise ValueError("The source sticker pack is empty.")

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
        
        # Map stickers and cap at a maximum of 50 stickers
        input_stickers = []
        for sticker in source_pack.stickers[:50]:
            input_stickers.append(
                InputSticker(
                    sticker=sticker.file_id,
                    emoji_list=sticker.emoji_list if hasattr(sticker, 'emoji_list') else [sticker.emoji],
                    format=sticker_format
                )
            )

        full_short_name = f"{new_short_name}_by_{bot_info.username}"
        logger.info(f"[CLONE] Preparing set '{full_short_name}' with {len(input_stickers)} stickers (Format: {sticker_format})")

        await report(f"🚀 Creating sticker pack ({len(input_stickers)} stickers)...")

        # Create the sticker pack safely in one go
        success = False
        retry_count = 0
        max_retries = 3

        while not success and retry_count < max_retries:
            try:
                success = await bot.create_new_sticker_set(
                    user_id=user_id,
                    name=full_short_name,
                    title=new_title,
                    stickers=input_stickers,
                    sticker_format=sticker_format
                )
            except TelegramRetryAfter as ex:
                retry_count += 1
                logger.warning(f"[FLOOD LIMIT] Hit TelegramRetryAfter for user {user_id}: retry_after={ex.retry_after}s (Attempt {retry_count}/{max_retries})")
                if retry_count >= max_retries:
                    raise Exception("Telegram flood limit exceeded. Please try again later.")
                
                wait_seconds = ex.retry_after + 5
                nap_count += 1
                total_nap_time += wait_seconds
                await report(f"💤 Telegram flood limit hit! Sleeping for {wait_seconds}s...")
                await asyncio.sleep(wait_seconds)

        if not success:
            raise Exception("Telegram returned False when creating the sticker set.")

        # If a custom icon/thumbnail was provided, set it now. If skipped, Telegram handles it automatically.
        if icon_file_id:
            try:
                await report("🖼️ Setting custom pack thumbnail...")
                await bot.set_sticker_set_thumbnail(
                    name=full_short_name,
                    user_id=user_id,
                    thumbnail=icon_file_id
                )
            except Exception as thumb_err:
                logger.warning(f"[THUMBNAIL WARNING] Failed to set custom thumbnail for {full_short_name}: {thumb_err}")

        created_link = f"https://t.me/addstickers/{full_short_name}"
        logger.info(f"[CLONE SUCCESS] Pack successfully created for user {user_id}: {created_link}")

        nap_start = time.time()
        nap_count += 1
        await report("✨ Finalizing setup...")
        await asyncio.sleep(1.0)
        total_nap_time += round(time.time() - nap_start, 1)

        total_duration = round(time.time() - start_time, 1)
        return {
            "links": [created_link],
            "total_time": total_duration,
            "nap_count": nap_count,
            "nap_time": round(total_nap_time, 1)
        }

    except TelegramBadRequest as e:
        logger.error(f"[TELEGRAM BAD REQUEST] User {user_id}: {e.message}", exc_info=True)
        raise Exception(f"Telegram API Error: {e.message}")
    except Exception as e:
        logger.exception(f"[CLONE ERROR] Unhandled exception during cloning for user {user_id}: {str(e)}")
        raise Exception(f"Cloning failed: {str(e)}")
