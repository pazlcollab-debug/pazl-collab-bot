from aiogram import Router, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import WEBAPP_URL

router = Router()

# ==========================
# ⚙️ Мой профиль
# ==========================
@router.message(lambda msg: msg.text in ["⚙️ Мой профиль", "⚙️ My profile"])
async def open_profile(message: types.Message):
    """Открывает Mini App с профилем пользователя"""
    telegram_id = message.from_user.id
    
    # 💡 ВАЖНО: Mini App находится в /webapp
    webapp_url = f"{WEBAPP_URL}/webapp/profile/{telegram_id}"

    # создаём inline-кнопку с WebApp
    builder = InlineKeyboardBuilder()
    builder.button(
        text="🌐 Открыть мой профиль",
        web_app=types.WebAppInfo(url=webapp_url)
    )

    await message.answer(
        "🧩 Нажмите кнопку ниже, чтобы открыть ваш профиль:",
        reply_markup=builder.as_markup()
    )


# ==========================
# 📘 Инструкции
# ==========================
@router.message(lambda msg: msg.text in ["📘 Инструкции", "📘 Instructions"])
async def show_instructions(message: types.Message):
    """Показывает краткую инструкцию"""
    text = (
        "📘 *Инструкции по работе с PAZL Collab*\n\n"
        "1️⃣ После модерации анкеты ваш профиль появляется в каталоге.\n"
        "2️⃣ Через Mini App можно редактировать данные и видеть свою карточку.\n"
        "3️⃣ Чтобы найти партнёров — используйте раздел каталога.\n\n"
        "❓ Если есть вопросы, обратитесь к модератору."
    )
    await message.answer(text, parse_mode="Markdown")
