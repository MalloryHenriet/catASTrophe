SQL_CLAUSES = ["SELECT", "FROM", "JOIN", "WHERE", "GROUP BY", "ORDER BY", "LIMIT", "HAVING", "UPDATE", "DELETE"]
#TODO: check that all clauses apply to our versions of SQLite

VERSIONS = ["/usr/bin/sqlite3-3.26.0", "/usr/bin/sqlite3-3.39.4"]

BUG_TYPES = ["CRASH", "LOGIC"]

TABLES_HEADER = {
    "kpop_idols": ["stage_name", "full_name", "korean_name", "korean_stage_name", "date_of_birth", "groupname", "country", "height", "weight", "birthplace", "gender", "instagram"],
    "kpop_song_rankings": ["year", "time", "rank", "song_title", "artist", "album"]
}

TABLES_HEADER_WITH_TYPE = {
    "kpop_idols": {"stage_name": "TEXT", "full_name": "TEXT", "korean_name": "TEXT", "korean_stage_name": "TEXT", "date_of_birth": "TEXT", "groupname": "TEXT", "country": "TEXT", "height": "INT", "weight": "INT", "birthplace": "TEXT", "gender": "TEXT", "instagram": "TEXT"},
    "kpop_song_rankings": {"year": "INT", "time": "INT", "rank": "INT", "song_title": "TEXT", "artist": "TEXT", "album": "TEXT"}
}

NUMERIC_COLS = ["height", "weight", "year", "rank", "time"]