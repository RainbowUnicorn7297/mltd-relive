import sqlite3

conn = sqlite3.connect('../mltd.db')
conn.row_factory = sqlite3.Row
