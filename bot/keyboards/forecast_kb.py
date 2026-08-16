from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

class RangeSelectCallback(CallbackData, prefix="fc_range"):
    days: int

class PageNavCallback(CallbackData, prefix="fc_nav"):
    index: int

def get_range_selection_keyboard() -> InlineKeyboardMarkup:
    """Buttons for choosing the date range"""

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📅 3 days", callback_data=RangeSelectCallback(days=3).pack()),
                InlineKeyboardButton(text="🗓️ 7 Days (Week)", callback_data=RangeSelectCallback(days=7).pack()),
            ],
            [
                InlineKeyboardButton(text="📆 14 Days (2 weeks)", callback_data=RangeSelectCallback(days=14).pack()),
            ],
            [
                InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_forecast")
            ]
        ]
    )

def get_forecast_navigation_keyboard(current_index: int, total_pages: int) -> InlineKeyboardMarkup:
    """Forecast page toggle buttons: [ ◀️ ] [ 1/7 ] [ ▶️ ]"""
    nav_row = []

    if current_index > 0:
        nav_row.append(
            InlineKeyboardButton(
                text="◀️ Previous", 
                callback_data=PageNavCallback(index=current_index - 1).pack()
            )
        )
    else:
        nav_row.append(InlineKeyboardButton(text="⏹️", callback_data="ignore"))

    nav_row.append(
        InlineKeyboardButton(
            text=f"Day {current_index + 1} / {total_pages}", 
            callback_data="ignore"
        )
    )

    if current_index < total_pages - 1:
        nav_row.append(
            InlineKeyboardButton(
                text="Next ▶️", 
                callback_data=PageNavCallback(index=current_index + 1).pack()
            )
        )
    else:
        nav_row.append(InlineKeyboardButton(text="⏹️", callback_data="ignore"))

    return InlineKeyboardMarkup(
        inline_keyboard=[
            nav_row,
            [InlineKeyboardButton(text="❌ Close", callback_data="cancel_forecast")]
        ]
    )