"""
This script aims to query the txt data from the cdc of Taiwan and transform the data into table format.
"""
import os
import logging
import requests
import numpy as np
import pandas as pd
from datetime import datetime
from src.utils import CWD, TODAY
from src.utils import roc2ad, find_date, chinese_to_arabic


def main(url: str = 'https://www.cbc.gov.tw/tw/public/Data/bkrldc.txt', filename: str = 'bkrldc'):
    # create save data path
    os.makedirs(os.path.join(CWD, 'data', 'tables'), exist_ok=True)
    os.makedirs(os.path.join(CWD, 'data', 'texts'), exist_ok=True)

    # fetch data
    file_path = os.path.join(CWD, 'data', 'texts', f'{filename}_{TODAY}.txt')
    _fetch_raw_text(url=url, file_path=file_path)

    # tranform to dataframe and process the dataframe
    df, data_dt = _get_deposit_data(file_path)
    df = _process_raw_df(df, data_dt)

    # save dataframe
    save_path = os.path.join(CWD, r'data', 'tables', f"{filename}_{data_dt}.csv")
    df.to_csv(save_path, index=False)
    return df


def _get_deposit_data(file_path: str):
    """
    text -> dataframe
    :returns
        df: transferred data
        data_dt: date of the data recorded in the file
    """
    with open(file_path, 'r', encoding='big5') as f:
        data = f.readlines()
    data_dt = roc2ad(find_date(data[2]), sep='/')
    df = []
    columns = ['異動識別碼(異動別)', '牌告利率名稱', '存期', '額度', '生效日期', '固定', '機動', '銀行']
    current_bank = ''
    for line in data[7:]:
        if "-----" in line:
            logging.info('finished to process all rows')
            break
        line = line.replace('\u3000', ' ').replace('\n', ' ').strip()
        row = [t for t in line.split(' ') if t != '']
        if "無實體" in line:
            row = row[0:2] + [''] + row[2:]
        if len(row) < 3:
            current_bank = line
            logging.info(f"{line}, starts processing.")
            continue
        record = {k: v for k, v in zip(columns[:len(row)], row)}
        record['銀行'] = current_bank
        df.append(record)
    df = pd.DataFrame.from_records(df)
    df[[col for col in columns if col not in df.columns]] = np.nan  # fill not existing columns
    return df, data_dt


def _process_raw_df(df: pd.DataFrame, data_dt: datetime.date):
    """
    process dataframe to a more understandable version
    :param df: raw dataframe to be processed
    :param data_dt: date of the data
    :return: processed dataframe
    """
    df[['異動識別碼', '異動別']] = df['異動識別碼(異動別)'].str.split('(', expand=True)
    df[['銀行代碼', '銀行名稱']] = df['銀行'].str.split(' ', expand=True)
    df['存期'] = df['存期'].apply(lambda x: x.translate(str.maketrans('１２３４５６７８９０', '1234567890')))
    df['額度'] = df['額度'].apply(lambda x: x.translate(str.maketrans('１２３４５６７８９０', '1234567890')))
    df['amounts'] = df['額度'].apply(lambda x: chinese_to_arabic(x))  # [TODO]
    df['生效日期'] = df['生效日期'].apply(lambda x: roc2ad(x))
    df['異動別'] = df['異動別'].str.replace(')', '')  # Remove the closing parenthesis
    df['資料日期'] = data_dt
    cols = [
        '資料日期', '異動識別碼', '異動別', '銀行代碼', '銀行名稱',
        '牌告利率名稱', '存期', '額度', 'amounts', '生效日期', '固定', '機動']
    df = df[cols]
    return df


def _fetch_raw_text(url: str, file_path):
    """
    fetch raw text from the webpage
    """
    # url = 'https://www.cbc.gov.tw/tw/public/Data/bkrldc.txt'
    response = requests.get(url)

    # Save the content to a file
    with open(file_path, 'wb') as file:
        file.write(response.content)

    logging.info(f"File downloaded and saved as {file_path}")
