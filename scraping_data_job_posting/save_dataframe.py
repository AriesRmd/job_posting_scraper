import os
import pandas as pd
from datetime import datetime

def save_csv_with_timestamp(df, folder='data', prefix='data'):
    os.makedirs(folder, exist_ok=True)
    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M')
    filename = f"{prefix}_{timestamp}.csv"
    filepath = os.path.join(folder, filename)
    df.to_csv(filepath,sep=';', index=False, encoding='utf-8')
    print(f"Data saved to {filepath}")
