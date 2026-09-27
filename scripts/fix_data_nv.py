import sqlite3

conn = sqlite3.connect('dealership.db')

# 1. Them NGUYEN THU HUYEN vao nhan_vien
conn.execute(
    "INSERT OR IGNORE INTO nhan_vien(ma_nv, ho_ten, chuc_vu, trang_thai) "
    "VALUES('NV008', 'NGUYỄN THU HUYỀN', 'Nhân viên', 'Đang làm')"
)

# 2. Them TRAN BICH PHUONG vao nhan_vien
conn.execute(
    "INSERT OR IGNORE INTO nhan_vien(ma_nv, ho_ten, chuc_vu, trang_thai) "
    "VALUES('NV009', 'TRẦN BÍCH PHƯỢNG', 'Nhân viên', 'Đang làm')"
)

# 3. Lien ket user thuhuyen -> NV008
conn.execute(
    "UPDATE users SET nv_id=(SELECT id FROM nhan_vien WHERE ma_nv='NV008') "
    "WHERE username='thuhuyen'"
)

# 4. Lien ket user bichphuong -> NV009
conn.execute(
    "UPDATE users SET nv_id=(SELECT id FROM nhan_vien WHERE ma_nv='NV009') "
    "WHERE username='bichphuong'"
)

conn.commit()

# Kiem tra lai
print("=== KET QUA ===")
rows = conn.execute(
    "SELECT u.username, u.ho_ten, u.nv_id, nv.ma_nv "
    "FROM users u LEFT JOIN nhan_vien nv ON u.nv_id=nv.id "
    "WHERE u.username IN ('thuhuyen','bichphuong')"
).fetchall()
for r in rows:
    print(f"  username={r[0]} | ho_ten={r[1]} | nv_id={r[2]} | ma_nv={r[3]}")

conn.close()
print("\nXONG! Tat app va mo lai, dang nhap thuhuyen se cham cong duoc!")