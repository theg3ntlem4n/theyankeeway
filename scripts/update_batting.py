import pandas as pd

    df = pd.read_csv(url)
    df["stat_type"] = name
    df["pull_date"] = pull_date

    all_frames.append(df)

# Combine all stat views into one table (long format)
final_df = pd.concat(all_frames, ignore_index=True)

# Basic cleanup
final_df = final_df.loc[:, ~final_df.columns.duplicated()]
final_df.columns = [c.lower().replace('%', 'pct') for c in final_df.columns]

# Save locally
os.makedirs("data/raw", exist_ok=True)
final_df.to_csv("data/raw/mlb_batting_all_stats.csv", index=False)

# Upload to database
final_df.to_sql(
    "mlb_batting_daily_all",
    engine,
    if_exists="append",
    index=False
)

print("Expanded batting dataset uploaded successfully")
```python
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

# Fangraphs export endpoint
url = (
    "https://www.fangraphs.com/leaders.aspx?"
    "pos=all&stats=bat&lg=all&qual=0&type=8&season=2026&month=0"
    "&season1=2026&ind=0&team=0&pageitems=2000&csv=1"
)

print("Downloading batting data...")

df = pd.read_csv(url)

df["pull_date"] = datetime.utcnow()

print(df.head())

# Save locally
os.makedirs("data/raw", exist_ok=True)

df.to_csv("data/raw/mlb_batting.csv", index=False)

# Upload to database

df.to_sql(
    "mlb_batting_daily",
    engine,
    if_exists="append",
    index=False
)

print("Batting data uploaded successfully")
