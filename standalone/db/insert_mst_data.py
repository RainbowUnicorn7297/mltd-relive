from connection import conn
from os import listdir
import csv

def insert_mst_data(cursor, table_name):
    with open('mst_data/' + table_name + '.csv', newline='',
              encoding='utf-8') as f:
        reader = csv.DictReader(f)
        cursor.executemany(
            'insert into ' + table_name + ' values (' +
            ', '.join(':' + name for name in reader.fieldnames) + ')',
            reader
        )

if __name__ == "__main__":
    cursor = conn.cursor()
    for filename in listdir('mst_data'):
        if 'mst' in filename:
            table_name = filename.split('.')[0]
            insert_mst_data(cursor, table_name)
    conn.commit()
