
# join_bot.py
# -------------------------------
# SPX - JOIN BOT (aiogram v3)
# -------------------------------
# هذا البوت:
#  - يعمل بـ aiogram v3
#  - يقرأ التوكن من env: JOIN_TOKEN
#  - يرحّب بالمستخدم عبر /start
#  - يوافق تلقائياً على طلبات الانضمام (Chat Join Requests)
#  - يرسل رسالة ترحيب خاصة للمستخدم (إن أمكن)
#
# Start Command (Render):  python3 join_bot.py

import os
import asyncio
from contextlib import suppress

# نحاول استيراد settings (اختياري). لو غير موجود، نقرأ من البيئة مباشرة.
JOIN_TOKEN = os.getenv("JOIN_TOKEN")
try:
    import settings  # ملف اختياري فيه قراءة ENV والتحقق
    if not JOIN_TOKEN:
        JOIN_TOKEN = getattr(settings, "JOIN_TOKEN", None)
except Exception:
    # لو ما في settings.py، نكمل بالبيئة فقط
    pass

if not JOIN_TOKEN or not isinstance(JOIN_TOKEN, str):
    raise RuntimeError("JOIN_TOKEN is missing or invalid. "
                       "Set it in Render → Environment → JOIN_TOKEN.")

from aiogram import Bot, Dispatcher, Router, F
from aiogram.client.default import DefaultBotProperties
from aiogram.types import (
    Message,
    ChatJoinRequest,
    BotCommand,
)
from aiogram.exceptions import TelegramBadRequest

router = Router()

# ===== أوامر البوت الأساسية =====
@router.message(F.text == "/start")
async def cmd_start(msg: Message):
    text = (
        "أهلًا بك 👋\n"
        "أنا بوت الانضمام. أوافق على طلبات الانضمام للقناة/المجموعة تلقائيًا.\n"
        "جرّب: /ping"
    )
    await msg.answer(text)

@router.message(F.text == "/ping")
async def cmd_ping(msg: Message):
    await msg.answer("pong ✅")

# ===== التعامل مع طلبات الانضمام =====
@router.chat_join_request()
async def on_join_request(req: ChatJoinRequest):
    """
    يوافق تلقائيًا على طلبات الانضمام.
    يلزم تفعيل 'Approve new members' في إعدادات القناة/المجموعة.
    """
    # قبول الطلب
    await req.approve()
    # محاولة إرسال رسالة ترحيب خاصة للمستخدم (قد تُرفض لو لم يبدأ محادثة مع البوت)
    welcome_pm = (
        f"مرحبًا {req.from_user.full_name} 🎉\n"
        f"تم قبول طلبك للانضمام إلى: {req.chat.title}"
    )
    with suppress(TelegramBadRequest):
        await req.bot.send_message(req.from_user.id, welcome_pm)

# ===== الإقلاع =====
async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="بدء / المساعدة"),
        BotCommand(command="ping", description="اختبار البوت"),
    ]
    with suppress(Exception):
        await bot.set_my_commands(commands)

async def main():
    bot = Bot(
        token=JOIN_TOKEN,
        default=DefaultBotProperties(parse_mode="HTML"),
    )
    dp = Dispatcher()
    dp.include_router(router)
    await set_bot_commands(bot)
    print("JOIN BOT is running…")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
