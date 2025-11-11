import asyncio
from aiogram import Bot

BOT_TOKEN = "7983940637:AAFjRhnzNxpftBDuV5howbnRoKNk4jlKG_s"
CHANNEL_LINK = "@PAZL_Collab_Moderation"

async def main():
    bot = Bot(token=BOT_TOKEN)
    chat = await bot.get_chat(CHANNEL_LINK)
    print(f"🔹 Chat title: {chat.title}")
    print(f"🔹 Chat ID: {chat.id}")

if __name__ == "__main__":
    asyncio.run(main())
