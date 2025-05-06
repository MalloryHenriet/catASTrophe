import random

from utils import create_table

tables = {
    "kpop_idols": ["Stage Name", "Full Name", "Korean Name", "K. Stage Name", "Date of Birth", "Group", "Country", "Height", "Weight", "Birthplace", "Gender", "Instagram"],
    "kpop_song_rankings": ["year", "time", "rank", "song_title", "artist", "album"]
}

class DatabaseGenerator:
    def __init__(self):
        pass

    def choose_pivot():
        return 0

    def generate_database(self):
        idols_random_cols = random.sample(tables["kpop_idols"], k=random.randint(1, len(tables["kpop_idols"])))
        songs_random_cols = random.sample(tables["kpop_song_rankings"], k=random.randint(1, len(tables["kpop_song_rankings"])))
        
        idols_table = create_table("idols_table", [(col, "TEXT") for col in idols_random_cols])
        songs_table = create_table("songs_table", [(col, "TEXT") for col in songs_random_cols])

        return random.random()
    

def main():
    gen = DatabaseGenerator()
    
    database = gen.generate_database()

if __name__ == "__main__":
    main()