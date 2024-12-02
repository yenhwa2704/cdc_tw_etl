"""
This script stores the functions that may be used in other cases
such as processing date and numeric format
"""
import os
import re
import logging
from datetime import datetime

CWD = os.getcwd()
TODAY = datetime.now().date()


def exception_handler(func):
    def wrapper(*args, **kwargs):
        try:
            output = func(*args, **kwargs)
            logging.info(f"successfully execute the function: {func.__name__}")
            return output
        except Exception as e:
            logging.error(f"Exception occurred in {func.__name__}: {str(e)}", exc_info=True)
            print(f"An error occurred: {e}")
            raise
    return wrapper


def roc2ad(date_str: str, sep: str = '.'):
    """
    transfer ROC date string to a generalised date format
    :param date_str: ROC format date string (113.01.01, 105-03-04)
    :param sep: 'the char to separate y, m, d'
    :return: datetime.date
    """
    y, m, d = [int(i) for i in date_str.split(sep)]
    return datetime(y + 1911, m, d).date()


def find_date(text: str):
    """
    find the ROC date string in a string and return the string
    """
    pattern = r'\d{3}/\d{2}/\d{2}'
    match = re.search(pattern, text)

    if match:
        found_date = match.group()
        return found_date
    else:
        raise ValueError('cannot find the date')


def chinese_to_arabic(s):
    """
    transfer chinese to arabic numbers
    """
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

    if not bool(re.search(r'\d', s)):
        raise ValueError('there is no number in the string')

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
