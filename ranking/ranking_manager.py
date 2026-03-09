import json, os
from datetime import datetime
from paths import data_path

RANKING_FILE = data_path("ranking.json")

def load_data():
    if not os.path.exists(RANKING_FILE):
        return {"snake": [], "mines": [], "pong": []}
    with open(RANKING_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(RANKING_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def add_score(game, player, score):
    data = load_data()
    if game not in data:
        data[game] = []
    data[game].append({
        "player": player,
        "score": score,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    # ordena y guarda solo top 10
    data[game] = sorted(data[game], key=lambda x: x["score"], reverse=True)[:10]
    save_data(data)

def get_top_scores(game):
    data = load_data()
    return data.get(game, [])
