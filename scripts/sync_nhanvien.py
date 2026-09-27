"""
sync_nhanvien.py — Đồng bộ tài khoản NV vào bảng nhan_vien
Chạy 1 lần: python sync_nhanvien.py
"""
from database import get_conn
conn = get_conn()
c = conn.cursor()
users = c.execute("""
    SELECT id, ho_ten FROM users 
    WHERE role='nhanvien' AND status='approved' AND nv_id IS NULL
""").fetchall()

print(f"Tim thay {len(users)} tai khoan NV chua lien ket...")

for user_id, ho_ten in users:
    existing = c.execute(
        "SELECT id FROM nhan_vien WHERE ho_ten=?", (ho_ten,)
    ).fetchone()

    if existing:
        c.execute("UPDATE users SET nv_id=? WHERE id=?", (existing[0], user_id))
        print(f"  Lien ket: {ho_ten} -> NV id={existing[0]}")
    else:
        cnt = c.execute("SELECT COUNT(*) FROM nhan_vien").fetchone()[0]
        ma_nv = f"NV{cnt+1:03d}"
        while c.execute("SELECT id FROM nhan_vien WHERE ma_nv=?", (ma_nv,)).fetchone():
            cnt += 1; ma_nv = f"NV{cnt+1:03d}"

        c.execute("""
            INSERT INTO nhan_vien(ma_nv, ho_ten, chuc_vu, trang_thai)
            VALUES(?, ?, 'Nhan vien BH', 'Dang lam')
        """, (ma_nv, ho_ten))
        nv_id = c.lastrowid   # dùng cursor thay vì connection
        c.execute("UPDATE users SET nv_id=? WHERE id=?", (nv_id, user_id))
        print(f"  Tao moi: {ma_nv} — {ho_ten}")
conn.commit()
conn.close()
print("\nOK! Da dong bo xong!")