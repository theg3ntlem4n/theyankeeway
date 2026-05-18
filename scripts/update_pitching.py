import pandas as pd
}

season = 2026
pull_date = datetime.utcnow()

all_frames = []

for name, t in STAT_TYPES.items():
    print(f"Downloading pitching dataset: {name}")

    url = (
        f"{BASE_URL}?pos=all&stats=pit&lg=all&qual=0"
        f"&type={t}&season={season}&season1={season}"
        f"&ind=0&team=0&pageitems=2000&csv=1"
    )

    df = pd.read_csv(url)
    df["stat_type"] = name
    df["pull_date"] = pull_date

    all_frames.append(df)

final_df = pd.concat(all_frames, ignore_index=True)

# cleanup
final_df = final_df.loc[:, ~final_df.columns.duplicated()]
final_df.columns = [c.lower().replace('%', 'pct') for c in final_df.columns]

os.makedirs("data/raw", exist_ok=True)
final_df.to_csv("data/raw/mlb_pitching_all_stats.csv", index=False)

final_df.to_sql(
    "mlb_pitching_daily_all",
    engine,
    if_exists="append",
    index=False
)

print("Expanded pitching dataset uploaded successfully")
```python
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

url = (
    "https://www.fangraphs.com/leaders.aspx?"
    "pos=all&stats=pit&lg=all&qual=0&type=8&season=2026&month=0"
    "&season1=2026&ind=0&team=0&pageitems=2000&csv=1"
)

print("Downloading pitching data...")

df = pd.read_csv(url)

df["pull_date"] = datetime.utcnow()

os.makedirs("data/raw", exist_ok=True)

df.to_csv("data/raw/mlb_pitching.csv", index=False)

df.to_sql(
    "mlb_pitching_daily",
    engine,
    if_exists="append",
    index=False
)

print("Pitching data uploaded successfully")
