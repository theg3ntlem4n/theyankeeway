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

CURRENT_SEASON = 2026

print("Pulling current season update...")

df = batting_stats(CURRENT_SEASON, qual=0)

df.columns = df.columns.str.lower()

df = df.assign(
    season=CURRENT_SEASON,
    pull_date=datetime.utcnow()
)

df = df.rename(columns={
    "idfg": "playerid",
    "name": "name",
    "team": "team"
})

df.to_sql(
    "player_season_stats",
    engine,
    if_exists="append",
    index=False,
    chunksize=2000,
    method="multi"
)

print("DAILY UPDATE COMPLETE")
