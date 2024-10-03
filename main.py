import os
from src.bkrldc_process import main, CWD
from src.bkrldc_process import chinese_to_arabic
from src.bkrldc_process import _get_deposit_data, _process_raw_df

if __name__ == '__main__':
    print(chinese_to_arabic('億萬'))
    df = main()
    print('')

