"""
Filters handler — FSM-based dialog for setting up vacancy filters.
"""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

router = Router()


class FilterSetup(StatesGroup):
    waiting_for_keywords = State()
    waiting_for_location = State()
    waiting_for_level = State()
    waiting_for_salary = State()


@router.message(Command("settings"))
async def cmd_settings(message: Message, state: FSMContext):
    await state.set_state(FilterSetup.waiting_for_keywords)
    await message.answer(
        "⚙️ <b>Настройка фильтров</b>\n\n"
        "Шаг 1/4: Введи ключевые слова через запятую.\n"
        "Например: <code>python, django, backend</code>"
    )


@router.message(FilterSetup.waiting_for_keywords)
async def process_keywords(message: Message, state: FSMContext):
    keywords = [kw.strip().lower() for kw in message.text.split(",") if kw.strip()]
    await state.update_data(keywords=keywords)
    await state.set_state(FilterSetup.waiting_for_location)
    await message.answer(
        f"✅ Ключевые слова: <b>{', '.join(keywords)}</b>\n\n"
        "Шаг 2/4: Введи желаемые города через запятую.\n"
        "Например: <code>Москва, Алматы, Remote</code>\n"
        "Или напиши <code>любой</code> чтобы не ограничивать."
    )


@router.message(FilterSetup.waiting_for_location)
async def process_location(message: Message, state: FSMContext):
    text = message.text.strip()
    locations = [] if text.lower() == "любой" else [
        loc.strip() for loc in text.split(",") if loc.strip()
    ]
    await state.update_data(locations=locations)
    await state.set_state(FilterSetup.waiting_for_level)
    await message.answer(
        "Шаг 3/4: Выбери уровень опыта:\n"
        "<code>intern</code> / <code>junior</code> / <code>middle</code> / "
        "<code>senior</code> / <code>any</code>"
    )


@router.message(FilterSetup.waiting_for_level)
async def process_level(message: Message, state: FSMContext):
    level_map = {
        "intern": "intern", "junior": "junior",
        "middle": "middle", "senior": "senior", "any": None,
    }
    level = level_map.get(message.text.strip().lower())
    await state.update_data(experience_level=level)
    await state.set_state(FilterSetup.waiting_for_salary)
    await message.answer(
        "Шаг 4/4: Минимальная зарплата (в рублях).\n"
        "Например: <code>100000</code>\n"
        "Или <code>0</code> чтобы не ограничивать."
    )


@router.message(FilterSetup.waiting_for_salary)
async def process_salary(message: Message, state: FSMContext):
    try:
        salary_min = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Введи число. Например: <code>100000</code>")
        return

    data = await state.get_data()
    data["salary_min"] = salary_min if salary_min > 0 else None

    # Save filter via API
    saved = await _save_filter(message.from_user.id, data)

    await state.clear()
    if saved:
        await message.answer(
            "✅ <b>Фильтр сохранён!</b>\n\n"
            f"🔑 Ключевые слова: <b>{', '.join(data.get('keywords', []))}</b>\n"
            f"📍 Локации: <b>{', '.join(data.get('locations', [])) or 'любые'}</b>\n"
            f"📊 Уровень: <b>{data.get('experience_level') or 'любой'}</b>\n"
            f"💰 Мин. зарплата: <b>{data.get('salary_min') or 'не указана'}</b>\n\n"
            "Я начну присылать подходящие вакансии! 🎯"
        )
    else:
        await message.answer("❌ Ошибка при сохранении фильтра. Попробуй ещё раз.")


async def _save_filter(telegram_id: int, data: dict) -> bool:
    """Save user filter via internal API."""
    import httpx
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "http://localhost:8000/api/v1/filters/",
                json={
                    "name": "Telegram Filter",
                    "keywords": data.get("keywords", []),
                    "locations": data.get("locations", []),
                    "experience_level": data.get("experience_level"),
                    "salary_min": data.get("salary_min"),
                    "is_active": True,
                    "notify_on_match": True,
                },
                headers={"X-Telegram-Id": str(telegram_id)},
                timeout=5.0,
            )
            return resp.status_code in (200, 201)
    except Exception:
        return False
