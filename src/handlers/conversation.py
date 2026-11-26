import re
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from src.services.telegram_api import clone_sticker_pack

router = Router()

class CloneStickerStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_shortname = State()
    waiting_for_icon = State()

STICKER_REGEX = re.compile(r"(?:https?://)?(?:t\.me|telegram\.me)/addstickers/([a-zA-Z0-9_]+)")

# 1. Entry point: Only triggers when user is NOT in any active state (idle)
@router.message(StateFilter(None), F.text & ~F.text.startswith("/"))
async def process_sticker_link(message: Message, state: FSMContext):
    match = STICKER_REGEX.search(message.text)
    if not match:
        await message.answer("⚠️ Please send a valid Telegram sticker pack link to start cloning (e.g., `https://t.me/addstickers/...`)")
        return
    
    source_short_name = match.group(1)
    await state.update_data(source_short_name=source_short_name)
    
    await message.answer(
        f"✅ **Source pack detected:** `{source_short_name}`\n\n"
        "Now, send me the **Display Name** for your new sticker pack:",
        parse_mode="Markdown"
    )
    await state.set_state(CloneStickerStates.waiting_for_title)

# 2. Step 1: Receiving Display Name
@router.message(CloneStickerStates.waiting_for_title, F.text & ~F.text.startswith("/"))
async def process_title(message: Message, state: FSMContext):
    await state.update_data(new_title=message.text.strip())
    await message.answer(
        "📝 Great! Now send the **Short Name / URL Suffix** for the link "
        "(e.g., `my_awesome_pack` so the final link becomes `t.me/addstickers/my_awesome_pack`):"
    )
    await state.set_state(CloneStickerStates.waiting_for_shortname)

# 3. Step 2: Receiving Short Name & Checking Availability
@router.message(CloneStickerStates.waiting_for_shortname, F.text & ~F.text.startswith("/"))
async def process_shortname(message: Message, state: FSMContext):
    shortname = message.text.strip()
    
    if not re.match(r"^[a-zA-Z0-9_]+$", shortname):
        await message.answer(
            "❌ Invalid format. Short names can only contain letters, numbers, and underscores. Try again:"
        )
        return

    # Construct full name: <shortname>_by_<bot_username>
    bot_info = await message.bot.get_me()
    full_short_name = f"{shortname}_by_{bot_info.username}"

    # Check if the short name is already occupied on Telegram
    try:
        await message.bot.get_sticker_set(name=full_short_name)
        # If this succeeds, the pack already exists!
        await message.answer(
            "❌ **Short name already taken!** Another pack is already using this suffix. Please choose a different one:"
        )
        return
    except Exception:
        # If it throws an exception, the pack doesn't exist yet -> Name is available!
        pass

    await state.update_data(new_shortname=shortname)
    await message.answer(
        "🖼️ Almost done! Send a **custom icon/thumbnail image** for the pack, "
        "or type `/skip` to use the first sticker from the pack automatically."
    )
    await state.set_state(CloneStickerStates.waiting_for_icon)

# 4. Step 3: Receiving Icon / Skip & Executing Clone
@router.message(CloneStickerStates.waiting_for_icon)
async def process_icon(message: Message, state: FSMContext):
    icon_file_id = None

    if message.text and message.text.lower() == "/skip":
        pass
    elif message.photo:
        icon_file_id = message.photo[-1].file_id
    else:
        await message.answer("⚠️ Please send a valid image file as a photo, or type `/skip`.")
        return

    data = await state.get_data()
    await state.clear()

    progress_msg = await message.answer("⏳ Cloning sticker pack... Please wait a moment.")

    try:
        # Execute the cloning service
        new_pack_link = await clone_sticker_pack(
            bot=message.bot,
            user_id=message.from_user.id,
            source_short_name=data.get('source_short_name'),
            new_title=data.get('new_title'),
            new_short_name=data.get('new_shortname'),
            icon_file_id=icon_file_id
        )

        await progress_msg.edit_text(
            "🎉 **Sticker Pack Cloned Successfully!**\n\n"
            f"🔗 **Your New Pack Link:** {new_pack_link}",
            parse_mode="Markdown"
        )
    except Exception as e:
        await progress_msg.edit_text(f"❌ **Cloning Failed:**\n`{str(e)}`", parse_mode="Markdown")
