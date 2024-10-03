import os
import re
import logging
import requests
import numpy as np
import pandas as pd
from datetime import datetime

CWD = os.getcwd()
today = datetime.now().date()


def main(url: str = 'https://www.cbc.gov.tw/tw/public/Data/bkrldc.txt', filename: str = 'bkrldc'):
    # create save data path
    os.makedirs(os.path.join(CWD, 'data', 'tables'), exist_ok=True)
    os.makedirs(os.path.join(CWD, 'data', 'texts'), exist_ok=True)

    # fetch data
    file_path = os.path.join(CWD, 'data', 'texts', f'{filename}_{today}.txt')
    fetch_raw_text(url=url, file_path=file_path)

    # tranform to dataframe and process the dataframe
    df, data_dt = _get_deposit_data(file_path)
    df = _process_raw_df(df, data_dt)

    # save dataframe
    save_path = os.path.join(CWD, r'data', 'tables', f"{filename}_{data_dt}.csv")
    df.to_csv(save_path, index=False)
    return df


def _get_deposit_data(file_path: str):
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


def roc2ad(date_str: str, sep: str = '.'):
    y, m, d = [int(i) for i in date_str.split(sep)]
    return datetime(y + 1911, m, d).date()


def find_date(text: str):
    pattern = r'\d{3}/\d{2}/\d{2}'
    match = re.search(pattern, text)

    if match:
        found_date = match.group()
        return found_date
    else:
        raise ValueError('cannot find the date')


def chinese_to_arabic(s):
    units = {'億': 100000000, '萬': 10000, '仟': 1000, '佰': 100, '拾': 10}

    def parse_part(part):
        part_num = 0
        num = ''
        for char in part:
            if char.isdigit():
                num += char
            elif char in units:
                num = int(num)
                part_num += num * units[char]
                num = ''
            else:
                raise ValueError(f"unknown char: {char}")
        num = 0 if num == '' else int(num)
        part_num += num
        return part_num

    total = 0
    if '億' in s:
        parts = s.split('億')
        total += parse_part(parts[0]) * units['億']
        s = '億'.join(parts[1:])
    if '萬' in s:
        parts = s.split('萬')
        total += parse_part(parts[0]) * units['萬']
        s = '萬'.join(parts[1:])
    total += parse_part(s)
    return total


def fetch_raw_text(url: str, file_path):
    # url = 'https://www.cbc.gov.tw/tw/public/Data/bkrldc.txt'
    response = requests.get(url)

    # Save the content to a file
    with open(file_path, 'wb') as file:
        file.write(response.content)

    logging.info(f"File downloaded and saved as {file_path}")
