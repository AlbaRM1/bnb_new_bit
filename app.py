import asyncio
import logging
from aiogram import Bot, Dispatcher

from config_reader import config
from handlers import bnb_spam, start, admin_panel
from database.models import async_main

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(token='7104204342:AAEHIhSmnx5hR9RQgwg834CsmFeLrXJnuvc')
chat_id = '-4164115662'

# Диспетчер
dp = Dispatcher()


async def main():
    await async_main()
    
    dp.include_router(start.router)
    dp.include_router(bnb_spam.router)
    dp.include_router(admin_panel.router)
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())