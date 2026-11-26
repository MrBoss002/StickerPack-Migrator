import re
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

router = Router()

# Define FSM states for the cloning wizard
class CloneStickerStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_shortname = State()
    waiting_for_icon = State()

# Regex to detect Telegram sticker pack links
STICKER_REGEX = re.compile(r"(?:https?://)?(?:t\.me|telegram\.me)/addstickers/([a-zA-Z0-9_]+)")

@router.message(F.text & ~F.text.startswith("/"))
async def process_sticker_link(message: Message, state: FSMContext):
    """
    Step 1: Detects when a user sends a valid Telegram sticker pack link.
    """
    match = STICKER_REGEX.search(message.text)
    if not match:
        return  # Ignore regular text messages that aren't sticker links
    
    source_short_name = match.group(1)
    
    # Save source pack name into FSM session data
    await state.update_data(source_short_name=source_short_name)
    
    await message.answer(
        f"✅ **Source pack detected:** `{source_short_name}`\n\n"
        "Now, send me the **Display Name** for your new sticker pack:",
        parse_mode="Markdown"
    )
    # Transition to next state
    await state.set_state(CloneStickerStates.waiting_for_title)

@router.message(CloneStickerStates.waiting_for_title, F.text)
async def process_title(message: Message, state: FSMContext):
    """
    Step 2: Captures the new display title for the pack.
    """
    await state.update_data(new_title=message.text.strip())
    await message.answer(
        "📝 Great! Now send the **Short Name / URL Suffix** for the link "
        "(e.g., `my_awesome_pack` so the final link becomes `t.me/addstickers/my_awesome_pack`):"
    )
    await state.set_state(CloneStickerStates.waiting_for_shortname)

@router.message(CloneStickerStates.waiting_for_shortname, F.text)
async def process_shortname(message: Message, state: FSMContext):
    """
    Step 3: Validates and captures the new URL short name.
    """
    shortname = message.text.strip()
    
    # Telegram short names only allow letters, numbers, and underscores
    if not re.match(r"^[a-zA-Z0-9_]+$", shortname):
        await message.answer(
            "❌ Invalid format. Short names can only contain letters, numbers, and underscores. Try again:"
        )
        return

    await state.update_data(new_shortname=shortname)
    await message.answer(
        "🖼️ Almost done! Send a **custom icon/thumbnail image** for the pack, "
        "or type `/skip` to use the first sticker from the pack automatically."
    )
    await state.set_state(CloneStickerStates.waiting_for_icon)

@router.message(CloneStickerStates.waiting_for_icon)
async def process_icon(message: Message, state: FSMContext):
    """
    Step 4: Handles custom icon upload or skips to default.
    """
    icon_file_id = None

    if message.text and message.text.lower() == "/skip":
        await message.answer("⏭️ Icon skipped. Using the first sticker as default.")
    elif message.photo:
        # Grab the highest resolution photo provided
        icon_file_id = message.photo[-1].file_id
        await message.answer("✅ Custom icon received!")
    else:
        await message.answer("⚠️ Please send a valid image file as a photo, or type `/skip`.")
        return

    await state.update_data(icon_file_id=icon_file_id)

    # Collect all accumulated data from state
    data = await state.get_data()
    
    # Clear the state session to finish the wizard
    await state.clear()

    # Summary preview (Next step will connect this to telegram_api.py execution)
    summary = (
        "🚀 **Cloning Parameters Collected!**\n\n"
        f"• **Source Pack:** `{data.get('source_short_name')}`\n"
        f"• **New Title:** `{data.get('new_title')}`\n"
        f"• **New Link Name:** `{data.get('new_shortname')}`\n"
        f"• **Custom Icon:** `{'Provided' if data.get('icon_file_id') else 'Skipped (Default)'}`\n\n"
        "⏳ *Triggering cloning process... (Next, we will wire this to your Telegram API service!)*"
    )
    await message.answer(summary, parse_mode="Markdown")
