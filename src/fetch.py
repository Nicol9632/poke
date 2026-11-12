import requests
import sqlite3
import json
import time
from datetime import datetime

conn = sqlite3.connect("data/pokemon.db")

# テーブル作成（2つ）
for table in ["raw_pokemon", "raw_species"]:
    conn.execute(f"""
    CREATE TABLE IF NOT EXISTS {table} (
      id INTEGER PRIMARY KEY,
      name TEXT,
      json TEXT,
      fetched_at TEXT
    )
    """)

def exists(table, name):
    """そのテーブルに保存済みならTrue"""
    row = conn.execute(f"SELECT 1 FROM {table} WHERE name = ?", (name,)).fetchone()
    return row is not None

def save(table, data):
    """JSONを丸ごと保存"""
    conn.execute(
        f"INSERT INTO {table} VALUES (?, ?, ?, ?)",
        (data["id"], data["name"], json.dumps(data), datetime.now().isoformat())
    )

# 全件の一覧を取得
url = "https://pokeapi.co/api/v2/pokemon?limit=2000&offset=0"
results = requests.get(url).json()["results"]
print(f"全{len(results)}件")

for i, p in enumerate(results, start=1):
    # pokemon
    if exists("raw_pokemon", p["name"]):
        continue
    data = requests.get(p["url"]).json()
    time.sleep(0.5)

    # species（フォーム違いは同じspeciesを共有するので、未保存のときだけ取得）
    species_name = data["species"]["name"]
    if not exists("raw_species", species_name):
        species = requests.get(data["species"]["url"]).json()
        save("raw_species", species)
        time.sleep(0.5)

    save("raw_pokemon", data)
    conn.commit()   # 1件ごとに確定（途中で止まっても続きから再開できる）
    print(f"{i}/{len(results)} 保存: {p['name']}")

conn.close()
print("完了")