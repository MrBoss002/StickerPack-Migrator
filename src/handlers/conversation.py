import re
import time
import asyncio
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from src.services.telegram_api import clone_sticker_pack

router = Router()

# Dictionary to track last successful clone timestamp per user ID for speed control
USER_COOLDOWN_TRACKER = {}
COOLDOWN_SECONDS = 15

class CloneStickerStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_shortname = State()
    waiting_for_icon = State()

STICKER_REGEX = re.compile(r"(?:https?://)?(?:t\.me|telegram\.me)/addstickers/([a-zA-Z0-9_]+)")

@router.message(StateFilter(None), F.text & ~F.text.startswith("/"))
async def process_sticker_link(message: Message, state: FSMContext):
    user_id = message.from_user.id
    current_time = time.time()
    
    # Check if user is on post-clone safety cooldown
    if user_id in USER_COOLDOWN_TRACKER:
        elapsed_since_last = current_time - USER_COOLDOWN_TRACKER[user_id]
        if elapsed_since_last < COOLDOWN_SECONDS:
            remaining = int(COOLDOWN_SECONDS - elapsed_since_last)
            
            # Send initial cooldown warning message with live editing
            cd_msg = await message.answer(
                f"🛡️ <b>Speed Control Enabled For Your Safety!</b>\n\n"
                f"⏳ Please slow down. Cooldown active: <b>{remaining}s</b> remaining...",
                parse_mode="HTML"
            )
            
            while remaining > 0:
                await asyncio.sleep(min(5, remaining))
                remaining = max(0, int(COOLDOWN_SECONDS - (time.time() - USER_COOLDOWN_TRACKER[user_id])))
                if remaining > 0:
                    try:
                        await cd_msg.edit_text(
                            f"🛡️ <b>Speed Control Enabled For Your Safety!</b>\n\n"
                            f"⏳ Please slow down. Cooldown active: <b>{remaining}s</b> remaining...",
                            parse_mode="HTML"
                        )
                    except Exception:
                        pass
            
            try:
                await cd_msg.edit_text("✅ <b>Cooldown finished!</b> You are ready to go. Send your sticker link again:", parse_mode="HTML")
            except Exception:
                pass
            return

    match = STICKER_REGEX.search(message.text)
    if not match:
        await message.answer("⚠️ Please send a valid Telegram sticker pack link to start cloning (e.g., <code>https://t.me/addstickers/...</code>)", parse_mode="HTML")
        return
    
    source_short_name = match.group(1)
    await state.update_data(source_short_name=source_short_name)
    
    await message.answer(
        f"✅ <b>Source pack detected:</b> <code>{source_short_name}</code>\n\n"
        "Now, send me the <b>Display Name</b> for your new sticker pack:",
        parse_mode="HTML"
    )
    await state.set_state(CloneStickerStates.waiting_for_title)

@router.message(CloneStickerStates.waiting_for_title, F.text & ~F.text.startswith("/"))
async def process_title(message: Message, state: FSMContext):
    await state.update_data(new_title=message.text.strip())
    await message.answer(
        "📝 Great! Now send the <b>Short Name / URL Suffix</b> for the link "
        "(e.g., <code>my_awesome_pack</code> so the final link becomes <code>t.me/addstickers/my_awesome_pack</code>):",
        parse_mode="HTML"
    )
    await state.set_state(CloneStickerStates.waiting_for_shortname)

@router.message(CloneStickerStates.waiting_for_shortname, F.text & ~F.text.startswith("/"))
async def process_shortname(message: Message, state: FSMContext):
    shortname = message.text.strip()
    
    if not re.match(r"^[a-zA-Z0-9_]+$", shortname):
        await message.answer(
            "❌ Invalid format. Short names can only contain letters, numbers, and underscores. Try again:",
            parse_mode="HTML"
        )
        return

    bot_info = await message.bot.get_me()
    full_short_name = f"{shortname}_by_{bot_info.username}"

    try:
        await message.bot.get_sticker_set(name=full_short_name)
        await message.answer(
            "❌ <b>Short name already taken!</b> Another pack is already using this suffix. Please choose a different one:",
            parse_mode="HTML"
        )
        return
    except Exception:
        pass

    await state.update_data(new_shortname=shortname)
    await message.answer(
        "🖼️ Almost done! Send a <b>custom icon/thumbnail image</b> for the pack, "
        "or type <code>/skip</code> to use the first sticker from the pack automatically.",
        parse_mode="HTML"
    )
    await state.set_state(CloneStickerStates.waiting_for_icon)

@router.message(CloneStickerStates.waiting_for_icon)
async def process_icon(message: Message, state: FSMContext):
    icon_file_id = None

    if message.text and message.text.lower() == "/skip":
        pass
    elif message.photo:
        icon_file_id = message.photo[-1].file_id
    else:
        await message.answer("⚠️ Please send a valid image file as a photo, or type <code>/skip</code>.", parse_mode="HTML")
        return

    data = await state.get_data()
    await state.clear()

    progress_msg = await message.answer("⏳ <b>Initializing cloning sequence...</b>", parse_mode="HTML")

    # Callback to update the live progress message with HTML telemetry
    async def update_progress(status: str, elapsed: float, naps: int, nap_duration: float):
        try:
            await progress_msg.edit_text(
                f"⏳ <b>Cloning in Progress...</b>\n\n"
                f"{status}\n\n"
                f"⏱️ <b>Elapsed Time:</b> {elapsed}s\n"
                f"💤 <b>Rest Naps Taken:</b> {naps} ({nap_duration}s total)",
                parse_mode="HTML"
            )
        except Exception:
            pass

    try:
        result = await clone_sticker_pack(
            bot=message.bot,
            user_id=message.from_user.id,
            source_short_name=data.get('source_short_name'),
            new_title=data.get('new_title'),
            new_short_name=data.get('new_shortname'),
            icon_file_id=icon_file_id,
            progress_callback=update_progress
        )

        # Record cooldown timestamp right upon successful completion
        USER_COOLDOWN_TRACKER[message.from_user.id] = time.time()

        # Format links cleanly with HTML anchor tags
        links_text = "\n".join([f"• <a href=\"{link}\">{link}</a>" for link in result['links']])

        await progress_msg.edit_text(
            "🎉 <b>Sticker Pack Cloned Successfully!</b>\n\n"
            f"🔗 <b>New Pack Link(s):</b>\n{links_text}\n\n"
            f"📊 <b>Cloning Statistics:</b>\n"
            f"• ⏱️ <b>Total Time Taken:</b> {result['total_time']} seconds\n"
            f"• 💤 <b>Anti-Flood Naps:</b> {result['nap_count']} breaks ({result['nap_time']}s total)",
            parse_mode="HTML"
        )
    except Exception as e:
        await progress_msg.edit_text(f"❌ <b>Cloning Failed:</b>\n<code>{str(e)}</code>", parse_mode="HTML")
