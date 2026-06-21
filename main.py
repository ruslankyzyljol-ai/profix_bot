import asyncio
import random
import os
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, StateFilter
from aiogram.types import (
    Message, CallbackQuery, FSInputFile,
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ChatMemberStatus

from config import BOT_TOKEN, ADMIN_ID, CHANNEL_USERNAME, CHANNEL_URL, MINES_DIR, LINKS, PROMOS

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# ==================== ТЕКСТТЕР ====================

TEXTS = {
    "ky": {
        "welcome": (
            "🤖 <b>PROFIXKG Прогноз Ботуна Кош Келиңиз!</b>\n\n"
            "Бул бот сизге казино оюндары боюнча прогноздорду берет:\n"
            "✈️ Lucky Jet | 💣 Mines | 🐔 Chicken Road\n\n"
            "Ботту колдонуу үчүн биздин каналга жазылыңыз 👇"
        ),
        "choose_lang": "🌐 Тилди тандаңыз / Выберите язык:",
        "subscribe": "📢 Ботту колдонуу үчүн каналга жазылыңыз:",
        "not_subscribed": "❌ Сиз дагы эле каналга жазылган жоксуз. Жазылып, кайра басыңыз.",
        "subscribed_ok": "✅ Рахмат! Ботту колдоно аласыз.",
        "main_menu": "📌 Башкы меню:",
        "choose_game": "🎮 Кайсы оюнга прогноз алгыңыз келет?",
        "analyzing": "🔍 Анализ жүрүп жатат... 10 секунд күтө туруңуз...",
        "prognoz_warning": (
            "⚠️ <b>МААНИЛҮҮ!</b>\n\n"
            "Прогноздор туура иштеши үчүн:\n"
            "✅ Жаңы аккаунт ачыңыз\n"
            "✅ Биздин ссылка аркылуу катталыңыз\n"
            "✅ Промокод жазыңыз\n\n"
            "Ссылка жана промокод алуу үчүн 👉 <b>Бонустар</b> бөлүмүнө өтүңүз."
        ),
        "choose_bonus": "🎁 Кайсы казинодон бонус алгыңыз келет?",
        "not_ready": "⏳ Бул казино азырынча кошула элек. Башкасын тандаңыз!",
        "support_text": "🆘 Колдоо кызматы 24/7 иштейт!\n\n👨‍💻 Админге жазыңыз: @nurriksal",
        "back": "⬅️ Артка",
        "btn_prognoz": "🎰 Прогноздор",
        "btn_bonus": "🎁 Бонустар",
        "btn_support": "🆘 Колдоо 24/7",
        "btn_continue": "▶️ Улануу",
        "btn_get_link": "🎁 Ссылка алуу",
        "btn_new_pred": "🔄 Жаңы прогноз",
        "btn_subscribe": "📢 Каналга өтүү",
        "btn_check": "✅ Текшерүү",
    },
    "ru": {
        "welcome": (
            "🤖 <b>Добро пожаловать в PROFIXKG Прогноз Бот!</b>\n\n"
            "Этот бот даёт прогнозы по казино играм:\n"
            "✈️ Lucky Jet | 💣 Mines | 🐔 Chicken Road\n\n"
            "Для использования бота подпишитесь на наш канал 👇"
        ),
        "choose_lang": "🌐 Тилди тандаңыз / Выберите язык:",
        "subscribe": "📢 Для использования бота подпишитесь на канал:",
        "not_subscribed": "❌ Вы ещё не подписались на канал. Подпишитесь и нажмите снова.",
        "subscribed_ok": "✅ Спасибо! Теперь вы можете пользоваться ботом.",
        "main_menu": "📌 Главное меню:",
        "choose_game": "🎮 На какую игру хотите прогноз?",
        "analyzing": "🔍 Идёт анализ... Подождите 10 секунд...",
        "prognoz_warning": (
            "⚠️ <b>ВАЖНО!</b>\n\n"
            "Для точной работы прогнозов:\n"
            "✅ Создайте новый аккаунт\n"
            "✅ Зарегистрируйтесь по нашей ссылке\n"
            "✅ Введите промокод\n\n"
            "Ссылку и промокод получите в разделе 👉 <b>Бонусы</b>."
        ),
        "choose_bonus": "🎁 Из какого казино хотите получить бонус?",
        "not_ready": "⏳ Это казино пока не добавлено. Выберите другое!",
        "support_text": "🆘 Служба поддержки работает 24/7!\n\n👨‍💻 Пишите админу: @nurriksal",
        "back": "⬅️ Назад",
        "btn_prognoz": "🎰 Прогнозы",
        "btn_bonus": "🎁 Бонусы",
        "btn_support": "🆘 Поддержка 24/7",
        "btn_continue": "▶️ Продолжить",
        "btn_get_link": "🎁 Получить ссылку",
        "btn_new_pred": "🔄 Новый прогноз",
        "btn_subscribe": "📢 Перейти на канал",
        "btn_check": "✅ Проверить",
    }
}

# ==================== ЖАРДАМЧЫ ====================

user_lang = {}

def t(user_id, key):
    lang = user_lang.get(user_id, "ky")
    return TEXTS[lang].get(key, "")

def main_keyboard(user_id):
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton(text=t(user_id, "btn_prognoz")), KeyboardButton(text=t(user_id, "btn_bonus"))],
        [KeyboardButton(text=t(user_id, "btn_support"))]
    ])

