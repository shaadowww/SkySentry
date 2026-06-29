from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

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