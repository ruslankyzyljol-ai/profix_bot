import asyncio
import random
import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, FSInputFile, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, ADMIN_ID, CHANNEL_USERNAME, CHANNEL_URL, MINES_DIR
import database as db

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# -------------------- КЛАВИАТУРАЛАР --------------------
def main_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add(KeyboardButton("🎰 Прогноздор"), KeyboardButton("🎁 Бонустар"), KeyboardButton("🆘 Колдоо 24/7"))
    return kb

def games_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add(KeyboardButton("✈️ Lucky Jet"), KeyboardButton("💣 Mines"), KeyboardButton("🐔 Chicken Road"), KeyboardButton("⬅️ Артка"))
    return kb

def bonuses_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add(KeyboardButton("🔴 1Win"), KeyboardButton("🟡 Mostbet"), KeyboardButton("⬅️ Артка"))
    return kb

def support_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    kb.add(KeyboardButton("❓ Прогноздор канчалык так?"), KeyboardButton("📩 Админге жазуу"), KeyboardButton("⬅️ Артка"))
    return kb

def admin_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add(KeyboardButton("📎 1Win шилтеме"), KeyboardButton("📎 Mostbet шилтеме"), KeyboardButton("📝 Промокод өзгөртүү"), KeyboardButton("📸 Каналга сүрөт жөнөтүү"), KeyboardButton("⬅️ Артка"))
    return kb

def refresh_keyboard():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🔄 Жаңы прогноз", callback_data="new_prediction"))
    return kb

# -------------------- ПРОВЕРКА ПОДПИСКИ --------------------
async def is_subscribed(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# -------------------- FSM ДЛЯ АДМИНА --------------------
class AdminStates(StatesGroup):
    waiting_for_link = State()
    waiting_for_promocode = State()
    waiting_for_channel_photo = State()
    waiting_for_channel_text = State()

# -------------------- ХЕНДЛЕРЛЕР --------------------
@dp.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    if await is_subscribed(user_id):
        await message.answer(f"👋 Салам, {message.from_user.first_name}!\nPROFIXKG прогноз ботуна кош келиңиз!\n\nТөмөнкү бөлүмдөрдүн бирин тандаңыз:", reply_markup=main_keyboard())
    else:
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("📢 Каналга өтүү", url=CHANNEL_URL))
        kb.add(InlineKeyboardButton("✅ Текшерүү", callback_data="check_sub"))
        await message.answer(f"🔔 Ботту колдонуу үчүн биздин каналга жазылыңыз:\n{CHANNEL_URL}\n\nАндан кийин «Текшерүү» баскычын басыңыз.", reply_markup=kb)

@dp.callback_query(lambda c: c.data == "check_sub")
async def check_subscription(callback: CallbackQuery):
    user_id = callback.from_user.id
    if await is_subscribed(user_id):
        await callback.message.delete()
        await callback.message.answer("✅ Рахмат! Эми сиз ботту толук колдоно аласыз.", reply_markup=main_keyboard())
    else:
        await callback.answer("❌ Сиз дагы эле каналга жазылган жоксуз. Жазылып, кайра басыңыз.", show_alert=True)

@dp.message(lambda msg: msg.text == "⬅️ Артка")
async def back_to_main(message: Message):
    await message.answer("Башкы меню:", reply_markup=main_keyboard())

@dp.message(lambda msg: msg.text == "🎰 Прогноздор")
async def show_games(message: Message):
    await message.answer("Кайсы оюнга прогноз алгыңыз келет?", reply_markup=games_keyboard())

async def show_analysis_and_prediction(message: Message, game_type: str, prediction_text: str, photo_path: str = None):
    loading_msg = await message.answer("🔍 Анализ жүрүп жатат... 10 секунд күтө туруңуз... 🔍")
    await asyncio.sleep(10)
    await loading_msg.delete()
    if photo_path and os.path.exists(photo_path):
        photo = FSInputFile(photo_path)
        await message.answer_photo(photo=photo, caption=prediction_text, reply_markup=refresh_keyboard())
    else:
        await message.answer(prediction_text, reply_markup=refresh_keyboard())

@dp.message(lambda msg: msg.text == "✈️ Lucky Jet")
async def lucky_jet(message: Message):
    pred_text = "✈️ LUCKY JET ПРОГНОЗУ\n📊 Коэффицент: 1.85x\n⏱️ Убакыт: 1-2 мүнөт\n📈 Багыт: ЖОГОРУ (UP)\n\n⏳ Прогноз 1 мүнөт иштейт!"
    await show_analysis_and_prediction(message, "luckyjet", pred_text)

