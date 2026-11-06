# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("./backend"))
from backend.database import get_connection

for db_path in ["backend/licenses.db", "deploy_vercel/backend/licenses.db"]:
    if os.path.isfile(db_path):
        conn = get_connection(db_path)
        c = conn.cursor()
        c.execute("DELETE FROM admin_users WHERE username != 'admin'")
        conn.commit()
        c.execute("SELECT username, role FROM admin_users")
        print(f"{db_path}: {c.fetchall()}")
        conn.close()
