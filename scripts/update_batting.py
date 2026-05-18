import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))

BASE_URL = "https://www.fangraphs.com/statsd.aspx"

# Example: batting game logs endpoint pattern
# FanGraphs uses season + split=game log style

seasons = range(2000, 2027)

all_games = []

for season in seasons:
    print(f"Pulling game logs {season}")

    url = (
        f"{BASE_URL}?playerid=&position=all&season={season}"
        "&stat=bat&split=game&team=0&league=0&csv=1"
    )

    try:
        df = pd.read_csv(url)
        df["season"] = season
        all_games.append(df)
    except Exception as e:
        print(f"Failed season {season}: {e}")

final_df = pd.concat(all_games, ignore_index=True)

final_df.columns = [c.lower().replace("%", "pct") for c in final_df.columns]

final_df["pull_date"] = datetime.utcnow()

final_df.to_sql(
    "player_game_logs",
    engine,
    if_exists="append",
    index=False
)

print("Game logs loaded (2000-present)")
