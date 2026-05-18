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

# =========================
# CLEAN COLUMN NAMES
# =========================
df.columns = (
    df.columns
    .str.lower()
    .str.replace("%", "pct")
    .str.replace(" ", "_")
)

# =========================
# FIX FAN GRAPHS INCONSISTENCIES
# =========================
rename_map = {}

if "date" in df.columns:
    rename_map["date"] = "game_date"

if "gamedate" in df.columns:
    rename_map["gamedate"] = "game_date"

if "player_id" in df.columns:
    rename_map["player_id"] = "playerid"

df = df.rename(columns=rename_map)

# =========================
# VALIDATION (prevents crash)
# =========================
required_cols = ["playerid", "game_date"]

missing = [c for c in required_cols if c not in df.columns]
if missing:
    raise ValueError(
        f"Missing columns {missing}. Available: {df.columns.tolist()}"
    )

# =========================
# SAFE ADDITIONS (NO FRAGMENTATION)
# =========================
df = df.assign(
    season=CURRENT_SEASON,
    pull_date=datetime.utcnow()
)

df = df.dropna(subset=["playerid", "game_date"])

# =========================
# UPSERT PREP
# =========================
records = df.to_dict(orient="records")

stmt = insert("player_game_logs").values(records)

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

print("Game logs updated successfully")
