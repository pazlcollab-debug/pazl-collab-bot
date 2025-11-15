from aiogram import Router, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging
from config import BOT_TOKEN
import aiohttp
from services.partnership_storage import get_partnership_storage, PartnershipStatus

router = Router()
logger = logging.getLogger(__name__)


# ==========================================================
# 🤝 Обработка предложений партнерства
# ==========================================================
@router.callback_query(F.data.startswith("partnership_"))
async def handle_partnership_callback(callback: types.CallbackQuery):
    """Обрабатывает ответы на предложения партнерства"""
    
    data = callback.data
    parts = data.split("_")
    
    if len(parts) < 4:
        await callback.answer("❌ Ошибка обработки запроса", show_alert=True)
        return
    
    action = parts[1]  # accept или decline
    from_user_id = parts[2]
    to_user_id = parts[3]
    
    # Получаем информацию о пользователях
    try:
        from_user_info = await get_user_info(from_user_id)
        to_user_info = await get_user_info(to_user_id)
        
        if not from_user_info or not to_user_info:
            await callback.answer("❌ Пользователь не найден", show_alert=True)
            return
        
        # Находим предложение партнерства
        storage = get_partnership_storage()
        partnerships = storage.get_partnerships_by_user(from_user_id)
        partnership = None
        for p in partnerships:
            if (p["from_user_id"] == from_user_id and 
                p["to_user_id"] == to_user_id and 
                p["status"] == PartnershipStatus.PENDING.value):
                partnership = p
                break
        
        if not partnership:
            await callback.answer("❌ Предложение партнерства не найдено", show_alert=True)
            return
        
        if action == "accept":
            # Обновляем статус в хранилище
            storage.update_status(
                partnership["id"],
                PartnershipStatus.ACCEPTED,
                metadata={"accepted_at": callback.message.date.isoformat() if callback.message.date else None}
            )
            
            # Отправляем сообщение инициатору о согласии
            message_to_initiator = (
                f"✅ *Отличные новости!*\n\n"
                f"Пользователь *{to_user_info['name']}* согласился стать вашим партнером!\n\n"
                f"📋 *Контактная информация:*\n"
                f"• Telegram: @{to_user_info.get('telegram', '—')}\n"
                f"• Направление: {to_user_info.get('direction', '—')}\n"
                f"• Город: {to_user_info.get('city', '—')}\n\n"
                f"🎉 Теперь вы можете связаться и обсудить детали сотрудничества!"
            )
            
            await send_message(int(from_user_id), message_to_initiator)
            await callback.answer("✅ Вы согласились на партнерство!", show_alert=True)
            
            # Обновляем сообщение у получателя
            await callback.message.edit_text(
                f"✅ *Вы согласились на партнерство*\n\n"
                f"Пользователю *{from_user_info['name']}* отправлено уведомление о вашем согласии.",
                parse_mode="Markdown"
            )
            
            logger.info(f"Partnership accepted: {partnership['id']}")
            
        elif action == "decline":
            # Обновляем статус в хранилище
            storage.update_status(
                partnership["id"],
                PartnershipStatus.DECLINED,
                metadata={"declined_at": callback.message.date.isoformat() if callback.message.date else None}
            )
            
            # Отправляем сообщение инициатору об отказе
            message_to_initiator = (
                f"❌ *Уведомление*\n\n"
                f"К сожалению, пользователь *{to_user_info['name']}* отказался от партнерства.\n\n"
                f"Не расстраивайтесь! Вы можете найти других партнеров в галерее."
            )
            
            await send_message(int(from_user_id), message_to_initiator)
            await callback.answer("❌ Вы отказались от партнерства", show_alert=True)
            
            # Обновляем сообщение у получателя
            await callback.message.edit_text(
                f"❌ *Вы отказались от партнерства*\n\n"
                f"Пользователю *{from_user_info['name']}* отправлено уведомление об отказе.",
                parse_mode="Markdown"
            )
            
            logger.info(f"Partnership declined: {partnership['id']}")
        
    except Exception as e:
        logging.error(f"Ошибка при обработке партнерства: {e}")
        await callback.answer("❌ Произошла ошибка", show_alert=True)


async def get_user_info(telegram_id: str):
    """Получает информацию о пользователе из Airtable"""
    try:
        from api.airtable_service import get_approved_experts
        experts = get_approved_experts()
        for expert in experts:
            if expert.get("telegram_id") == str(telegram_id):
                return expert
        return None
    except Exception as e:
        logging.error(f"Ошибка получения информации о пользователе: {e}")
        return None


async def send_message(chat_id: int, text: str, parse_mode: str = "Markdown"):
    """Отправляет сообщение через Telegram Bot API"""
    try:
        bot_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        async with aiohttp.ClientSession() as session:
            async with session.post(
                bot_url,
                json={
                    "chat_id": chat_id,
                    "text": text,
                    "parse_mode": parse_mode
                }
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logging.error(f"Ошибка отправки сообщения: {error_text}")
    except Exception as e:
        logging.error(f"Ошибка при отправке сообщения: {e}")

