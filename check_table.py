import sqlite3

conn = sqlite3.connect("vlr.db")

cursor = conn.cursor()
cursor.execute("PRAGMA table_info(Player_map_stats)")

print(cursor.fetchall())

conn.close()