# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("./backend"))
from backend.database import get_connection

conn = get_connection()
c = conn.cursor()
c.execute("SELECT * FROM license_history WHERE action LIKE '%ADMIN%' ORDER BY id DESC LIMIT 10")
rows = c.fetchall()
print(f"Total admin history rows: {len(rows)}")
for r in rows:
    print(dict(r))
conn.close()
