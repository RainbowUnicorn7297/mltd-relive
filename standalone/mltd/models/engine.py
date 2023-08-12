from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine

engine = create_engine('sqlite+pysqlite:///mltd-relive.db')


@event.listens_for(Engine, 'connect')
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute('PRAGMA foreign_keys=ON')
    cursor.close()

