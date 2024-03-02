from typing import List
from aiogram import Router, F
from crypto_track.database.manager import AsyncDatabaseManager
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from crypto_track.database.models import Crypto
from crypto_track.enums import TimeOptions
from crypto_track.uils import generate_main_keyboard
from aiogram.types import (Message,
                           ReplyKeyboardRemove,
                           InlineKeyboardMarkup,
                           InlineKeyboardButton,
                           CallbackQuery,
                           ReplyKeyboardMarkup, 
                           KeyboardButton)


def load_profile_messages():
    with open('messages/profile/you_have_not_account.txt', 'r', encoding='utf-8') as file:
        you_have_not_account_text = file.read()

    with open('messages/profile/your_profile.txt', 'r', encoding='utf-8') as file:
        your_profile_text = file.read()

    with open('messages/profile/edit_how_often.txt', 'r', encoding='utf-8') as file:
        edit_how_often_text = file.read()

    return you_have_not_account_text, your_profile_text, edit_how_often_text
you_have_not_account_text, your_profile_text, edit_how_often_text = load_profile_messages()


class UpdateState(StatesGroup):
    name = State()
    how_often = State()
    tracking_cryptos = State()
    
profile_router = Router()


@profile_router.message(F.text == 'پروفایل 🧒')
async def view_profile(message: Message):
    user = await AsyncDatabaseManager().get_user_with_cryptos(user_id=message.from_user.id)
    if not user:
        await message.answer(text=you_have_not_account_text, reply_markup=ReplyKeyboardRemove())
        return
    crypto_sym_list = [crypto.symbol for crypto in user.tracking_cryptos]
    await message.answer(text=your_profile_text.format(user_name=user.name, 
                                                       how_often=user.how_often.value, 
                                                       tracking_cryptos=f'{", ".join(crypto_sym_list)}'),
                                                       reply_markup=generate_edit_profile_keyboard())


@profile_router.callback_query(F.data == 'profile_edit_name')
async def handle_edit_name_query(callback_query: CallbackQuery, state: FSMContext):
    try: 
        await callback_query.answer('درحال پردازش')
    except:
        pass
    await state.set_state(UpdateState.name)

    await callback_query.message.answer('<b>لطفا اسم جدید خودتون رو وارد کنید: </b>')

@profile_router.message(UpdateState.name)
async def handle_edit_name_message(message: Message, state: FSMContext):
    if not message.text:
        await message.reply('لطفا اسم خود به صورت متن وارد کنید🙂')
        return

    await state.clear()
    await AsyncDatabaseManager().update_user(user_id=message.from_user.id,
                                             new_user_name=message.text)

    await message.answer('<b>✅ اسم شما آپدیت شد!</b>', reply_markup=generate_main_keyboard())


@profile_router.callback_query(F.data == 'profile_edit_how_often')
async def handle_edit_how_often_query(callback_query: CallbackQuery, state: FSMContext):
    try:
        await callback_query.answer('درحال پردازش')
    except:
        pass
    await state.set_state(UpdateState.how_often)

    await callback_query.message.answer(
        edit_how_often_text,
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text=f'⏳ هر {i.value} دقیقه یکبار')
                ] for i in TimeOptions
                
            ],
            resize_keyboard=True
        )
    )

@profile_router.message(UpdateState.how_often)
async def handle_edit_how_often_message(message: Message, state: FSMContext):
    how_often = message.text
    for time_option in TimeOptions:
        if how_often == f'⏳ هر {time_option.value} دقیقه یکبار':
            await AsyncDatabaseManager().update_user(user_id=message.from_user.id,
                                                     new_how_often=time_option)
            await state.clear()

            await message.answer(
                '<b>✅!روتین دریافت خبر شما آپدیت شد</b>',
                reply_markup=generate_main_keyboard())
            return

    await message.reply("متوجه منظورت نمیشم! از دکمه های پایین استفاده کن!")


@profile_router.callback_query(F.data == 'profile_edit_tracking_cryptos')
async def handle_edit_tracking_cryptos_query(callback_query: CallbackQuery, state: FSMContext):
    try:
        await callback_query.answer('درحال پردازش')
    except:
        pass
    await state.set_state(UpdateState.tracking_cryptos)

    available_cryptos = await AsyncDatabaseManager().get_all_cryptos()
    user_cryptos = [str(crypto.id) for crypto in await AsyncDatabaseManager().get_user_cryptos(user_id=callback_query.from_user.id)]
    await state.update_data(tracking_cryptos=user_cryptos)
    
    await callback_query.message.answer(
            "<b>ارز هایی که بهشون علاقه مند هستین رو انتخاب کنین👇</b>",
            reply_markup=generate_crypto_selection_keyboard_update(available_cryptos, user_cryptos))

@profile_router.callback_query(F.data.startswith('select_crypto_update:'))
async def handle_crypto_selection(callback_query: CallbackQuery, state: FSMContext):
    try:
        await callback_query.answer('درحال پردازش')
    except:
        pass
    crypto_id = callback_query.data.split(':')[1]
    data = await state.get_data()
    selected_cryptos = data.get('tracking_cryptos', [])
    
    if crypto_id not in selected_cryptos:
        selected_cryptos.append(crypto_id)
    else:
        selected_cryptos.remove(crypto_id)
    
    await state.update_data(tracking_cryptos=selected_cryptos)

    # This is not very good to query cryptos each time but it is a good way for now.
    cryptos = await AsyncDatabaseManager().get_all_cryptos()
    await callback_query.message.edit_reply_markup(reply_markup=generate_crypto_selection_keyboard_update(cryptos, selected_cryptos))

@profile_router.callback_query(F.data == 'done_selecting_cryptos_update')
async def handle_done_selecting_cryptos(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if data.get('tracking_cryptos', []) == []:
        await callback_query.answer('حداقل باید یک ارز را انتخاب کنید.')
        return
    
    await callback_query.message.delete()
    await state.clear()

    try:
        await callback_query.answer('درحال پردازش اطلاعات...')
    except:
        pass

    await AsyncDatabaseManager().add_cryptos_to_user_tracked(user_id=callback_query.from_user.id,
                                                            cryptos_to_add_ids=data['tracking_cryptos'])

    await callback_query.message.answer(
        "<b>✅ارز های دنبال شده آپدیت شد!</b>",
        reply_markup=generate_main_keyboard()
        )


def generate_crypto_selection_keyboard_update(available_cryptos: List[Crypto], chosen_cryptos_ids: List[str]):
    buttons = []
    for crypto in available_cryptos:
        text = f"{'✔️ ' if str(crypto.id) in chosen_cryptos_ids else ''}{crypto.name}"
        callback_data = f"select_crypto_update:{crypto.id}"
        buttons.append([InlineKeyboardButton(text=text, callback_data=callback_data)])

    buttons.append([InlineKeyboardButton(text="✅ پایان", callback_data="done_selecting_cryptos_update")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def generate_edit_profile_keyboard() -> InlineKeyboardMarkup:
    buttons = []
    buttons.append([InlineKeyboardButton(text='ویرایش نام', callback_data='profile_edit_name')])
    buttons.append([InlineKeyboardButton(text='ویرایش روتین آپدیت', callback_data='profile_edit_how_often')])
    buttons.append([InlineKeyboardButton(text='ویرایش ارز های دنبال شده', callback_data='profile_edit_tracking_cryptos')])

    return InlineKeyboardMarkup(inline_keyboard=buttons)
