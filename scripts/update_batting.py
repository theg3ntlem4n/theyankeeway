import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import insert
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))

BASE_URL = "https://www.fangraphs.com/statsd.aspx"

CURRENT_SEASON = 2026

print(f"Pulling game logs {CURRENT_SEASON}")

url = (
    f"{BASE_URL}?playerid=&position=all&season={CURRENT_SEASON}"
    "&stat=bat&split=game&team=0&league=0&csv=1"
)

df = pd.read_csv(url)

df.columns = [c.lower().replace("%", "pct") for c in df.columns]

df["season"] = CURRENT_SEASON
df["pull_date"] = datetime.utcnow()

# -----------------------------
# CLEAN REQUIRED KEYS
# -----------------------------
# ensure these exist in dataset
df = df.dropna(subset=["playerid", "game_date"])

records = df.to_dict(orient="records")

table = "player_game_logs"

stmt = insert(table).values(records)

update_cols = {
    col.name: col
    for col in stmt.excluded
    if col.name not in ["playerid", "game_date"]
}

stmt = stmt.on_conflict_do_update(
    index_elements=["playerid", "game_date"],
    set_=update_cols
)

with engine.begin() as conn:
    conn.execute(stmt)

print("Game logs upsert complete (no duplicates)")