def games_keyboard(user_id):
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton(text="✈️ Lucky Jet"), KeyboardButton(text="💣 Mines")],
        [KeyboardButton(text="🐔 Chicken Road")],
        [KeyboardButton(text=t(user_id, "back"))]
    ])

def bonus_keyboard(user_id):
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton(text="🔴 1Win"), KeyboardButton(text="🟡 Mostbet")],
        [KeyboardButton(text="🔵 Melbet"), KeyboardButton(text="🟣 1xBet")],
        [KeyboardButton(text=t(user_id, "back"))]
    ])

def refresh_keyboard(user_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(user_id, "btn_new_pred"), callback_data="new_prediction")]
    ])

async def is_subscribed(user_id):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in [
            ChatMemberStatus.MEMBER,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.CREATOR
        ]
    except:
        return False

# ==================== FSM ====================

class AdminStates(StatesGroup):
    waiting_link_key = State()
    waiting_link_val = State()
    waiting_promo_key = State()
    waiting_promo_val = State()
    waiting_channel_photo = State()
    waiting_channel_text = State()

# ==================== ХЕНДЛЕРЛЕР ====================

@dp.message(Command("start"))
async def cmd_start(message: Message):
    uid = message.from_user.id
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇰🇬 Кыргызча", callback_data="lang_ky"),
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")
        ]
    ])
    await message.answer(
        "🌐 Тилди тандаңыз / Выберите язык:",
        reply_markup=kb
    )

@dp.callback_query(lambda c: c.data.startswith("lang_"))
async def set_language(callback: CallbackQuery):
    uid = callback.from_user.id
    lang = callback.data.split("_")[1]
    user_lang[uid] = lang
    await callback.message.delete()

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(uid, "btn_subscribe"), url=CHANNEL_URL)],
        [InlineKeyboardButton(text=t(uid, "btn_check"), callback_data="check_sub")]
    ])
    await callback.message.answer(
        t(uid, "welcome") + "\n\n" + t(uid, "subscribe"),
        reply_markup=kb,
        parse_mode="HTML"
    )

@dp.callback_query(lambda c: c.data == "check_sub")
async def check_sub(callback: CallbackQuery):
    uid = callback.from_user.id
    if await is_subscribed(uid):
        await callback.message.delete()
        await callback.message.answer(
            t(uid, "subscribed_ok") + "\n\n" + t(uid, "main_menu"),
            reply_markup=main_keyboard(uid)
        )
    else:
        await callback.answer(t(uid, "not_subscribed"), show_alert=True)

# ==================== БАШКЫ МЕНЮ ====================

@dp.message(lambda m: m.text in ["⬅️ Артка", "⬅️ Назад"])
async def back_to_main(message: Message, state: FSMContext):
    await state.clear()
    uid = message.from_user.id
    await message.answer(t(uid, "main_menu"), reply_markup=main_keyboard(uid))

# ==================== ПРОГНОЗДОР ====================

@dp.message(lambda m: m.text in ["🎰 Прогноздор", "🎰 Прогнозы"])
async def show_games(message: Message):
    uid = message.from_user.id
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=t(uid, "btn_continue"), callback_data="go_games"),
            InlineKeyboardButton(text=t(uid, "btn_get_link"), callback_data="go_bonus")
        ]
    ])
    await message.answer(t(uid, "prognoz_warning"), reply_markup=kb, parse_mode="HTML")

@dp.callback_query(lambda c: c.data == "go_games")
async def go_games(callback: CallbackQuery):
    uid = callback.from_user.id
    await callback.message.delete()
    await callback.message.answer(t(uid, "choose_game"), reply_markup=games_keyboard(uid))

