import sqlite3
import pandas as pd
import plotly.express as px
import os

conn = sqlite3.connect("data/pokemon.db")

df_combo = pd.read_sql("""
SELECT
    CASE WHEN type2 IS NULL OR type1 < type2 THEN type1 ELSE type2 END AS type_a,
    CASE WHEN type2 IS NULL OR type1 < type2 THEN type2 ELSE type1 END AS type_b,
    COUNT(*)             AS pokemon_count,
	MAX(total) AS max_total,
	MIN(total) AS min_total,
    ROUND(AVG(total), 1) AS avg_total
FROM stg_pokemon
WHERE is_default = 1 AND is_legendary = 0 AND is_mythical = 0
GROUP BY type_a, type_b
HAVING COUNT(*) >= 3
ORDER BY avg_total;
""", conn) 

# グラフのラベル用に「type_a・type_b」の文字列を作る
df_combo["combo"] = df_combo["type_a"] + "・" + df_combo["type_b"].fillna("")

fig3 = px.scatter(
    df_combo, x="avg_total", y="combo",
    error_x=df_combo["max_total"] - df_combo["avg_total"],        # 平均から最大までの線
    error_x_minus=df_combo["avg_total"] - df_combo["min_total"],  # 平均から最小までの線
    title="タイプの組み合わせ別 合計種族値（点＝平均、線＝最小〜最大）",
    labels={"avg_total": "合計種族値", "combo": "タイプの組み合わせ"},
    height=1200,   # 行が多いので縦長にする
)
fig3.write_image("output/data03-chart.png", scale=2)

print("保存しました")
