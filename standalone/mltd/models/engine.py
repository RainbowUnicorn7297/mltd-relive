import time

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine

from mltd.servers.logging import logger

engine = create_engine('sqlite+pysqlite:///mltd-relive.db')


@event.listens_for(Engine, 'connect')
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute('PRAGMA foreign_keys=ON')
    cursor.close()


@event.listens_for(Engine, 'before_cursor_execute')
def before_cursor_execute(conn, cursor, statement,
                          parameters, context, executemany):
    conn.info.setdefault('query_start_time', []).append(time.perf_counter_ns())
    logger.debug(f'Start query: {statement}')
    logger.debug(f'Parameters: {parameters}')


@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement,
                         parameters, context, executemany):
    total_ns = time.perf_counter_ns() - conn.info['query_start_time'].pop(-1)
    logger.debug('Query complete!')
    logger.debug(f'Query execution time: {total_ns // 1_000_000} ms')

