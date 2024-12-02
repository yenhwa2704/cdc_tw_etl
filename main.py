"""entry point"""
import logging
from src.bkrldc_process import main

logging.basicConfig(
    filename='bkrldc.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


if __name__ == '__main__':
    df = main()
    logging.info('\n')
