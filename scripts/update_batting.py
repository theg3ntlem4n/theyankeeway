import pandas as pd
from pybaseball import statcast_batter
from pybaseball import batting_stats
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
from datetime import datetime

# =========================
# LOAD ENV
# =========================
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL missing")

engine = create_engine(DATABASE_URL)

START_YEAR = 2024
END_YEAR = 2026

all_frames = []

# =========================
# GET PLAYER IDS
# =========================
players = batting_stats(2026, qual=0)[["IDfg", "Name"]]

players.columns = ["playerid", "name"]

# =========================
# LOOP PLAYERS
# =========================
for _, row in players.iterrows():

    playerid = row["playerid"]
    name = row["name"]

    print(f"Pulling game logs for {name}")

    try:

        # statcast only supports MLBAM ids reliably
        # so this is placeholder workflow
        # later you should build ID crosswalk table

        continue

    except Exception as e:
        print(f"FAILED {name}: {e}")

# =========================
# SAVE
# =========================
if len(all_frames) > 0:

    final_df = pd.concat(all_frames, ignore_index=True)

    final_df.to_sql(
        "player_game_logs",
        engine,
        if_exists="replace",
        index=False,
        chunksize=1000,
        method="multi"
    )

print("Game logs upload complete")
