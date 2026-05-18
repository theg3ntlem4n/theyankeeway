import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import insert
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))

BASE_URL = "https://www.fangraphs.com/leaders.aspx"

CURRENT_SEASON = 2026  # change yearly OR automate later

print(f"Pulling season {CURRENT_SEASON}")

url = (
    f"{BASE_URL}?pos=all&stats=bat&lg=all&qual=0"
    f"&type=8&season={CURRENT_SEASON}&season1={CURRENT_SEASON}"
    f"&ind=0&team=0&pageitems=2000&csv=1"
)

df = pd.read_csv(url)

# Clean columns
df.columns = [c.lower().replace("%", "pct") for c in df.columns]

df["season"] = CURRENT_SEASON
df["pull_date"] = datetime.utcnow()

# -----------------------------
# UPSERT LOGIC (NO FRAGMENTATION)
# -----------------------------

records = df.to_dict(orient="records")

table = "player_season_stats"

stmt = insert(table).values(records)

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

print("Season stats upsert complete (no duplicates)")
