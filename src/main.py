import os
import asyncio
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from aiogram import Bot, Dispatcher
from src.config import BOT_TOKEN
from src.handlers.commands import router as commands_router
from src.handlers.conversation import router as conversation_router

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
    # Configure logging to see events in your terminal
    logging.basicConfig(level=logging.INFO)
    
    # 2. Start the dummy server in a background thread (so it binds to the port instantly)
    threading.Thread(target=run_dummy_server, daemon=True).start()
    logging.info("🌐 Dummy HTTP health-check server started on port %s", os.environ.get("PORT", 10000))

    # Initialize Bot and Dispatcher
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Register all routers (handlers & conversation wizard)
    dp.include_router(commands_router)
    dp.include_router(conversation_router)

    print("🤖 Sticker-Renamer bot is starting...")
    
    # Start polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Bot stopped successfully!")
