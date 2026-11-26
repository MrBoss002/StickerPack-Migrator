from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

# Define reusable keyboard for updates and support
def get_support_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📢 Updates", url="https://t.me/MrBossBotz"),
                InlineKeyboardButton(text="🛠️ Support", url="https://t.me/MrBossSupport")
            ]
        ]
    )

@router.message(CommandStart())
async def cmd_start(message: Message):
    welcome_text = (
        "👋 <b>Welcome to Sticker-Renamer!</b>\n\n"
        "I can help you clone, rename, and customize existing Telegram sticker packs "
        "under a brand-new link and title.\n\n"
        "📌 <b>How to use:</b>\n"
        "Simply send me any Telegram sticker pack link (e.g., <code>https://t.me/addstickers/Animals</code>) "
        "to get started!"
    )
    await message.answer(welcome_text, parse_mode="HTML", reply_markup=get_support_keyboard())

@router.message(Command("help"))
async def cmd_help(message: Message):
    help_text = (
        "🛠️ <b>Sticker-Renamer Help</b>\n\n"
        "1️⃣ Send a sticker pack link to the bot.\n"
        "2️⃣ Provide a new display name for the pack.\n"
        "3️⃣ Choose a custom short link suffix.\n"
        "4️⃣ Choose a custom icon or type <code>/skip</code> to use the first sticker.\n\n"
        "That's it! Your cloned pack will be ready instantly."
    )
    await message.answer(help_text, parse_mode="HTML", reply_markup=get_support_keyboard())