@dp.message(lambda msg: msg.text == "💣 Mines")
async def mines(message: Message):
    images = [f for f in os.listdir(MINES_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    if not images:
        await message.answer("❌ Mines сүрөттөрү табылган жок. Админге кайрылыңыз.")
        return
    chosen = random.choice(images)
    photo_path = os.path.join(MINES_DIR, chosen)
    pred_text = "💣 MINES ПРОГНОЗУ\n🎯 Тактык: 92%\n⏳ 1 мүнөт иштейт\n🔥 Бонусту унутпа!"
    await show_analysis_and_prediction(message, "mines", pred_text, photo_path)

@dp.message(lambda msg: msg.text == "🐔 Chicken Road")
async def chicken_road(message: Message):
    pred_text = "🐔 CHICKEN ROAD ПРОГНОЗУ\n📊 Коэффицент: 2.10x\n⏱️ Убакыт: 1 мүнөт\n📈 Багыт: ОҢ (RIGHT)\n\n⏳ Прогноз 1 мүнөт иштейт!"
    await show_analysis_and_prediction(message, "chickenroad", pred_text)

@dp.callback_query(lambda c: c.data == "new_prediction")
async def new_prediction(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("Кайсы оюнга прогноз аласыз?", reply_markup=games_keyboard())
    await callback.message.delete()

@dp.message(lambda msg: msg.text == "🎁 Бонустар")
async def show_bonuses(message: Message):
    await message.answer("🎁 Кайсы казинодон бонус алгыңыз келет?\n\n⚠️ ЭСКЕРТҮҮ: Бонус ТЕК ЖАҢЫ АККАУНТКА берилет!\nЭски аккаунт менен кирсеңиз, бонус берилбейт.", reply_markup=bonuses_keyboard())

@dp.message(lambda msg: msg.text == "🔴 1Win")
async def bonus_1win(message: Message):
    link = db.get_link("1win")
    promo = db.get_promocode("1win")
    if not link:
        await message.answer("⏳ 1Win шилтемеси азырынча кошула элек. Кийинчерээк кайра байкаңыз.")
        return
    await message.answer(f"🎁 1Win казинодон 500% бонус алыңыз!\n\n📝 КАНТИП АЛУУ КЕРЕК:\n1. Төмөнкү шилтеме аркылуу өтүңүз:\n{link}\n2. Жаңы аккаунт ачыңыз\n3. **{promo}** промокодун жазыңыз\n4. Бонус автоматтык түрдө берилет\n\n⚠️ ТЕК ЖАҢЫ АККАУНТКА!")

@dp.message(lambda msg: msg.text == "🟡 Mostbet")
async def bonus_mostbet(message: Message):
    link = db.get_link("mostbet")
    promo = db.get_promocode("mostbet")
    if not link:
        await message.answer("⏳ Mostbet шилтемеси азырынча кошула элек. Кийинчерээк кайра байкаңыз.")
        return
    await message.answer(f"🎁 Mostbet казинодон 250% бонус алыңыз!\n\n📝 КАНТИП АЛУУ КЕРЕК:\n1. Төмөнкү шилтеме аркылуу өтүңүз:\n{link}\n2. Жаңы аккаунт ачыңыз\n3. **{promo}** промокодун жазыңыз\n4. Бонус автоматтык түрдө берилет\n\n⚠️ ТЕК ЖАҢЫ АККАУНТКА!")

@dp.message(lambda msg: msg.text in ["🔵 Melbet", "🟣 1xBet"])
async def bonus_not_ready(message: Message):
    await message.answer("⏳ Бул казино азырынча кошула элек. Башкасын тандаңыз!", reply_markup=bonuses_keyboard())

@dp.message(lambda msg: msg.text == "🆘 Колдоо 24/7")
async def support_menu(message: Message):
    await message.answer("🆘 СУРООҢЫЗ БАРБЫ?\nБиздин колдоо кызматы 24/7 иштейт!\n\nТөмөнкү баскычтардын бирин тандаңыз:", reply_markup=support_keyboard())

@dp.message(lambda msg: msg.text == "❓ Прогноздор канчалык так?")
async def faq_accuracy(message: Message):
    await message.answer("🎯 Прогноздордун тактыгы биздин шилтеме аркылуу катталган колдонуучулар үчүн гана 100% иштейт.\n\nСиз **1Win** же **Mostbet** шилтемеси аркылуу жаңы аккаунт ачып, тиешелүү промокодду (PROFIN же PROFIX) жазышыңыз керек.\nОшондо гана так прогноздорду жана бонустарды аласыз!\n\n⚠️ Эски аккаунт менен кирсеңиз, прогноздор иштебей калышы мүмкүн.")

@dp.message(lambda msg: msg.text == "📩 Админге жазуу")
async def contact_admin(message: Message):
    await message.answer("👨‍💻 Админге жазыңыз: @nurriksal\nСурооңузду жазсаңыз, тез арада жооп беребиз.")

@dp.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Сиз админ эмессиз!")
        return
    await message.answer("⚙️ Админ панель. Эмне кылгыңыз келет?", reply_markup=admin_keyboard())

@dp.message(lambda msg: msg.text.startswith("📎 ") and msg.from_user.id == ADMIN_ID)
async def admin_change_link(message: Message, state: FSMContext):
    if "1Win" in message.text:
        key = "1win"
    elif "Mostbet" in message.text:
        key = "mostbet"
    else:
        await message.answer("Туура эмес баскыч.")
        return
    await state.update_data(link_key=key)
    await message.answer(f"✏️ {key} үчүн жаңы шилтемени жазыңыз:")
    await state.set_state(AdminStates.waiting_for_link)

@dp.message(StateFilter(AdminStates.waiting_for_link))
async def set_new_link(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await state.clear()
        return
    data = await state.get_data()
    key = data.get("link_key")
    new_link = message.text.strip()
    db.set_link(key, new_link)
    await message.answer(f"✅ {key} шилтемеси жаңыртылды!\n🔗 Жаңы шилтеме: {new_link}")
    await state.clear()

@dp.message(lambda msg: msg.text == "📝 Промокод өзгөртүү" and msg.from_user.id == ADMIN_ID)
async def admin_change_promo(message: Message, state: FSMContext):
    await state.set_state(AdminStates.waiting_for_promocode)
    await message.answer("✏️ Жаңы промокодду жазыңыз (бардык казинолор үчүн бирдей):")

@dp.message(StateFilter(AdminStates.waiting_for_promocode))
async def set_new_promo(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await state.clear()
        return
    new_promo = message.text.strip()
    db.set_promocode("1win", new_promo)
    db.set_promocode("mostbet", new_promo)
    db.set_promocode("melbet", new_promo)
    db.set_promocode("1xbet", new_promo)
    await message.answer(f"✅ Промокод БААРЫНА жаңыртылды!\n📝 Жаңы промокод: {new_promo}")
    await state.clear()

@dp.message(lambda msg: msg.text == "📸 Каналга сүрөт жөнөтүү" and msg.from_user.id == ADMIN_ID)
async def admin_send_photo_to_channel_start(message: Message, state: FSMContext):
    await state.set_state(AdminStates.waiting_for_channel_photo)
    await message.answer("📸 Каналга жибере турган СҮРӨТТҮ жөнөтүңүз (файл же фото):")

@dp.message(StateFilter(AdminStates.waiting_for_channel_photo), lambda m: m.photo or m.document)
async def admin_send_photo_to_channel_photo(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await state.clear()
        return
    if message.photo:
        file_id = message.photo[-1].file_id
    else:
        file_id = message.document.file_id
    await state.update_data(channel_photo_file_id=file_id)
    await state.set_state(AdminStates.waiting_for_channel_text)
    await message.answer("✏️ Эми ошол сүрөткө тиешелүү ТЕКСТИ жазыңыз:")

@dp.message(StateFilter(AdminStates.waiting_for_channel_text))
async def admin_send_photo_to_channel_text(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await state.clear()
        return
    data = await state.get_data()
    file_id = data.get("channel_photo_file_id")
    caption = message.text.strip()
    try:
        await bot.send_photo(chat_id=CHANNEL_USERNAME, photo=file_id, caption=caption)
        await message.answer("✅ Сүрөт жана текст каналга жиберилди!")
    except Exception as e:
        await message.answer(f"❌ Катташууда ката: {e}")
    await state.clear()

@dp.message()
async def fallback(message: Message):
    await message.answer("Түшүнүксүз буйрук. Башкы менюну колдонуңуз.", reply_markup=main_keyboard())

async def main():
    if not os.path.exists(MINES_DIR):
        os.makedirs(MINES_DIR)
        print(f"⚠️ {MINES_DIR} папкасы түзүлдү. 8 сүрөт салыңыз.")
    print("🤖 Бот иштеп жатат...")
    await dp.start_polling(bot)