@dp.callback_query(lambda c: c.data == "go_bonus")
async def go_bonus_from_prognoz(callback: CallbackQuery):
    uid = callback.from_user.id
    await callback.message.delete()
    await callback.message.answer(t(uid, "choose_bonus"), reply_markup=bonus_keyboard(uid))

async def send_prediction(message: Message, pred_text: str, photo_path: str = None):
    uid = message.from_user.id
    loading = await message.answer(t(uid, "analyzing"))
    await asyncio.sleep(10)
    await loading.delete()
    if photo_path and os.path.exists(photo_path):
        photo = FSInputFile(photo_path)
        await message.answer_photo(photo=photo, caption=pred_text, reply_markup=refresh_keyboard(uid), parse_mode="HTML")
    else:
        await message.answer(pred_text, reply_markup=refresh_keyboard(uid), parse_mode="HTML")

@dp.message(F.text == "✈️ Lucky Jet")
async def lucky_jet(message: Message):
    pred = (
        "✈️ <b>LUCKY JET ПРОГНОЗУ</b>\n\n"
        "📊 Коэффицент: <b>1.85x</b>\n"
        "📈 Багыт: ЖОГОРУ ⬆️\n"
        "⏱️ Убакыт: 1-2 мүнөт\n\n"
        "⚠️ Жаңы акк + биздин ссылка + промокод менен катталыңыз!"
    )
    await send_prediction(message, pred)

@dp.message(F.text == "💣 Mines")
async def mines(message: Message):
    images = []
    if os.path.exists(MINES_DIR):
        images = [f for f in os.listdir(MINES_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    pred = (
        "💣 <b>MINES ПРОГНОЗУ</b>\n\n"
        "🎯 Тактык: 92%\n"
        "⏱️ 1 мүнөт иштейт\n\n"
        "⚠️ Жаңы акк + биздин ссылка + промокод менен катталыңыз!"
    )
    photo_path = os.path.join(MINES_DIR, random.choice(images)) if images else None
    await send_prediction(message, pred, photo_path)

@dp.message(F.text == "🐔 Chicken Road")
async def chicken_road(message: Message):
    pred = (
        "🐔 <b>CHICKEN ROAD ПРОГНОЗУ</b>\n\n"
        "📊 Коэффицент: <b>2.10x</b>\n"
        "📈 Багыт: ОҢ ➡️\n"
        "⏱️ Убакыт: 1 мүнөт\n\n"
        "⚠️ Жаңы акк + биздин ссылка + промокод менен катталыңыз!"
    )
    await send_prediction(message, pred)

@dp.callback_query(lambda c: c.data == "new_prediction")
async def new_prediction(callback: CallbackQuery):
    uid = callback.from_user.id
    await callback.answer()
    await callback.message.delete()
    await callback.message.answer(t(uid, "choose_game"), reply_markup=games_keyboard(uid))

# ==================== БОНУСТАР ====================

@dp.message(lambda m: m.text in ["🎁 Бонустар", "🎁 Бонусы"])
async def show_bonus(message: Message):
    uid = message.from_user.id
    await message.answer(t(uid, "choose_bonus"), reply_markup=bonus_keyboard(uid))

@dp.message(F.text == "🔴 1Win")
async def bonus_1win(message: Message):
    link = LINKS.get("1win", "")
    promo = PROMOS.get("1win", "")
    text = (
        "🔴 <b>1Win</b>\n\n"
        f"🔗 Ссылка аркылуу катталыңыз:\n{link}\n\n"
        f"📝 Промокод: <b>{promo}</b>\n\n"
        "📌 Промокодду кайда жазуу керек:\n"
        "Катталуу формасын ачып → <b>«Добавить промокод»</b> баскычын басып → "
        f"<b>{promo}</b> деп жазыңыз → Зарегистрироваться\n\n"
        "⚠️ ТЕК ЖАҢЫ АККАУНТКА!"
    )
    photo_path = "images/1win_promo.jpg"
    if os.path.exists(photo_path):
        await message.answer_photo(FSInputFile(photo_path), caption=text, parse_mode="HTML")
    else:
        await message.answer(text, parse_mode="HTML")

@dp.message(F.text == "🟡 Mostbet")
async def bonus_mostbet(message: Message):
    link = LINKS.get("mostbet", "")
    promo = PROMOS.get("mostbet", "")
    text = (
        "🟡 <b>Mostbet</b>\n\n"
        f"🔗 Ссылка аркылуу катталыңыз:\n{link}\n\n"
        f"📝 Промокод: <b>{promo}</b>\n\n"
        "📌 Промокодду кайда жазуу керек:\n"
        "Катталуу формасын ачып → <b>«Промокод, если есть»</b> талаасына → "
        f"<b>{promo}</b> деп жазыңыз → Начать игру\n\n"
        "⚠️ ТЕК ЖАҢЫ АККАУНТКА!"
    )
    photo_path = "images/mostbet_promo.jpg"
    if os.path.exists(photo_path):
        await message.answer_photo(FSInputFile(photo_path), caption=text, parse_mode="HTML")
    else:
        await message.answer(text, parse_mode="HTML")

@dp.message(F.text.in_(["🔵 Melbet", "🟣 1xBet"]))
async def bonus_not_ready(message: Message):
    uid = message.from_user.id
    await message.answer(t(uid, "not_ready"), reply_markup=bonus_keyboard(uid))

# ==================== КОЛДОО ====================

@dp.message(lambda m: m.text in ["🆘 Колдоо 24/7", "🆘 Поддержка 24/7"])
async def support(message: Message):
    uid = message.from_user.id
    await message.answer(t(uid, "support_text"))

# ==================== АДМИН ====================

@dp.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Сиз админ эмессиз!")
        return
    kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton(text="🔗 1Win ссылка"), KeyboardButton(text="🔗 Mostbet ссылка")],
        [KeyboardButton(text="📝 1Win промокод"), KeyboardButton(text="📝 Mostbet промокод")],
        [KeyboardButton(text="📸 Каналга жөнөтүү")],
        [KeyboardButton(text="⬅️ Артка")]
    ])
    await message.answer("⚙️ Админ панель:", reply_markup=kb)

