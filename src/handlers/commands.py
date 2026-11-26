from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    welcome_text = (
        "👋 **Welcome to Sticker-Renamer!**\n\n"
        "I can help you clone, rename, and customize existing Telegram sticker packs "
        "under a brand-new link and title.\n\n"
        "📌 **How to use:**\n"
        "Simply send me any Telegram sticker pack link (e.g., `https://t.me/addstickers/Animals`) "
        "to get started!"
    )
    await message.answer(welcome_text, parse_mode="Markdown")

@router.message(Command("help"))
async def cmd_help(message: Message):
    help_text = (
        "🛠️ **Sticker-Renamer Help**\n\n"
        "1️⃣ Send a sticker pack link to the bot.\n"
        "2️⃣ Provide a new display name for the pack.\n"
        "3️⃣ Choose a custom short link suffix.\n"
        "4️⃣ Choose a custom icon or type `/skip` to use the first sticker.\n\n"
        "That's it! Your cloned pack will be ready instantly."
    )
    await message.answer(help_text, parse_mode="Markdown")
