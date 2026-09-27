"""
migrate_anh.py — Thêm cột anh_url vào bảng xe
Chạy 1 lần: python migrate_anh.py
"""
from database import get_conn
conn = get_conn()
try:
    conn.execute("ALTER TABLE xe ADD COLUMN anh_url TEXT DEFAULT ''")
    conn.commit()
    print("OK! Da them cot anh_url vao bang xe!")
except Exception as e:
    if "duplicate column" in str(e).lower():
        print("Cot anh_url da ton tai!")
    else:
        print(f"Loi: {e}")
conn.close()