@dp.message(lambda m: m.text in ["🔗 1Win ссылка", "🔗 Mostbet ссылка"] and m.from_user.id == ADMIN_ID)
async def admin_change_link(message: Message, state: FSMContext):
    key = "1win" if "1Win" in message.text else "mostbet"
    await state.update_data(key=key)
    await state.set_state(AdminStates.waiting_link_val)
    await message.answer(f"✏️ {key} үчүн жаңы ссылканы жазыңыз:")

@dp.message(StateFilter(AdminStates.waiting_link_val))
async def save_link(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    data = await state.get_data()
    LINKS[data["key"]] = message.text.strip()
    await message.answer(f"✅ Ссылка жаңыртылды!")
    await state.clear()

@dp.message(lambda m: m.text in ["📝 1Win промокод", "📝 Mostbet промокод"] and m.from_user.id == ADMIN_ID)
async def admin_change_promo(message: Message, state: FSMContext):
    key = "1win" if "1Win" in message.text else "mostbet"
    await state.update_data(key=key)
    await state.set_state(AdminStates.waiting_promo_val)
    await message.answer(f"✏️ {key} үчүн жаңы промокодду жазыңыз:")

@dp.message(StateFilter(AdminStates.waiting_promo_val))
async def save_promo(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    data = await state.get_data()
    PROMOS[data["key"]] = message.text.strip()
    await message.answer(f"✅ Промокод жаңыртылды!")
    await state.clear()

@dp.message(lambda m: m.text == "📸 Каналга жөнөтүү" and m.from_user.id == ADMIN_ID)
async def admin_send_photo_start(message: Message, state: FSMContext):
    await state.set_state(AdminStates.waiting_channel_photo)
    await message.answer("📸 Каналга жиберчү сүрөттү жөнөтүңүз:")

@dp.message(StateFilter(AdminStates.waiting_channel_photo))
async def admin_get_photo(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    if not message.photo and not message.document:
        await message.answer("❌ Сүрөт жөнөтүңүз!")
        return
    file_id = message.photo[-1].file_id if message.photo else message.document.file_id
    await state.update_data(file_id=file_id)
    await state.set_state(AdminStates.waiting_channel_text)
    await message.answer("✏️ Эми текстти жазыңыз:")

@dp.message(StateFilter(AdminStates.waiting_channel_text))
async def admin_send_to_channel(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    data = await state.get_data()
    try:
        await bot.send_photo(
            chat_id=CHANNEL_USERNAME,
            photo=data["file_id"],
            caption=message.text.strip()
        )
        await message.answer("✅ Каналга жиберилди!")
    except Exception as e:
        await message.answer(f"❌ Ката: {e}")
    await state.clear()

# ==================== FALLBACK ====================

@dp.message()
async def fallback(message: Message):
    uid = message.from_user.id
    await message.answer(t(uid, "main_menu"), reply_markup=main_keyboard(uid))

# ==================== ИШКЕ КОШУУ ====================

async def main():
    if not os.path.exists(MINES_DIR):
        os.makedirs(MINES_DIR)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
