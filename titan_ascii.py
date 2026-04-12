import os
import requests
from ascii_magic import AsciiArt, Back
import random

def create_ascii_art(query, chat_id):
    print(f"🛰️ MI Neural Press is generating ASCII Art for: {query}")
    
    # 1. AI Image Generation (تصویر بنانا)
    # ہم ٹاپک کو Pollinations کے لنک میں ڈال کر ڈاؤن لوڈ کریں گے
    seed = random.randint(100, 999)
    image_url = f"https://image.pollinations.ai/prompt/{query.replace(' ', '%20')}?width=1024&height=1024&seed={seed}"
    response = requests.get(image_url, timeout=10)
    
    img_name = f"temp_{chat_id}.jpg"
    with open(img_name, 'wb') as f:
        f.write(response.content)
    
    # 2. Convert to ASCII Art (ٹیکسٹ میں بدلنا)
    try:
        # ہم تصویر کو ٹیکسٹ میں بدلیں گے، اور اس کے رنگوں کو بھی سپورٹ کریں گے
        my_art = AsciiArt.from_image(img_name)
        
        # ٹیکسٹ کا اسٹائل: 'width' جتنا زیادہ ہوگا، ٹیکسٹ اتنا زیادہ ہوگا (زیادہ ڈیٹیل)
        ascii_text = my_art.to_terminal(columns=80, back=Back.BLACK)
        # اگر آپ صرف سادہ ٹیکسٹ (بغیر رنگوں کے) چاہتے ہیں:
        # ascii_text = my_art.to_ascii(columns=80) 
        
        print("✅ ASCII Art generated successfully!")
        
    except Exception as e:
        print(f"❌ ASCII Error: {e}")
        ascii_text = "⚠️ ASCII Art synthesis failed."
    
    # Clean up temp image
    if os.path.exists(img_name): os.remove(img_name)
    
    return ascii_text
