# Image Generator for weather forecast
import os
import io
from PIL import Image, ImageDraw, ImageFont

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BOT_DIR = os.path.dirname(CURRENT_DIR)


class WIG:
    DAY_BG_PATH = os.path.join(BOT_DIR, "assets", "images", "sky_bg.png")
    NIGHT_BG_PATH = os.path.join(BOT_DIR, "assets", "images", "night_sky_bg.png")
    FONT_PATH = os.path.join(BOT_DIR, "assets", "fonts", "Montserrat-Regular.ttf")
    FONT_BOLD_PATH = os.path.join(BOT_DIR, "assets", "fonts", "Montserrat-Bold.ttf")

    @classmethod
    def generate_weather_card(
        cls, 
        city: str, 
        temp: float, 
        weather_state: str, 
        day_state: str
    ) -> io.BytesIO:
        """Generates Weather Info Card"""

        try:
            if day_state == "Day":
                img = Image.open(cls.DAY_BG_PATH).convert("RGBA").resize((1000,1000))
            else: 
                img = Image.open(cls.NIGHT_BG_PATH).convert("RGBA").resize((1000,1000))
        except FileNotFoundError:
            img = Image.new("RGBA", (1000, 1000), color="#1e2530")

        try:
            font_city = ImageFont.truetype(cls.FONT_PATH, 75)
            font_state = ImageFont.truetype(cls.FONT_PATH, 45)
            font_temp = ImageFont.truetype(cls.FONT_BOLD_PATH, 150)
            font_dayinfo = ImageFont.truetype(cls.FONT_PATH, 45)
        except OSError:
            print(f"🚨 Error: Check out the font presence Montserrat in bot/assets/fonts/.")
            font_city = font_state = font_temp = font_dayinfo = ImageFont.load_default()


        overlay = Image.new("RGBA", (1000, 1000), (0, 0, 0, 90))
        img = Image.alpha_composite(img, overlay).convert("RGBA")
        draw = ImageDraw.Draw(img)

        center_x = 500

        draw.text((center_x, 220), city, fill="#ffffff", font=font_city, anchor="mm")
        
        
        draw.text((center_x, 310), weather_state, fill="#cfd8dc", font=font_state, anchor="mm")
    
        draw.text((center_x, 540), f"{temp}°C", fill="#ffffff", font=font_temp, anchor="mm")

        draw.text((center_x, 750), f"{day_state}", fill="#ffffff", font=font_dayinfo, anchor="mm")

        image_buffer = io.BytesIO()
        img.save(image_buffer, format="PNG")
        image_buffer.seek(0)

        return image_buffer