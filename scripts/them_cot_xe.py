"""
Chạy file này 1 lần để thêm cột mới vào bảng xe
"""
import sqlite3, os
db_path = os.path.join(os.path.dirname(__file__), "dealership.db")
conn = sqlite3.connect(db_path)
try:
    conn.execute("ALTER TABLE xe ADD COLUMN noi_bat INTEGER DEFAULT 0")
    print("✅ Thêm cột noi_bat thành công")
except: print("⚠️ Cột noi_bat đã tồn tại")
try:
    conn.execute("ALTER TABLE xe ADD COLUMN giam_gia REAL DEFAULT 0")
    print("✅ Thêm cột giam_gia thành công")
except: print("⚠️ Cột giam_gia đã tồn tại")
try:
    conn.execute("ALTER TABLE xe ADD COLUMN ngay_nhap TEXT")
    print("✅ Thêm cột ngay_nhap thành công")
except: print("⚠️ Cột ngay_nhap đã tồn tại")

# Cập nhật ngày nhập mặc định cho xe hiện có
conn.execute("""UPDATE xe SET ngay_nhap = date('now') WHERE ngay_nhap IS NULL""")

# Đánh dấu 3 xe nổi bật mặc định
conn.execute("UPDATE xe SET noi_bat=1 WHERE id IN (SELECT id FROM xe ORDER BY gia_ban DESC LIMIT 3)")

# Đánh dấu 2 xe giảm giá mẫu
conn.execute("UPDATE xe SET giam_gia=10 WHERE id IN (SELECT id FROM xe ORDER BY id LIMIT 2)")

conn.commit(); conn.close()
print("✅ Xong! Chạy lại main.py")