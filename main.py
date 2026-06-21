import asyncio
import random
import os
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ChatMemberStatus

from config import BOT_TOKEN, ADMIN_ID, CHANNEL_USERNAME, CHANNEL_URL, MINES_DIR
import database as db

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

def main_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton(text="🎰 Прогноздор"), KeyboardButton(text="🎁 Бонустар")],
        [KeyboardButton(text="🆘 Колдоо 24/7")]
    ])
    return kb

def games_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton(text="✈️ Lucky Jet"), KeyboardButton(text="💣 Mines")],
        [KeyboardButton(text="🐔 Chicken Road"), KeyboardButton(text="🎲 Башка оюндар")],
        [KeyboardButton(text="⬅️ Артка")]
    ])
    return kb

def bonuses_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton(text="🔴 1Win"), KeyboardButton(text="🟡 Mostbet")],
        [KeyboardButton(text="🔵 Melbet"), KeyboardButton(text="🟣 1xBet")],
        [KeyboardButton(text="⬅️ Артка")]
    ])
    return kb

def support_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton(text="❓ Прогноздор канчалык так?")],
        [KeyboardButton(text="📩 Админге жазуу")],
        [KeyboardButton(text="⬅️ Артка")]
    ])
    return kb

def admin_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton(text="📎 1Win шилтеме"), KeyboardButton(text="📎 Mostbet шилтеме")],
        [KeyboardButton(text="📎 Melbet шилтеме"), KeyboardButton(text="📎 1xBet шилтеме")],
        [KeyboardButton(text="📝 Промокод өзгөртүү"), KeyboardButton(text="📸 Каналга сүрөт жөнөтүү")],
        [KeyboardButton(text="⬅️ Артка")]
    ])
    return kb

def refresh_keyboard():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Жаңы прогноз", callback_data="new_prediction")]
    ])
    return kb

async def is_subscribed(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]
    except:
        return False

class AdminStates(StatesGroup):
    waiting_for_link = State()
    waiting_for_promocode = State()
    waiting_for_channel_photo = State()
    waiting_for_channel_text = State()

@dp.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    if await is_subscribed(user_id):
        await message.answer(
            f"👋 Салам, {message.from_user.first_name}!\n"
            "PROFIXKG прогноз ботуна кош келиңиз!\n\n"
            "Төмөнкү бөлүмдөрдүн бирин тандаңыз:",
            reply_markup=main_keyboard()
        )
    else:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📢 Каналга өтүү", url=CHANNEL_URL)],
            [InlineKeyboardButton(text="✅ Текшерүү", callback_data="check_sub")]
        ])
        await message.answer(
            f"🔔 Ботту колдонуу үчүн биздин каналга жазылыңыз:\n{CHANNEL_URL}\n\n"
            "Андан кийин «Текшерүү» баскычын басыңыз.",
            reply_markup=kb
        )

@dp.callback_query(lambda c: c.data == "check_sub")
async def check_subscription(callback: CallbackQuery):
    if await is_subscribed(callback.from_user.id):
        await callback.message.delete()
        await callback.message.answer("✅ Рахмат! Эми сиз ботту толук колдоно аласыз.", reply_markup=main_keyboard())
    else:
        await callback.answer("❌ Сиз дагы эле каналга жазылган жоксуз.", show_alert=True)

@dp.message(F.text == "⬅️ Артка")
async def back_to_main(message: Message):
    await message.answer("Башкы меню:", reply_markup=main_keyboard())

@dp.message(F.text == "🎰 Прогноздор")
async def show_games(message: Message):
    await message.answer("Кайсы оюнга прогноз алгыңыз келет?", reply_markup=games_keyboard())

@dp.message(F.text == "🎲 Башка оюндар")
async def other_games(message: Message):
    await message.answer("⏳ Бул оюндар азырынча кошула элек.", reply_markup=games_keyboard())

