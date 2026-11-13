import sqlite3
import pandas as pd
import plotly.express as px
import os

conn = sqlite3.connect("data/pokemon.db")

conn.execute("DROP VIEW IF EXISTS mart_stats_by_generation")
conn.execute("""
    CREATE VIEW mart_stats_by_generation AS
    SELECT
        generation,
        COUNT(*)              AS pokemon_count,
        ROUND(AVG(total), 1)  AS avg_total,
        MAX(total)            AS max_total,
        MIN(total)            AS min_total
    FROM stg_pokemon
    WHERE is_default = 1
        AND is_legendary = 0
        AND is_mythical = 0
    GROUP BY generation
    ORDER BY generation
""")

for row in conn.execute("SELECT * FROM mart_stats_by_generation"):
    print(row)

os.makedirs("output", exist_ok=True) 

# ① 折れ線用のデータ（mart）
df = pd.read_sql("SELECT * FROM mart_stats_by_generation", conn)

# ② 箱ひげ図用のデータ（stagingから1匹ずつ）
df_all = pd.read_sql("""
    SELECT generation, total FROM stg_pokemon
    WHERE is_default = 1 AND is_legendary = 0 AND is_mythical = 0
""", conn)

conn.close()   # データを読み終わったら閉じる

# ③ 折れ線グラフ
fig = px.line(
    df, x="generation", y="avg_total", markers=True,
    title="世代ごとの平均合計種族値（伝説・幻・別フォームを除く）",
    labels={"generation": "世代", "avg_total": "平均合計種族値"},
)
fig.write_html("output/stats_by_generation.html")

# ④ 箱ひげ図
fig2 = px.box(
    df_all, x="generation", y="total",
    title="世代ごとの合計種族値の分布",
    labels={"generation": "世代", "total": "合計種族値"},
)
fig2.write_html("output/stats_distribution.html")

print("保存しました")
