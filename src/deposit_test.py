import re
import numpy as np
import pandas as pd
from datetime import datetime


def main(file_path: str = 'bkrldc.txt'):
    df, data_dt = _get_deposit_data(file_path)
    df = _process_raw_df(df, data_dt)
    return df


def _get_deposit_data(file_path: str = 'bkrldc.txt'):
    with open(file_path, 'r', encoding='big5') as f:
        data = f.readlines()
    data_dt = roc2ad(find_date(data[2]), sep='/')
    df = []
    columns = ['異動識別碼(異動別)', '牌告利率名稱', '存期', '額度', '生效日期', '固定', '機動', '銀行']
    current_bank = ''
    for line in data[7:]:
        if "-----" in line:
            print('end')
            break
        line = line.replace('\u3000', ' ').replace('\n', ' ').strip()
        row = [t for t in line.split(' ') if t != '']
        if "無實體" in line:
            row = row[0:2] + [''] + row[2:]
        if len(row) < 3:
            current_bank = line
            print(line)
            continue
        record = {k: v for k, v in zip(columns[:len(row)], row)}
        record['銀行'] = current_bank
        df.append(record)
    df = pd.DataFrame.from_records(df)
    return df, data_dt


def _process_raw_df(df: pd.DataFrame, data_dt: datetime.date):
    df[['異動識別碼', '異動別']] = df['異動識別碼(異動別)'].str.split('(', expand=True)
    df[['銀行代碼', '銀行名稱']] = df['銀行'].str.split(' ', expand=True)
    df['存期'] = df['存期'].apply(lambda x: x.translate(str.maketrans('１２３４５６７８９０', '1234567890')))
    df['額度'] = df['額度'].apply(lambda x: x.translate(str.maketrans('１２３４５６７８９０', '1234567890')))
    # df['額度'] = df['額度'].apply(lambda x: chinese_to_int(x))  # [TODO]
    df['生效日期'] = df['生效日期'].apply(lambda x: roc2ad(x))
    df['異動別'] = df['異動別'].str.replace(')', '')  # Remove the closing parenthesis
    df['資料日期'] = data_dt
    cols = ['資料日期', '異動識別碼', '異動別', '銀行代碼', '銀行名稱', '牌告利率名稱', '存期', '額度', '生效日期', '固定', '機動']
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


def chinese_to_int(chinese_num: str):
    """Converts a Chinese number string to an integer.
    Args:
        chinese_num (str): The Chinese number string.
    Returns:
        int: The corresponding integer value, or np.nan if the string is '一般'.
    """
    if chinese_num == '一般':
        return np.nan
    # Create a dictionary mapping Chinese characters to their corresponding multipliers.
    multipliers = {
        '億': 100000000,
        '仟萬': 10000000,
        '佰萬': 1000000,
        '萬': 10000,
        '仟': 1000,
        '佰': 100,
        '十': 10
    }
    # Initialize the result to 0.
    result = 0
    # Iterate over each character in the Chinese number string.
    for i in range(len(chinese_num)):
        # If the current character is a multiplier, add it to the result.
        if chinese_num[i] in multipliers:
            result += int(chinese_num[i-1]) * multipliers[chinese_num[i]]
        # Otherwise, the current character is a digit, so add it to the result.
        else:
            result += int(chinese_num[i])

    return result