from typing import List
from crypto_track.database.manager import AsyncDatabaseManager
from crypto_track.enums import TimeOptions
from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardButton, 
    InlineKeyboardMarkup, 
    CallbackQuery,
)
from crypto_track.database.models import Crypto
from crypto_track.uils import generate_main_keyboard


def load_signup_messages():
    with open('messages/signup/new_user_signup.txt', 'r', encoding='utf-8') as file:
        new_user_signup_text = file.read()

    with open('messages/signup/new_user_comeback.txt', 'r', encoding='utf-8') as file:
        new_user_comeback_text = file.read()

    with open('messages/signup/handle_name_signup.txt', 'r', encoding='utf-8') as file:
        handle_name_signup_text = file.read()

    with open('messages/signup/handle_howoften_signup.txt', 'r', encoding='utf-8') as file:
        handle_howoften_signup_text = file.read()

    with open('messages/signup/new_user_welcome.txt', 'r', encoding='utf-8') as file:
        new_user_welcome_text = file.read()
    
    with open('messages/signup/fail_signup.txt', 'r', encoding='utf-8') as file:
        fail_signup_text = file.read()

    return new_user_signup_text, new_user_comeback_text, handle_name_signup_text, handle_howoften_signup_text, new_user_welcome_text, fail_signup_text

new_user_signup_text, new_user_comeback_text, handle_name_signup_text, handle_howoften_signup_text, new_user_welcome_text, fail_signup_text = load_signup_messages()

signup_router = Router()

class SignUpForm(StatesGroup):
    name = State()
    how_often = State()
    tracked_cryptos = State()


@signup_router.message(CommandStart())
async def start(message: Message, state: FSMContext) -> None:
    user_exists = await AsyncDatabaseManager().check_user_exists(user_id=message.from_user.id)
    
    if user_exists:
        await message.answer(
            new_user_comeback_text.format(user_name=user_exists.name),
            reply_markup=generate_main_keyboard()
        )
    else:
        await state.set_state(SignUpForm.name)
        await message.answer(
            new_user_signup_text, 
            reply_markup=ReplyKeyboardRemove()
        )


@signup_router.message(SignUpForm.name)
async def handle_name(message: Message, state: FSMContext):
    if not message.text:
        await message.reply('لطفا اسم خود به صورت متن وارد کنید🙂')
        return
    await state.update_data(name=message.text)
    await state.set_state(SignUpForm.how_often)

    await message.answer(
        handle_name_signup_text.format(user_name=message.text.title()),
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text=f'⏳ هر {i.value} دقیقه یکبار')
                ] for i in TimeOptions
                
            ],
            resize_keyboard=True
        )
    )


@signup_router.message(SignUpForm.how_often, F.text)
async def handle_how_often(message: Message, state: FSMContext):
    how_often = message.text
    for time_option in TimeOptions:
        if how_often == f'⏳ هر {time_option.value} دقیقه یکبار':
            data = await state.update_data(how_often=time_option)
            await state.set_state(SignUpForm.tracked_cryptos)
            # 👇
            available_cryptos = await AsyncDatabaseManager().get_all_cryptos()

            await message.answer(
                handle_howoften_signup_text.format(user_name=data.get('name', ''), how_often=time_option.value),
                reply_markup=generate_crypto_selection_keyboard(available_cryptos, []))
            return

    await message.reply("متوجه منظورت نمیشم! از دکمه های پایین استفاده کن!")


@signup_router.callback_query(F.data.startswith('select_crypto:'))
async def handle_crypto_selection(callback_query: CallbackQuery, state: FSMContext):
    try:
        await callback_query.answer('درحال پردازش')
    except:
        pass
    crypto_id = callback_query.data.split(':')[1]
    data = await state.get_data()
    selected_cryptos = data.get('tracked_cryptos', [])
    
    if crypto_id not in selected_cryptos:
        selected_cryptos.append(crypto_id)
    else:
        selected_cryptos.remove(crypto_id)
    
    await state.update_data(tracked_cryptos=selected_cryptos)

    # This is not very good to query cryptos each time but it is a good way for now.
    cryptos = await AsyncDatabaseManager().get_all_cryptos()
    await callback_query.message.edit_reply_markup(reply_markup=generate_crypto_selection_keyboard(cryptos, selected_cryptos))


@signup_router.callback_query(F.data == 'done_selecting_cryptos')
async def handle_done_selecting_cryptos(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if data.get('tracked_cryptos', None) is None:
        await callback_query.answer('حداقل باید یک ارز را انتخاب کنید.')
        return
    
    await callback_query.message.delete()
    await state.clear()

    if not data.get('name', None) or not data.get('how_often', None):
        try:
            await callback_query.answer(
                "مشکلی رخ داد!💔",
                reply_markup=ReplyKeyboardRemove())
        except:
            pass
        await callback_query.message.answer(fail_signup_text)
    else:
        try:
            await callback_query.answer('درحال پردازش اطلاعات...')
        except:
            pass
        new_user = await AsyncDatabaseManager().create_new_user_and_add_cryptos(user_id=callback_query.from_user.id,
                                                                                user_name=data['name'],
                                                                                how_often=data['how_often'],
                                                                                cryptos_to_add_ids=data['tracked_cryptos'])
        await callback_query.message.answer(
            generate_newuser_welcome(name=new_user.name, how_often=new_user.how_often, tracking_cryptos=data['tracked_cryptos']),
            reply_markup=generate_main_keyboard()
            )


def generate_crypto_selection_keyboard(available_cryptos: List[Crypto], chosen_cryptos_ids: List[str]):
    buttons = []
    for crypto in available_cryptos:
        text = f"{'✔️ ' if str(crypto.id) in chosen_cryptos_ids else ''}{crypto.name}"
        callback_data = f"select_crypto:{crypto.id}"
        buttons.append([InlineKeyboardButton(text=text, callback_data=callback_data)])

    buttons.append([InlineKeyboardButton(text="✅ پایان", callback_data="done_selecting_cryptos")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def generate_newuser_welcome(name: str, how_often: str, tracking_cryptos: List):
    return new_user_welcome_text.format(user_name=name, how_often=how_often.value, following_Cryptos_number=len(tracking_cryptos))
