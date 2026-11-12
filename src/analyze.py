import sqlite3
import json

conn = sqlite3.connect("data/pokemon.db")

# 世代の表記を数字に変換するための対応表
GEN = {
    "generation-i": 1, "generation-ii": 2, "generation-iii": 3,
    "generation-iv": 4, "generation-v": 5, "generation-vi": 6,
    "generation-vii": 7, "generation-viii": 8, "generation-ix": 9,
}

# 毎回作り直す（rawから何度でも再現できるので）
conn.execute("DROP TABLE IF EXISTS stg_pokemon")
conn.execute("""
CREATE TABLE stg_pokemon (
  id INTEGER PRIMARY KEY,
  name TEXT,
  name_ja TEXT,
  species TEXT,
  is_default INTEGER,
  generation INTEGER,
  type1 TEXT,
  type2 TEXT,
  hp INTEGER, attack INTEGER, defense INTEGER,
  sp_attack INTEGER, sp_defense INTEGER, speed INTEGER,
  total INTEGER,
  height_m REAL,
  weight_kg REAL,
  is_legendary INTEGER,
  is_mythical INTEGER
)
""")

# ① speciesの情報を、名前で引ける辞書にしておく
species_map = {}
for name, js in conn.execute("SELECT name, json FROM raw_species").fetchall():
    s = json.loads(js)
    name_ja = None
    for n in s["names"]:
        if n["language"]["name"] == "ja-hrkt":
            name_ja = n["name"]
    species_map[name] = {
        "name_ja": name_ja,
        "generation": GEN[s["generation"]["name"]],
        "is_legendary": int(s["is_legendary"]),
        "is_mythical": int(s["is_mythical"]),
    }

# ② pokemonを1件ずつ整形して保存
for (js,) in conn.execute("SELECT json FROM raw_pokemon").fetchall():
    p = json.loads(js)
    sp = species_map[p["species"]["name"]]

    # 種族値を {"hp": 35, "attack": 55, ...} の形にする
    stats = {s["stat"]["name"]: s["base_stat"] for s in p["stats"]}

    # タイプ（1つ目・2つ目）
    types = sorted(p["types"], key=lambda t: t["slot"])
    type1 = types[0]["type"]["name"]
    type2 = types[1]["type"]["name"] if len(types) > 1 else None

    conn.execute(
        "INSERT INTO stg_pokemon VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (
            p["id"], p["name"], sp["name_ja"], p["species"]["name"],
            int(p["is_default"]), sp["generation"],
            type1, type2,
            stats["hp"], stats["attack"], stats["defense"],
            stats["special-attack"], stats["special-defense"], stats["speed"],
            sum(stats.values()),
            p["height"] / 10, p["weight"] / 10,
            sp["is_legendary"], sp["is_mythical"],
        ),
    )

conn.commit()
conn.close()
print("staging完了")