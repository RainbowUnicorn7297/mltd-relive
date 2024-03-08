import argparse
import os
import sys
import time
from logging import StreamHandler
from multiprocessing import Process, set_start_method

from mltd.models.setup import (check_database_version, cleanup, setup,
                               upgrade_database)
from mltd.servers import api_server
from mltd.servers.config import config, server_language
from mltd.servers.logging import formatter, handler, logger

stream_handler = StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


def start_server(reset=False):
    if reset or not os.path.isfile('mltd-relive.db'):
        reset_data()
    upgrade_database()

    handler.doRollover()
    logger.info(f'Starting server...')
    api_process = Process(target=api_server.start, daemon=True)
    api_process.start()

    time.sleep(2)
    logger.info(f'Server started.')
    api_process.join()


def reset_data():
    if os.path.isfile('mltd-relive.db'):
        check_database_version()
        decision = input('Database already exists. Reset all data? [Y/N] ')
        if decision.upper() != 'Y':
            exit()
        cleanup()
        logger.info('Dropped all tables.')

    handler.doRollover()
    setup()


def change_language(language):
    global server_language
    config.set_config('language', language)
    server_language = language


if __name__ == '__main__':
    set_start_method('spawn')

    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--language', choices=['zh', 'ko'],
                        help='game client language')
    parser.add_argument('-r', '--reset', action='store_true',
                        help='reset data')
    args = parser.parse_args()

    config.set_config('is_local', True)
    if args.language:
        change_language(args.language)
    start_server(args.reset)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass

