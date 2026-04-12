import requests
import random
import os

def generate_titan_image(prompt):
    # صرف وہ ماڈلز جو سب سے فاسٹ ہیں
    models = ["flux", "turbo", "pollinations-ai-aesthetic"]
    seed = random.randint(1, 999999)
    encoded_prompt = requests.utils.quote(prompt)
    
    # ہم صرف ایک کوشش کریں گے سب سے فاسٹ ماڈل کے ساتھ
    model = random.choice(models) 
    
    try:
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?model={model}&width=1024&height=1024&seed={seed}&nologo=true"
        
        # Timeout صرف 10 سیکنڈ (تاکہ یوزر کو ویٹ نہ کرنا پڑے)
        response = requests.get(url, timeout=12)
        
        if response.status_code == 200:
            file_path = f"img_{seed}.jpg"
            with open(file_path, "wb") as f:
                f.write(response.content)
            return file_path, model.upper()
    except:
        # اگر فیل ہو تو فوراً سمپل ماڈل پر جائیں (بغیر کسی نخرے کے)
        try:
            simple_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?nologo=true"
            res = requests.get(simple_url, timeout=10)
            if res.status_code == 200:
                file_path = f"img_s_{seed}.jpg"
                with open(file_path, "wb") as f:
                    f.write(res.content)
                return file_path, "STANDARD"
        except:
            return None, None
    return None, None
