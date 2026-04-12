import os
import requests
import random
from PIL import Image

def create_ascii_art(query, chat_id):
    try:
        # 1. Image Download
        seed = random.randint(100, 999)
        image_url = f"https://image.pollinations.ai/prompt/{query.replace(' ', '%20')}?width=100&height=100&seed={seed}"
        response = requests.get(image_url, timeout=15)
        
        img_name = f"temp_{chat_id}.jpg"
        with open(img_name, 'wb') as f:
            f.write(response.content)

        # 2. ASCII Character Set (Simple to Complex)
        chars = ["@", "#", "S", "%", "?", "*", "+", ";", ":", ",", "."]

        # 3. Process Image with PIL
        img = Image.open(img_name).convert('L') # Convert to Grayscale
        # سائز چھوٹا رکھیں تاکہ ٹیلی گرام پر میسج کریش نہ ہو
        width, height = 60, 30 
        img = img.resize((width, height))
        
        pixels = img.getdata()
        ascii_str = ""
        for i, pixel in enumerate(pixels):
            # پکسل کو ٹیکسٹ میں بدلنا
            ascii_str += chars[pixel // 25] 
            if (i + 1) % width == 0:
                ascii_str += "\n"

        if os.path.exists(img_name): os.remove(img_name)
        return ascii_str

    except Exception as e:
        print(f"Error in ASCII: {e}")
        return None
