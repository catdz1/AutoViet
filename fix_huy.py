import sqlite3

conn = sqlite3.connect("dealership.db")   # sửa lại đường dẫn nếu file DB không cùng thư mục
cur = conn.execute(
    "UPDATE don_hang SET trang_thai_tt='Huỷ' WHERE trang_thai='Huỷ' AND trang_thai_tt != 'Huỷ'"
)
conn.commit()
print(f"Đã đồng bộ {cur.rowcount} đơn hàng.")
conn.close()