import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))

BASE_URL = "https://www.fangraphs.com/leaders.aspx"

seasons = range(2000, 2027)

all_frames = []

for season in seasons:
    print(f"Pulling season {season}")

    url = (
        f"{BASE_URL}?pos=all&stats=bat&lg=all&qual=0"
        f"&type=8&season={season}&season1={season}"
        f"&ind=0&team=0&pageitems=2000&csv=1"
    )

    df = pd.read_csv(url)
    df["season"] = season

    all_frames.append(df)

final_df = pd.concat(all_frames, ignore_index=True)

final_df.columns = [c.lower().replace("%", "pct") for c in final_df.columns]

final_df["pull_date"] = datetime.utcnow()

final_df.to_sql(
    "player_season_stats",
    engine,
    if_exists="append",
    index=False
)

print("Season stats loaded (2000-present)")
