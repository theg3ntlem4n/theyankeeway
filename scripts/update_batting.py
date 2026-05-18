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
        "pos=all&stats=bat&lg=all&qual=0&type=8&season=2026&month=0"
        "&season1=2026&ind=0&team=0&pageitems=2000&csv=1"

)

print("Downloading batting data...")

df = pd.read_csv(url)

df["pull_date"] = datetime.utcnow()

print(df.head())

os.makedirs("data/raw", exist_ok = True)

df.to_csv("data/raw/mlb_batting.csv", index=False)

df.to_sql("mlb_batting_daily", engine, if_exists="append", index=False)

print("Batting data uploaded successfully")
