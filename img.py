import requests
import random
import os

def generate_titan_image(prompt):
    # Models List
    models = ["flux", "flux-pro", "turbo", "pollinations-ai-aesthetic", "any-dark"]
    seed = random.randint(1, 999999)
    encoded_prompt = requests.utils.quote(prompt)
    
    # Try each model one by one
    for model in models:
        try:
            # 1. Image URL Construction
            url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?model={model}&width=1024&height=1024&seed={seed}&nologo=true"
            
            # 2. Downloading
            response = requests.get(url, timeout=20)
            if response.status_code == 200 and len(response.content) > 10000:
                file_path = f"img_{seed}.jpg"
                with open(file_path, "wb") as f:
                    f.write(response.content)
                return file_path, model.upper() # Return file and which model worked
        except:
            continue # Try next model if this one fails
            
    # If all models fail, try simple pollination (No model parameter)
    try:
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?nologo=true"
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            file_path = f"img_simple_{seed}.jpg"
            with open(file_path, "wb") as f:
                f.write(response.content)
            return file_path, "STANDARD"
    except:
        return None, None
