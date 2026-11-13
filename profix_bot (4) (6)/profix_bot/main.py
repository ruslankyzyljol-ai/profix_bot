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

from config import (
    BOT_TOKEN, ADMIN_ID, CHANNEL_USERNAME, CHANNEL_URL, MINES_DIR,
    LINKS, PROMOS, USER_LANG, save_data
)

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
        "choose_lang": "🌐 Тилди тандаңыз:",
        "subscribe": "📢 Ботту колдонуу үчүн каналга жазылыңыз:",
        "not_subscribed": "❌ Сиз каналга жазылган жоксуз. Жазылып, кайра басыңыз.",
        "subscribed_ok": "✅ Рахмат! Ботту колдоно аласыз.",
        "main_menu": "📌 Башкы меню:",
        "choose_game": "🎮 Кайсы оюнга прогноз алгыңыз келет?",
        "analyzing": "🔍 Анализ жүрүп жатат... 5 секунд күтө туруңуз...",
        "prognoz_warning": (
            "⚠️ <b>СУНУШ!</b>\n\n"
            "Прогноздор так иштеши үчүн жаңы аккаунт ачып,\n"
            "биздин ссылка жана промокод менен катталыңыз.\n\n"
            "Ссылка алуу үчүн <b>«🔗 Ботко улануу»</b> басыңыз."
        ),
        "choose_bonus": "🎁 Кайсы казинодон бонус алгыңыз келет?",
        "not_ready": "⏳ Бул казино азырынча кошула элек. Башкасын тандаңыз!",
        "support_text": "🆘 Колдоо кызматы 24/7 иштейт!\n\n👨‍💻 Админге жазыңыз: @nurriksal",
        "btn_prognoz": "🎰 Прогноздор",
        "btn_bonus": "🎁 Бонустар",
        "btn_support": "🆘 Колдоо 24/7",
        "btn_skip": "⚠️ Пропустить",
        "btn_get_link": "🔗 Ботко улануу",
        "btn_new_pred": "🔄 Жаңы прогноз",
        "btn_subscribe": "📢 Каналга өтүү",
        "btn_check": "✅ Текшерүү",
        "btn_back": "⬅️ Артка",
    },
    "ru": {
        "welcome": (
            "🤖 <b>Добро пожаловать в PROFIXKG!</b>\n\n"
            "Бот даёт прогнозы по играм казино:\n"
            "✈️ Lucky Jet | 💣 Mines | 🐔 Chicken Road\n\n"
            "Для использования подпишитесь на наш канал 👇"
        ),
        "choose_lang": "🌐 Выберите язык:",
        "subscribe": "📢 Подпишитесь на канал для использования бота:",
        "not_subscribed": "❌ Вы не подписаны на канал. Подпишитесь и нажмите снова.",
        "subscribed_ok": "✅ Спасибо! Теперь вы можете пользоваться ботом.",
        "main_menu": "📌 Главное меню:",
        "choose_game": "🎮 На какую игру хотите прогноз?",
        "analyzing": "🔍 Идёт анализ... Подождите 5 секунд...",
        "prognoz_warning": (
            "⚠️ <b>РЕКОМЕНДАЦИЯ!</b>\n\n"
            "Для точной работы прогнозов создайте новый аккаунт\n"
            "и зарегистрируйтесь по нашей ссылке с промокодом.\n\n"
            "Для получения ссылки нажмите <b>«🔗 Продолжить в боте»</b>."
        ),
        "choose_bonus": "🎁 Из какого казино хотите получить бонус?",
        "not_ready": "⏳ Это казино пока не добавлено. Выберите другое!",
        "support_text": "🆘 Поддержка работает 24/7!\n\n👨‍💻 Пишите админу: @nurriksal",
        "btn_prognoz": "🎰 Прогнозы",
        "btn_bonus": "🎁 Бонусы",
        "btn_support": "🆘 Поддержка 24/7",
        "btn_skip": "⚠️ Пропустить",
        "btn_get_link": "🔗 Продолжить в боте",
        "btn_new_pred": "🔄 Новый прогноз",
        "btn_subscribe": "📢 Перейти на канал",
        "btn_check": "✅ Проверить",
        "btn_back": "⬅️ Назад",
    }
}

# ==================== ЖАРДАМЧЫ ====================

user_lang = USER_LANG  # config.py менен бөлүшүлөт, файлга сакталат
user_last_game = {}


def t(uid, key):
    lang = user_lang.get(uid, "ky")
    return TEXTS[lang].get(key, "")


def main_keyboard(uid):
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton(text=t(uid, "btn_prognoz")), KeyboardButton(text=t(uid, "btn_bonus"))],
        [KeyboardButton(text=t(uid, "btn_support"))]
    ])


def games_keyboard(uid):
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton(text="✈️ Lucky Jet"), KeyboardButton(text="💣 Mines")],
        [KeyboardButton(text="🐔 Chicken Road")],
        [KeyboardButton(text=t(uid, "btn_back"))]
    ])


