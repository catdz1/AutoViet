from database import get_conn

# Kiem tra ten bang
conn = get_conn()
tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print("Cac bang trong DB:")
for t in tables:
    print(" -", t[0])

# Kiem tra cot bang khach_hang
print("\nCot bang khach_hang:")
cols = conn.execute("PRAGMA table_info(khach_hang)").fetchall()
for c in cols:
    print(" -", c[1])

# Kiem tra cot bang xe
print("\nCot bang xe:")
cols = conn.execute("PRAGMA table_info(xe)").fetchall()
for c in cols:
    print(" -", c[1])

conn.close()