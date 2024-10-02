import os
from src.deposit_test import main, CWD
from src.deposit_test import chinese_to_arabic

if __name__ == '__main__':
    # test_case = [
    #     '1億5仟萬', '1億1仟萬', '5仟萬', '3仟5佰萬', '3仟6佰萬', '5仟1佰萬', '5仟5佰萬',
    #     '5仟6佰萬', '2億1仟萬', '7仟5佰萬', '7仟6佰萬', '4億2仟萬', '4億3仟萬', '3仟萬',
    #     '3仟1佰萬', '3仟4佰萬', '5億1仟萬']
    # [print(t, chinese_to_arabic[t]) for t in test_case]
    df = main()
    print('')
