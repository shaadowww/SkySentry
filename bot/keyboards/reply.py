from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """
    Keyboard with cancel button for FSM scenaries
    """

    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❌ Cancel")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )