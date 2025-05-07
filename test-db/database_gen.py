import random
import pandas as pd

from utils import create_table, load_csv, generate_insert
from config import TABLES_HEADER, TABLES_HEADER_WITH_TYPE

class DatabaseGenerator:
    def __init__(self):
        pass

    def choose_pivot():
        return 0

    def generate_database(self):
        idols_random_cols = random.sample(TABLES_HEADER["kpop_idols"], k=random.randint(1, len(TABLES_HEADER["kpop_idols"])))
        songs_random_cols = random.sample(TABLES_HEADER["kpop_song_rankings"], k=random.randint(1, len(TABLES_HEADER["kpop_song_rankings"])))
        
        idols_df = load_csv("./datasets/kpop_idols.csv", TABLES_HEADER["kpop_idols"], idols_random_cols)
        songs_df = load_csv("./datasets/kpop_rankings.csv", TABLES_HEADER["kpop_song_rankings"], songs_random_cols)

        idols_table = create_table("idols_table", [(col, TABLES_HEADER_WITH_TYPE["kpop_idols"].get(col, "TEXT")) for col in idols_random_cols])
        songs_table = create_table("songs_table", [(col, TABLES_HEADER_WITH_TYPE["kpop_song_rankings"].get(col, "TEXT")) for col in songs_random_cols])

        insert_idols = generate_insert("idols_table", idols_df)
        insert_songs = generate_insert("songs_table", songs_df)

        sql_script = "\n\n".join([
            idols_table,
            songs_table,
            insert_idols,
            insert_songs
        ])

        with open("test_db.sql", "w", encoding="utf-8") as f:
            f.write(sql_script)

        return "test_db.sql"