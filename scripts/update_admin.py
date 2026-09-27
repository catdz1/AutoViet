import hashlib
from database import get_conn

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

conn = get_conn()

# Xem tất cả tài khoản hiện có
rows = conn.execute("SELECT id, username, role FROM users").fetchall()
print("Danh sach tai khoan hien co:")
for r in rows:
    print(f"  id={r[0]} username={r[1]} role={r[2]}")

# Xoá tất cả tài khoản ngoquoctuan không phải admin
conn.execute("DELETE FROM users WHERE username='ngoquoctuan' AND role!='admin'")

# Đổi admin (dù username hiện tại là gì)
admin = conn.execute("SELECT id FROM users WHERE role='admin' LIMIT 1").fetchone()
if admin:
    conn.execute(
        "UPDATE users SET username='ngoquoctuan', password=?, ho_ten='Ngo Quoc Tuan' WHERE id=?",
        (hash_pw("123456"), admin[0])
    )
    conn.commit()
    print("\nOK! Da doi tai khoan admin:")
    print("  Username : ngoquoctuan")
    print("  Mat khau : 123456")
else:
    print("Khong tim thay tai khoan admin!")

conn.close()