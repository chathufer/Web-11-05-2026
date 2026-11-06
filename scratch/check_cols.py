import sqlite3

conn = sqlite3.connect(r"backend\licenses.db")
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(licenses)")
cols = [c[1] for c in cursor.fetchall()]
print("Current columns in licenses:", cols)
conn.close()
