import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from mcrcon import MCRcon

# --- КОНФИГУРАЦИЯ ---
API_TOKEN = '7973278862:AAHQcnNmjsQPbGVBkTguxylnM0npJX34hF4'  # Вставьте токен

# Данные от сервера
RCON_IP = '65.108.21.148'
RCON_PORT = 25981
RCON_PASS = 'ifthisx983405932874dfjkjdfvjnkvncxvbkjlndfgbuxz09v9cx' # Обязательно смените пароль на сервере и вставьте сюда новый!

# ID вашей группы
GROUP_ID = -1003537637837

# Настройка логов
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message()
async def check_sub_and_whitelist(message: types.Message):
    # Игнорируем сообщения от ботов
    if message.from_user.is_bot:
        return

    user_id = message.from_user.id
    nickname = message.text.strip()

    # 1. ПРОВЕРКА НАХОЖДЕНИЯ В ГРУППЕ
    try:
        chat_member = await bot.get_chat_member(chat_id=GROUP_ID, user_id=user_id)

        # Статусы: left (ушел/не вступал), kicked (забанен)
        # Если человека нет в чате — посылаем лесом
        if chat_member.status in ['left', 'kicked']:
            await message.answer(
                "⛔ <b>тебе нельзя тут быть</b>\n"
                "чтобы зайти на серв тебе надо купить проходку.",
                parse_mode="HTML"
            )
            return

    except Exception as e:
        # Если бот не админ или другая ошибка
        await message.answer(f"бота нету в группе бля код: {e}")
        return

    # 2. ВАЛИДАЦИЯ НИКНЕЙМА
    if len(nickname) < 3 or len(nickname) > 16 or not nickname.replace("_", "").isalnum():
        await message.answer("❌ Некорректный никнейм. Используй только английские буквы, цифры и '_'.")
        return

    # 3. ОТПРАВКА RCON КОМАНДЫ
    status_msg = await message.answer("подключение к серву...")

    try:
        with MCRcon(RCON_IP, RCON_PASS, port=RCON_PORT) as mcr:
            response = mcr.command(f"whitelist add {nickname}")

            if "Added" in response or "added" in response:
                await status_msg.edit_text(f"игроку <b>{nickname}</b> выдан доступ!", parse_mode="HTML")
            elif "already" in response:
                await status_msg.edit_text(f"игрок <b>{nickname}</b> уже в вайтлисте.", parse_mode="HTML")
            else:
                await status_msg.edit_text(f"ответ сервера: {response}")

    except Exception as e:
        await status_msg.edit_text(f"ошибка соединения.\nкод: {e}")

async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
