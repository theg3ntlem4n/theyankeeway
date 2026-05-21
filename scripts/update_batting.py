import socket

_original_getaddrinfo = socket.getaddrinfo

def ipv4_only(*args, **kwargs):
    kwargs["family"] = socket.AF_INET
    return _original_getaddrinfo(*args, **kwargs)

socket.getaddrinfo = ipv4_only

import pandas as pd
from pybaseball import batting_stats_bref
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

        df = batting_stats_bref(season)

        if df.empty:
            print(f"No data for {season}")
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

        # add season + timestamp safely
        df = df.assign(
            season=season,
            pull_date=datetime.utcnow()
        )

        all_frames.append(df)

    except Exception as e:
        print(f"FAILED {season}: {e}")

# =========================
# VALIDATE
# =========================
if len(all_frames) == 0:
    raise ValueError("No data pulled")

# =========================
# CONCAT
# =========================
final_df = pd.concat(all_frames, ignore_index=True)

# =========================
# OPTIONAL COLUMN CLEANUP
# =========================
if "name" not in final_df.columns:
    raise ValueError("Name column missing")

# create stable player id if needed
if "playerid" not in final_df.columns:

    final_df["playerid"] = (
        final_df["name"]
        .str.lower()
        .str.replace(" ", "_")
    )

# =========================
# SAVE TO SUPABASE
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
