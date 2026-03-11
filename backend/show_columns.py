import sqlite3
from pathlib import Path
path = Path('data/app.db') if Path('data/app.db').exists() else Path('app.db')
print('DB path', path)
conn = sqlite3.connect(path)
c = conn.cursor()
c.execute("PRAGMA table_info(flows)")
for row in c.fetchall():
    print(row)
