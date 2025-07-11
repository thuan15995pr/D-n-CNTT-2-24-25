import os
from datetime import timedelta
from datetime import datetime
import pandas as pd


def convert_to_utc(time_str):
    if " EDT" in time_str:
        time_str_cleaned = time_str.replace(" EDT", "")
        offset = timedelta(hours=-4)
    elif " EST" in time_str:
        time_str_cleaned = time_str.replace(" EST", "")
        offset = timedelta(hours=-5)
    else:
        offset = timedelta(hours=0)
        time_str_cleaned = time_str

    formats = [
        '%B %d, %Y — %I:%M %p', 
        '%b %d, %Y %I:%M%p',  
        '%d-%b-%y',
        '%Y-%m-%d',
        '%Y/%m/%d',
        '%b %d, %Y'
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(time_str_cleaned, fmt)
            if fmt == '%d-%b-%y':
                offset = timedelta(hours=0)

            dt_utc = dt + offset

            return dt_utc.strftime('%Y-%m-%d %H:%M:%S UTC')
        except ValueError:
            continue

    return "Invalid date format"


def date_inte(folder_path, saving_path):
    csv_files = [file for file in os.listdir(folder_path) if file.endswith('.csv')]
    for csv_file in csv_files:
        print('Starting: ' + csv_file)
        file_path = os.path.join(folder_path, csv_file)
        df = pd.read_csv(file_path, on_bad_lines="warn")
        df.columns = df.columns.str.capitalize()
        if 'Datetime' in df.columns:
            df.rename(columns={'Datetime': 'Date'}, inplace=True)
        print(df["Date"])
        df['Date'] = df['Date'].apply(convert_to_utc)
        print(df["Date"])
        df['Date'] = pd.to_datetime(df['Date'], utc=True)
        df = df.sort_values(by='Date', ascending=False)
        print(df)

        df.to_csv(os.path.join(saving_path, csv_file), index=False)
        print('Done: ' + csv_file)


if __name__ == "__main__":
    news_folder_path = 'news_data_raw'
    news_saving_path = 'news_data_preprocessed'

    stock_folder_path = 'stock_price_data_raw'
    stock_saving_path = 'stock_price_data_preprocessed'

    date_inte(news_folder_path, news_saving_path)
    date_inte(stock_folder_path, stock_saving_path)

