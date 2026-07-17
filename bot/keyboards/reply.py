import datetime
from aiogram.types import (
    ReplyKeyboardMarkup, 
    KeyboardButton, 
    InlineKeyboardButton, 
    InlineKeyboardMarkup,
)

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from bot.states import *

def share_location() -> ReplyKeyboardMarkup:
    """
    Location sharing keyboard
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📍 Share Location", request_location=True)],
            [KeyboardButton(text="❌ Cancel")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def cancel_keyboard() -> ReplyKeyboardMarkup:
    """
    Cancel Keyboard
    """

    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❌ Cancel")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

schedule_update = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Add Schedule", callback_data="add")],
    [InlineKeyboardButton(text="Remove Schedule", callback_data="remove")]
])

def user_schedules_buttons(schedules_indxs: list[str]) -> InlineKeyboardMarkup:
    """Reply Markup while `remove schedule`
    according to how many schedules user has"""
    builder = InlineKeyboardBuilder()

    for index in schedules_indxs:
        builder.button(text=f"🗑️ #{index}", callback_data=f"del_num_{index}")
    
    builder.button(text="❌ Cancel", callback_data="schedule_delete_cancel")

    # TODO сделать приятное отображение кнопок расписаний

    n = len(schedules_indxs)

    button_adjust: list[int] = [4] * (n // 4)

    if n % 4 > 0:
        button_adjust.append(n % 4)

    builder.adjust(*button_adjust, 1)

    return builder.as_markup()