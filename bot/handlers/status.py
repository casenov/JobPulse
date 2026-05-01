from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command("status"))
async def cmd_status(message: Message, **kwargs):
    tg_user = kwargs.get("tg_user")
    if not tg_user:
        await message.answer("❌ Пользователь не найден. Введи /start для регистрации.")
        return

    await message.answer(
        "📊 <b>Твой статус</b>\n\n"
        "Используй /settings чтобы обновить фильтры.\n"
        "Используй /stop чтобы остановить уведомления."
    )


@router.message(Command("stop"))
async def cmd_stop(message: Message):
    import httpx
    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                "http://localhost:8000/api/v1/users/telegram/notifications/toggle/",
                json={"telegram_id": message.from_user.id},
                timeout=5.0,
            )
        await message.answer(
            "🔕 <b>Уведомления отключены.</b>\n\n"
            "Введи /start или /settings чтобы включить снова."
        )
    except Exception:
        await message.answer("❌ Не удалось остановить уведомления. Попробуй позже.")
