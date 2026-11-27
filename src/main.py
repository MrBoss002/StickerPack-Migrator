import os
import asyncio
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from aiogram import Bot, Dispatcher
from src.config import BOT_TOKEN
from src.handlers.commands import router as commands_router
from src.handlers.conversation import router as conversation_router

# Configure detailed logging to see timestamps, levels, and source modules in Render logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)

# 1. Dummy HTTP handler to satisfy Render's port detection requirement
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive and polling!")
        
    def log_message(self, format, *args):
        # Suppress access logs to keep the terminal clean
        pass

def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

async def main():
    # 2. Start the dummy server in a background thread
    threading.Thread(target=run_dummy_server, daemon=True).start()
    logger.info("🌐 Dummy HTTP health-check server started on port %s", os.environ.get("PORT", 10000))

    # Initialize Bot and Dispatcher
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Register all routers (handlers & conversation wizard)
    dp.include_router(commands_router)
    dp.include_router(conversation_router)

    logger.info("🤖 Sticker-Renamer bot is starting...")
    
    # Start polling safely with exception trapping
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.exception(f"CRITICAL: Polling stopped unexpectedly due to error: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped manually via KeyboardInterrupt!")
    except Exception as e:
        logger.exception(f"CRITICAL: Main loop crashed: {e}")
