from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, **kwargs):
    user = kwargs.get("tg_user")
    name = message.from_user.first_name or "друг"

    await message.answer(
        f"👋 Привет, <b>{name}</b>!\n\n"
        f"Я <b>JobScout Bot</b> — твой персональный агент по поиску вакансий.\n\n"
        f"🔍 Я буду присылать тебе только релевантные вакансии на основе твоих фильтров.\n\n"
        f"<b>Команды:</b>\n"
        f"• /settings — настроить фильтры\n"
        f"• /status — посмотреть текущие фильтры\n"
        f"• /stop — остановить уведомления\n\n"
        f"Начни с /settings чтобы настроить поиск! 🚀"
    )
