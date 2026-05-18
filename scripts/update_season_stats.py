import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import insert
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))

BASE_URL = "https://www.fangraphs.com/leaders.aspx"

# =========================
# CONFIG
# =========================
START_YEAR = 2000
END_YEAR = 2026

all_frames = []

for season in range(START_YEAR, END_YEAR + 1):
    print(f"Pulling season {season}")

    url = (
        f"{BASE_URL}?pos=all&stats=bat&lg=all&qual=0"
        f"&type=8&season={season}&season1={season}"
        f"&ind=0&team=0&pageitems=2000&csv=1"
    )

    df = pd.read_csv(url)
    df["season"] = season

    all_frames.append(df)

df = pd.concat(all_frames, ignore_index=True)

# =========================
# CLEAN + NORMALIZE
# =========================
df.columns = (
    df.columns
    .str.lower()
    .str.replace("%", "pct")
    .str.replace(" ", "_")
)

df = df.assign(pull_date=datetime.utcnow())

# =========================
# REQUIRED COLUMN SAFETY
# =========================
required = ["playerid", "name", "team", "season"]
for col in required:
    if col not in df.columns:
        raise ValueError(f"Missing required column: {col}")

# =========================
# UPSERT
# =========================
records = df.to_dict(orient="records")

stmt = insert("player_season_stats").values(records)

update_cols = {
    col.name: col
    for col in stmt.excluded
    if col.name not in ["playerid", "season"]
}

stmt = stmt.on_conflict_do_update(
    index_elements=["playerid", "season"],
    set_=update_cols
)

with engine.begin() as conn:
    conn.execute(stmt)

print("Season stats updated successfully")