def bonus_keyboard(uid):
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton(text="🔴 1Win"), KeyboardButton(text="🟡 Mostbet")],
        [KeyboardButton(text="🔵 Melbet"), KeyboardButton(text="🟣 1xBet")],
        [KeyboardButton(text=t(uid, "btn_back"))]
    ])


def refresh_keyboard(uid, game):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(uid, "btn_new_pred"), callback_data=f"new_pred_{game}")]
    ])


async def is_subscribed(uid):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=uid)
        return member.status in [
            ChatMemberStatus.MEMBER,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.CREATOR
        ]
    except Exception as e:
        logging.error(f"is_subscribed error: {e}")
        return False


def find_images(folder):
    if os.path.isdir(folder):
        return [f for f in os.listdir(folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    return []


# ==================== FSM ====================

class AdminStates(StatesGroup):
    waiting_link_val = State()
    waiting_promo_val = State()
    waiting_channel_photo = State()
    waiting_channel_text = State()


# ==================== START ====================

@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇰🇬 Кыргызча", callback_data="lang_ky"),
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")
        ]
    ])
    await message.answer("🌐 Тилди тандаңыз / Выберите язык:", reply_markup=kb)


@dp.callback_query(lambda c: c.data.startswith("lang_"))
async def set_language(callback: CallbackQuery):
    uid = callback.from_user.id
    lang = callback.data.split("_")[1]
    user_lang[uid] = lang
    save_data()
    await callback.answer()
    try:
        await callback.message.delete()
    except Exception:
        pass

    if await is_subscribed(uid):
        await callback.message.answer(
            t(uid, "subscribed_ok") + "\n\n" + t(uid, "main_menu"),
            reply_markup=main_keyboard(uid)
        )
    else:
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
        await callback.answer()
        try:
            await callback.message.delete()
        except Exception:
            pass
        await callback.message.answer(
            t(uid, "subscribed_ok") + "\n\n" + t(uid, "main_menu"),
            reply_markup=main_keyboard(uid)
        )
    else:
        await callback.answer(t(uid, "not_subscribed"), show_alert=True)


# ==================== АРТКА ====================

@dp.message(lambda m: m.text in ["⬅️ Артка", "⬅️ Назад"])
async def back_to_main(message: Message, state: FSMContext):
    await state.clear()
    uid = message.from_user.id
    await message.answer(t(uid, "main_menu"), reply_markup=main_keyboard(uid))


# ==================== ПРОГНОЗДОР ====================

@dp.message(lambda m: m.text in ["🎰 Прогноздор", "🎰 Прогнозы"])
async def show_prognoz_warning(message: Message):
    uid = message.from_user.id
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=t(uid, "btn_skip"), callback_data="go_games"),
            InlineKeyboardButton(text=t(uid, "btn_get_link"), callback_data="go_bonus")
        ]
    ])
    await message.answer(t(uid, "prognoz_warning"), reply_markup=kb, parse_mode="HTML")


@dp.callback_query(lambda c: c.data == "go_games")
async def go_games(callback: CallbackQuery):
    uid = callback.from_user.id
    await callback.answer()
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.message.answer(t(uid, "choose_game"), reply_markup=games_keyboard(uid))


@dp.callback_query(lambda c: c.data == "go_bonus")
async def go_bonus_cb(callback: CallbackQuery):
    uid = callback.from_user.id
    await callback.answer()
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.message.answer(t(uid, "choose_bonus"), reply_markup=bonus_keyboard(uid))


async def send_prediction(message: Message, uid: int, pred_text: str, game: str, photo_path: str = None):
    user_last_game[uid] = game
    loading = await message.answer(t(uid, "analyzing"))
    await asyncio.sleep(5)
    try:
        await loading.delete()
    except Exception:
        pass
    kb = refresh_keyboard(uid, game)
    if photo_path and os.path.exists(photo_path):
        photo = FSInputFile(photo_path)
        await message.answer_photo(photo=photo, caption=pred_text, reply_markup=kb, parse_mode="HTML")
    else:
        await message.answer(pred_text, reply_markup=kb, parse_mode="HTML")


PRED_LUCKYJET = (
    "✈️ <b>LUCKY JET ПРОГНОЗУ</b>\n\n"
    "📊 Коэффицент: <b>1.85x</b>\n"
    "📈 Багыт: ЖОГОРУ ⬆️\n"
    "⏱️ Убакыт: 1-2 мүнөт\n\n"
    "⚠️ Жаңы акк + биздин ссылка + промокод!"
)
PRED_MINES = (
    "💣 <b>MINES ПРОГНОЗУ</b>\n\n"
    "🎯 Тактык: 92%\n"
    "⏱️ 5 секунд күт\n\n"
    "⚠️ Жаңы акк + биздин ссылка + промокод!"
)
PRED_CHICKEN = (
    "🐔 <b>CHICKEN ROAD ПРОГНОЗУ</b>\n\n"
    "📊 Коэффицент: <b>2.10x</b>\n"
    "📈 Багыт: ОҢ ➡️\n"
    "⏱️ Убакыт: 1 мүнөт\n\n"
    "⚠️ Жаңы акк + биздин ссылка + промокод!"
)