async def show_analysis_and_prediction(message: Message, prediction_text: str, photo_path: str = None):
    loading_msg = await message.answer("🔍 Анализ жүрүп жатат... 10 секунд күтө туруңуз... 🔍")
    await asyncio.sleep(10)
    await loading_msg.delete()
    if photo_path and os.path.exists(photo_path):
        photo = FSInputFile(photo_path)
        await message.answer_photo(photo=photo, caption=prediction_text, reply_markup=refresh_keyboard())
    else:
        await message.answer(prediction_text, reply_markup=refresh_keyboard())

@dp.message(F.text == "✈️ Lucky Jet")
async def lucky_jet(message: Message):
    pred_text = "✈️ LUCKY JET ПРОГНОЗУ\n📊 Коэффицент: 1.85x\n⏱️ Убакыт: 1-2 мүнөт\n📈 Багыт: ЖОГОРУ (UP)\n\n⏳ Прогноз 1 мүнөт иштейт!"
    await show_analysis_and_prediction(message, pred_text)

@dp.message(F.text == "💣 Mines")
async def mines(message: Message):
    images = [f for f in os.listdir(MINES_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    if not images:
        await message.answer("❌ Mines сүрөттөрү табылган жок.")
        return
    photo_path = os.path.join(MINES_DIR, random.choice(images))
    pred_text = "💣 MINES ПРОГНОЗУ\n🎯 Тактык: 92%\n⏳ 1 мүнөт иштейт\n🔥 Бонусту унутпа!"
    await show_analysis_and_prediction(message, pred_text, photo_path)

@dp.message(F.text == "🐔 Chicken Road")
async def chicken_road(message: Message):
    pred_text = "🐔 CHICKEN ROAD ПРОГНОЗУ\n📊 Коэффицент: 2.10x\n⏱️ Убакыт: 1 мүнөт\n📈 Багыт: ОҢ (RIGHT)\n\n⏳ Прогноз 1 мүнөт иштейт!"
    await show_analysis_and_prediction(message, pred_text)

@dp.callback_query(lambda c: c.data == "new_prediction")
async def new_prediction(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("Кайсы оюнга прогноз аласыз?", reply_markup=games_keyboard())
    await callback.message.delete()

@dp.message(F.text == "🎁 Бонустар")
async def show_bonuses(message: Message):
    await message.answer(
        "🎁 Кайсы казинодон бонус алгыңыз келет?\n\n"
        "⚠️ ЭСКЕРТҮҮ: Бонус ТЕК ЖАҢЫ АККАУНТКА берилет!",
        reply_markup=bonuses_keyboard()
    )

@dp.message(F.text == "🔴 1Win")
async def bonus_1win(message: Message):
    link = db.get_link("1win")
    promo = db.get_promocode("1win")
    if not link:
        await message.answer("⏳ 1Win шилтемеси азырынча кошула элек.")
        return
    await message.answer(
        f"🎁 1Win казинодон 500% бонус алыңыз!\n\n"
        f"1. Шилтеме: {link}\n"
        f"2. Жаңы аккаунт ачыңыз\n"
        f"3. Промокод: {promo}\n\n"
        f"⚠️ ТЕК ЖАҢЫ АККАУНТКА!"
    )

@dp.message(F.text == "🟡 Mostbet")
async def bonus_mostbet(message: Message):
    link = db.get_link("mostbet")
    promo = db.get_promocode("mostbet")
    if not link:
        await message.answer("⏳ Mostbet шилтемеси азырынча кошула элек.")
        return
    await message.answer(
        f"🎁 Mostbet казинодон 250% бонус алыңыз!\n\n"
        f"1. Шилтеме: {link}\n"
        f"2. Жаңы аккаунт ачыңыз\n"
        f"3. Промокод: {promo}\n\n"
        f"⚠️ ТЕК ЖАҢЫ АККАУНТКА!"
    )

@dp.message(F.text.in_(["🔵 Melbet", "🟣 1xBet"]))
async def bonus_not_ready(message: Message):
    await message.answer("⏳ Бул казино азырынча кошула элек.", reply_markup=bonuses_keyboard())

@dp.message(F.text == "🆘 Колдоо 24/7")
async def support_menu(message: Message):
    await message.answer("🆘 СУРООҢЫЗ БАРБЫ?\nБиздин колдоо кызматы 24/7 иштейт!", reply_markup=support_keyboard())

@dp.message(F.text == "❓ Прогноздор канчалык так?")
async def faq_accuracy(message: Message):
    await message.answer(
        "🎯 Прогноздор биздин шилтеме аркылуу катталган колдонуучулар үчүн иштейт.\n\n"
        "1Win же Mostbet шилтемеси аркылуу жаңы аккаунт ачып, промокодду жазыңыз."
    )

@dp.message(F.text == "📩 Админге жазуу")
async def contact_admin(message: Message):
    await message.answer("👨‍💻 Админге жазыңыз: @nurriksal\nСурооңузду жазсаңыз, тез арада жооп беребиз.")

@dp.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Сиз админ эмессиз!")
        return
    await message.answer("⚙️ Админ панель:", reply_markup=admin_keyboard())

@dp.message(lambda msg: msg.text and msg.text.startswith("📎 ") and msg.from_user.id == ADMIN_ID)
async def admin_change_link(message: Message, state: FSMContext):
    if "1Win" in message.text: key = "1win"
    elif "Mostbet" in message.text: key = "mostbet"
    elif "Melbet" in message.text: key = "melbet"
    elif "1xBet" in message.text: key = "1xbet"
    else: return
    await state.update_data(link_key=key)
    await message.answer(f"✏️ {key} үчүн жаңы шилтемени жазыңыз:")
    await state.set_state(AdminStates.waiting_for_link)

@dp.message(StateFilter(AdminStates.waiting_for_link))
async def set_new_link(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await state.clear()
        return
    data = await state.get_data()
    db.set_link(data.get("link_key"), message.text.strip())
    await message.answer(f"✅ Шилтеме жаңыртылды!")
    await state.clear()

@dp.message(F.text == "📝 Промокод өзгөртүү")
async def admin_change_promo(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    await state.set_state(AdminStates.waiting_for_promocode)
    await message.answer("✏️ Жаңы промокодду жазыңыз:")

@dp.message(StateFilter(AdminStates.waiting_for_promocode))
async def set_new_promo(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await state.clear()
        return
    new_promo = message.text.strip()
    for k in ["1win", "mostbet", "melbet", "1xbet"]:
        db.set_promocode(k, new_promo)
    await message.answer(f"✅ Промокод жаңыртылды: {new_promo}")
    await state.clear()

@dp.message(F.text == "📸 Каналга сүрөт жөнөтүү")
async def admin_send_photo_start(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    await state.set_state(AdminStates.waiting_for_channel_photo)
    await message.answer("📸 Сүрөттү жөнөтүңүз:")

@dp.message(StateFilter(AdminStates.waiting_for_channel_photo))
async def admin_send_photo_receive(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await state.clear()
        return
    file_id = message.photo[-1].file_id if message.photo else message.document.file_id
    await state.update_data(channel_photo_file_id=file_id)
    await state.set_state(AdminStates.waiting_for_channel_text)
    await message.answer("✏️ Эми текстти жазыңыз:")

@dp.message(StateFilter(AdminStates.waiting_for_channel_text))
async def admin_send_photo_text(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await state.clear()
        return
    data = await state.get_data()
    try:
        await bot.send_photo(chat_id=CHANNEL_USERNAME, photo=data.get("channel_photo_file_id"), caption=message.text.strip())
        await message.answer("✅ Каналга жиберилди!")
    except Exception as e:
        await message.answer(f"❌ Ката: {e}")
    await state.clear()

@dp.message()
async def fallback(message: Message):
    await message.answer("Башкы менюну колдонуңуз.", reply_markup=main_keyboard())

async def main():
    if not os.path.exists(MINES_DIR):
        os.makedirs(MINES_DIR)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
