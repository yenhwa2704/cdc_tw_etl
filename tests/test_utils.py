import pytest
from datetime import datetime
from src.utils import chinese_to_arabic
from src.utils import find_date, roc2ad


def test_chinese_to_arabic():
    assert chinese_to_arabic('1億') == 100000000
    assert chinese_to_arabic('26億') == 2600000000
    assert chinese_to_arabic('5仟萬') == 50000000
    assert chinese_to_arabic('2億1仟萬') == 210000000
    assert chinese_to_arabic('5仟6佰萬') == 56000000
    assert chinese_to_arabic('1億5仟6佰萬') == 156000000


def test_chinese_to_arabic_error():
    with pytest.raises(ValueError):
        chinese_to_arabic('abc')
    with pytest.raises(ValueError):
        chinese_to_arabic('億萬')


def test_roc2ad():
    assert roc2ad('113.12.01') == datetime(2024, 12, 1).date()
    assert roc2ad('113/04/01', sep='/') == datetime(2024, 4, 1).date()
    with pytest.raises(ValueError):
        roc2ad('億萬')


def test_find_date():
    assert find_date('uin2o113/01/05ioewjr') == '113/01/05'
    with pytest.raises(ValueError):
        find_date('億萬')
