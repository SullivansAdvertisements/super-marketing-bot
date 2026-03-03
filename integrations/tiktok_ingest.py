import pandas as pd

def ingest_tiktok_creative_center_csv(file) -> pd.DataFrame:
    df = pd.read_csv(file)
    df.columns = [c.strip() for c in df.columns]
    return df
