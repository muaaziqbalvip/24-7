import schedule
import time
import requests
import random

def fetch_post():
    topics = ["technology", "AI", "Islamic facts", "science"]
    topic = random.choice(topics)

    text = f"🔥 Daily Update about {topic}\nStay tuned with MI AI 🤖"
    img = f"https://source.unsplash.com/800x600/?{topic}"

    return text, img

def run_scheduler(bot, channel_id):
    def job():
        text, img = fetch_post()
        try:
            bot.send_photo(channel_id, img, caption=text)
        except:
            pass

    schedule.every(5).minutes.do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)