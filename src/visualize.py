import sqlite3

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

conn.close()