def mines_photo():
    folder = "images/mines"
    images = find_images(folder)
    return os.path.join(folder, random.choice(images)) if images else None


@dp.message(F.text == "✈️ Lucky Jet")
async def lucky_jet(message: Message):
    await send_prediction(message, message.from_user.id, PRED_LUCKYJET, "luckyjet")


@dp.message(F.text == "💣 Mines")
async def mines(message: Message):
    await send_prediction(message, message.from_user.id, PRED_MINES, "mines", mines_photo())


@dp.message(F.text == "🐔 Chicken Road")
async def chicken_road(message: Message):
    await send_prediction(message, message.from_user.id, PRED_CHICKEN, "chickenroad")


@dp.callback_query(lambda c: c.data.startswith("new_pred_"))
async def new_prediction(callback: CallbackQuery):
    uid = callback.from_user.id
    game = callback.data.split("new_pred_")[1]
    await callback.answer()
    try:
        await callback.message.delete()
    except Exception:
        pass

    if game == "luckyjet":
        await send_prediction(callback.message, uid, PRED_LUCKYJET, "luckyjet")
    elif game == "mines":
        await send_prediction(callback.message, uid, PRED_MINES, "mines", mines_photo())
    elif game == "chickenroad":
        await send_prediction(callback.message, uid, PRED_CHICKEN, "chickenroad")


# ==================== БОНУСТАР ====================

@dp.message(lambda m: m.text in ["🎁 Бонустар", "🎁 Бонусы"])
async def show_bonus(message: Message):
    uid = message.from_user.id
    await message.answer(t(uid, "choose_bonus"), reply_markup=bonus_keyboard(uid))


async def send_bonus(message: Message, emoji_name: str, key: str, promo_image: str):
    link = LINKS.get(key, "")
    promo = PROMOS.get(key, "")
    text = (
        f"{emoji_name}\n\n"
        f"🔗 Ссылка аркылуу катталыңыз:\n{link}\n\n"
        f"📝 Промокод: <b>{promo}</b>\n\n"
        "📌 Промокодду кайда жазуу керек — жогорудагы сүрөттө!\n\n"
        "⚠️ ТЕК ЖАҢЫ АККАУНТКА!"
    )
    # promo_image: бир файл (images/1win_promo.jpg) же папка болушу мүмкүн
    paths = []
    if os.path.isfile(promo_image):
        paths = [promo_image]
    elif os.path.isdir(promo_image):
        paths = [os.path.join(promo_image, f) for f in find_images(promo_image)]

    if paths:
        for i, path in enumerate(paths):
            if i == len(paths) - 1:
                await message.answer_photo(FSInputFile(path), caption=text, parse_mode="HTML")
            else:
                await message.answer_photo(FSInputFile(path))
    else:
        await message.answer(text, parse_mode="HTML")


@dp.message(F.text == "🔴 1Win")
async def bonus_1win(message: Message):
    await send_bonus(message, "🔴 <b>1Win</b>", "1win", "images/1win_promo.jpg")


@dp.message(F.text == "🟡 Mostbet")
async def bonus_mostbet(message: Message):
    await send_bonus(message, "🟡 <b>Mostbet</b>", "mostbet", "images/mostbet_promo.jpg")


@dp.message(F.text.in_(["🔵 Melbet", "🟣 1xBet"]))
async def bonus_not_ready(message: Message):
    uid = message.from_user.id
    await message.answer(t(uid, "not_ready"), reply_markup=bonus_keyboard(uid))


# ==================== КОЛДОО ====================

@dp.message(lambda m: m.text in ["🆘 Колдоо 24/7", "🆘 Поддержка 24/7"])
async def support(message: Message):
    uid = message.from_user.id
    await message.answer(t(uid, "support_text"), reply_markup=main_keyboard(uid))


# ==================== АДМИН ====================

def admin_keyboard():
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton(text="🔗 1Win ссылка"), KeyboardButton(text="🔗 Mostbet ссылка")],
        [KeyboardButton(text="📝 1Win промокод"), KeyboardButton(text="📝 Mostbet промокод")],
        [KeyboardButton(text="📸 Каналга жөнөтүү")],
        [KeyboardButton(text="⬅️ Артка")]
    ])


@dp.message(Command("admin"))
async def admin_panel(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Сиз админ эмессиз!")
        return
    await state.clear()
    await message.answer("⚙️ Админ панель:", reply_markup=admin_keyboard())


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
    LINKS[data["key"]] = (message.text or "").strip()
    save_data()
    await message.answer("✅ Ссылка жаңыртылды!", reply_markup=admin_keyboard())
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
    PROMOS[data["key"]] = (message.text or "").strip()
    save_data()
    await message.answer("✅ Промокод жаңыртылды!", reply_markup=admin_keyboard())
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
            caption=(message.text or "").strip()
        )
        await message.answer("✅ Каналга жиберилди!", reply_markup=admin_keyboard())
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
    os.makedirs(MINES_DIR, exist_ok=True)
    os.makedirs("images/mines", exist_ok=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
