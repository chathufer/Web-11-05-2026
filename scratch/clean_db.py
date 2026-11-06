# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("./backend"))
from backend.database import get_connection

conn = get_connection()
c = conn.cursor()
c.execute("DELETE FROM licenses WHERE customer_name LIKE '%Official Buyer%' OR customer_name LIKE '%Trial User (TestPC)%'")
c.execute("DELETE FROM activations WHERE hwid LIKE '%TEST%' OR hwid LIKE '%DEBUG%'")
c.execute("DELETE FROM trial_claims WHERE hwid LIKE '%TEST%' OR hwid LIKE '%DEBUG%'")
conn.commit()

c.execute("SELECT COUNT(*) FROM licenses")
lic_count = c.fetchone()[0]
c.execute("SELECT COUNT(*) FROM activations")
act_count = c.fetchone()[0]
c.execute("SELECT COUNT(*) FROM trial_claims")
tc_count = c.fetchone()[0]
print(f"Cleaned licenses.db: {lic_count} licenses, {act_count} activations, {tc_count} trial claims")
conn.close()
