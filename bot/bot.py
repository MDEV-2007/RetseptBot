"""
MediScript Telegram Bot  (aiogram 3.x)

Run:
    python bot/bot.py

The bot:
  • /start  — welcome message + "Open MediScript" button
  • /help   — instructions
  • Doctors registered in Django (with telegram_id) can receive
    prescription PDFs directly from the web app.
"""
import asyncio
import logging
import os
import sys

# Allow importing Django settings when running standalone
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

router = Router()


def get_token() -> str:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    if not token:
        try:
            from decouple import config as _cfg
            token = _cfg("TELEGRAM_BOT_TOKEN", default="")
        except ImportError:
            pass
    if not token:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN is not set. "
            "Add it to your .env file or environment variables."
        )
    return token


def get_app_url() -> str:
    url = os.environ.get("DJANGO_APP_URL", "")
    if not url:
        try:
            from decouple import config as _cfg
            url = _cfg("DJANGO_APP_URL", default="http://localhost:8000")
        except ImportError:
            url = "http://localhost:8000"
    return url.rstrip("/")


# ── /start ────────────────────────────────────────────────────────────────────

@router.message(Command("start"))
async def cmd_start(message: types.Message) -> None:
    app_url = get_app_url()
    user = message.from_user

    # Build keyboard — prefer WebApp if HTTPS, otherwise a plain URL button
    if app_url.startswith("https://"):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(
                text="⚕ Open MediScript",
                web_app=WebAppInfo(url=f"{app_url}/dashboard/"),
            )
        ]])
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(
                text="⚕ Open MediScript",
                url=f"{app_url}/dashboard/",
            )
        ]])

    await message.answer(
        f"👋 Hello, *{user.full_name}*!\n\n"
        "Welcome to *MediScript* — the Medical Prescription System.\n\n"
        "With MediScript you can:\n"
        "• Manage patients\n"
        "• Create prescriptions\n"
        "• Download & print PDFs\n"
        "• Receive prescriptions right here in Telegram\n\n"
        "Tap the button below to open the app:",
        parse_mode="Markdown",
        reply_markup=keyboard,
    )


# ── /help ─────────────────────────────────────────────────────────────────────

@router.message(Command("help"))
async def cmd_help(message: types.Message) -> None:
    await message.answer(
        "*MediScript Help*\n\n"
        "Commands:\n"
        "  /start — Open the app\n"
        "  /help  — Show this message\n\n"
        "To receive prescriptions here:\n"
        "1. Log in to MediScript with your Telegram ID\n"
        "2. Create a prescription\n"
        "3. Press *Send via Telegram* in the app\n\n"
        "Your Telegram ID: `{}`".format(message.from_user.id),
        parse_mode="Markdown",
    )


# ── Fallback ───────────────────────────────────────────────────────────────────

@router.message()
async def fallback(message: types.Message) -> None:
    await message.answer(
        "Use /start to open MediScript or /help for instructions."
    )


# ── Main ───────────────────────────────────────────────────────────────────────

async def main() -> None:
    token = get_token()
    bot = Bot(token=token)
    dp = Dispatcher()
    dp.include_router(router)

    logger.info("MediScript bot starting…")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
