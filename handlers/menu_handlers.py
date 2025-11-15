from aiogram import Router, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from config import WEBAPP_URL

router = Router()

# ==========================================================
# ⚙️ Мой профиль (RU/EN)
# ==========================================================
@router.message(lambda msg: msg.text in ["⚙️ Мой профиль", "⚙️ My profile"])
async def open_profile(message: types.Message, state: FSMContext):
    """Открывает Mini App с профилем пользователя"""

    data = await state.get_data()
    lang = data.get("lang", "ru")
    telegram_id = message.from_user.id

    webapp_url = f"{WEBAPP_URL}/webapp/profile/{telegram_id}"

    if lang == "ru":
        text = "🧩 Нажмите кнопку ниже, чтобы открыть ваш профиль:"
        btn_text = "🌐 Открыть мой профиль"
    else:
        text = "🧩 Click the button below to open your profile:"
        btn_text = "🌐 Open my profile"

    builder = InlineKeyboardBuilder()
    builder.button(
        text=btn_text,
        web_app=types.WebAppInfo(url=webapp_url)
    )

    await message.answer(text, reply_markup=builder.as_markup())


# ==========================================================
# 🔍 Найти партнёра для эфира (RU/EN)
# ==========================================================
@router.message(lambda msg: msg.text in [
    "🔍 Найти партнёра для эфира",
    "🔍 Find a partner for stream"
])
async def open_partner_gallery(message: types.Message, state: FSMContext):
    """Открывает Mini App галерею профилей (каталог экспертов)"""

    data = await state.get_data()
    lang = data.get("lang", "ru")

    if lang == "ru":
        text = "🔍 Нажмите кнопку ниже, чтобы открыть галерею партнёров:"
        btn_text = "🌐 Открыть галерею"
    else:
        text = "🔍 Click the button below to open the partners gallery:"
        btn_text = "🌐 Open gallery"

    webapp_url = f"{WEBAPP_URL}/webapp/gallery"

    builder = InlineKeyboardBuilder()
    builder.button(
        text=btn_text,
        web_app=types.WebAppInfo(url=webapp_url)
    )

    await message.answer(text, reply_markup=builder.as_markup())


# ==========================================================
# 🎙 Найти партнёра для подкаста (RU/EN)
# ==========================================================
@router.message(lambda msg: msg.text in [
    "🎙 Найти партнёра для подкаста",
    "🎙 Find a partner for podcast"
])
async def open_podcast_gallery(message: types.Message, state: FSMContext):
    """Открывает Mini App галерею для подкаста"""

    data = await state.get_data()
    lang = data.get("lang", "ru")

    if lang == "ru":
        text = "🎙 Нажмите кнопку ниже, чтобы открыть каталог партнёров для подкаста:"
        btn_text = "🌐 Открыть каталог"
    else:
        text = "🎙 Click the button below to open the podcast partners catalog:"
        btn_text = "🌐 Open catalog"

    webapp_url = f"{WEBAPP_URL}/webapp/gallery"

    builder = InlineKeyboardBuilder()
    builder.button(
        text=btn_text,
        web_app=types.WebAppInfo(url=webapp_url)
    )

    await message.answer(text, reply_markup=builder.as_markup())


# ==========================================================
# 📘 Инструкции (RU/EN)
# ==========================================================
@router.message(lambda msg: msg.text in ["📘 Инструкции", "📘 Instructions"])
async def show_instructions(message: types.Message, state: FSMContext):
    """Показывает инструкцию"""

    data = await state.get_data()
    lang = data.get("lang", "ru")

    if lang == "ru":
        text = (
            "📘 *Инструкции по работе с PAZL Collab*\n\n"
            "1️⃣ После модерации анкеты ваш профиль появляется в каталоге.\n"
            "2️⃣ В Mini App можно предлагать пользователям партнёрство.\n"
            "3️⃣ Чтобы найти партнёров — используйте кнопки ниже «Найти партнёра ...».\n\n"
            "❓ Если есть вопросы — обращайтесь к модератору."
        )
    else:
        text = (
            "📘 *Instructions for PAZL Collab*\n\n"
            "1️⃣ After moderation your profile appears in the catalog.\n"
            "2️⃣ In the Mini App you can propose partnerships to other users.\n"
            "3️⃣ To find partners — use the “Find partner …” buttons below.\n\n"
            "❓ If you have questions — contact the moderator."
        )

    await message.answer(text, parse_mode="Markdown")
