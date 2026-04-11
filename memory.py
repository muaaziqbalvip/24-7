memory = {}

def get_history(uid):
    if uid not in memory:
        memory[uid] = []
    return memory[uid]

def update_history(uid, role, text):
    history = get_history(uid)
    history.append({"role": role, "parts": [{"text": text}]})

    if len(history) > 10:
        memory[uid] = history[-10:]