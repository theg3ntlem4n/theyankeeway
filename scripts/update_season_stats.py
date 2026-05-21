import socket

_original_getaddrinfo = socket.getaddrinfo

def ipv4_only(*args, **kwargs):
    kwargs["family"] = socket.AF_INET
    return _original_getaddrinfo(*args, **kwargs)

socket.getaddrinfo = ipv4_only

import pandas as pd
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

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300
)
# =========================
# CONFIG
# =========================
START_YEAR = 2008
END_YEAR = 2026

all_frames = []

# =========================
# PULL DATA
# =========================
for season in range(START_YEAR, END_YEAR + 1):

    print(f"Pulling season stats for {season}")

    try:

        df = batting_stats(season, qual=0)

        if df.empty:
            continue

        # normalize columns
        df.columns = (
            df.columns
            .str.lower()
            .str.replace("%", "pct")
            .str.replace("+", "_plus")
            .str.replace("-", "_")
            .str.replace(" ", "_")
        )

        # standardize
        df = df.rename(columns={
            "idfg": "playerid",
            "name": "name",
            "team": "team"
        })

        df = df.assign(
            season=season,
            pull_date=datetime.utcnow()
        )

        all_frames.append(df)

    except Exception as e:
        print(f"FAILED {season}: {e}")

# =========================
# CONCAT
# =========================
if len(all_frames) == 0:
    raise ValueError("No season data pulled")

final_df = pd.concat(all_frames, ignore_index=True)

# =========================
# SAVE
# =========================
final_df.to_sql(
    "player_season_stats",
    engine,
    if_exists="replace",
    index=False,
    chunksize=1000,
    method="multi"
)

print("Season stats upload complete")
