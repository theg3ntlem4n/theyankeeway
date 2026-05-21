import pandas as pd
from pybaseball import batting_stats
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300
)

START_YEAR = 2008
END_YEAR = 2026

all_frames = []

for year in range(START_YEAR, END_YEAR + 1):
    print(f"Pulling {year}")

    try:
        df = batting_stats(year, qual=0)

        if df is None or df.empty:
            continue

        df.columns = df.columns.str.lower()

        df = df.assign(
            season=year,
            pull_date=datetime.utcnow()
        )

        all_frames.append(df)

    except Exception as e:
        print(f"FAILED {year}: {e}")

if not all_frames:
    raise ValueError("No data pulled")

final_df = pd.concat(all_frames, ignore_index=True)

# ensure expected columns exist
rename_map = {
    "idfg": "playerid",
    "name": "name",
    "team": "team"
}

final_df = final_df.rename(columns=rename_map)

final_df.to_sql(
    "player_season_stats",
    engine,
    if_exists="replace",
    index=False,
    chunksize=2000,
    method="multi"
)

print("BACKFILL COMPLETE")
