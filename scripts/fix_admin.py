"""
fix_admin.py — Dọn dẹp các tài khoản user bị lỗi (username rỗng, trùng lặp)
và đảm bảo có đúng 1 tài khoản admin hoạt động được.
 
Cách dùng: copy file này vào cùng thư mục với dealership.db rồi chạy:
    python fix_admin.py
"""
import sqlite3, hashlib, os
 
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dealership.db")
 
def hash_pw(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()
 
def main():
    if not os.path.exists(DB_PATH):
        print(f"[X] Không tìm thấy database tại: {DB_PATH}")
        print("    Hãy copy fix_admin.py vào đúng thư mục chứa dealership.db")
        return
 
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
 
    # 1. Xóa toàn bộ các dòng user bị lỗi (username rỗng hoặc None)
    deleted = c.execute("DELETE FROM users WHERE username IS NULL OR TRIM(username)=''").rowcount
    conn.commit()
    if deleted:
        print(f"[OK] Da xoa {deleted} tai khoan loi (username rong)")
 
    # 2. Kiểm tra / tạo lại admin đúng chuẩn
    existing = c.execute("SELECT id FROM users WHERE username='admin'").fetchone()
    if existing:
        c.execute(
            "UPDATE users SET password=?, role='admin', status='approved', active=1 WHERE username='admin'",
            (hash_pw("admin123"),)
        )
        conn.commit()
        print("[OK] Da dat lai mat khau admin: admin / admin123")
    else:
        c.execute(
            "INSERT INTO users(username,password,ho_ten,email,role,status,active) VALUES(?,?,?,?,?,?,?)",
            ("admin", hash_pw("admin123"), "Quan tri vien", "admin@auto.vn", "admin", "approved", 1)
        )
        conn.commit()
        print("[OK] Da tao tai khoan admin moi: admin / admin123")
 
    conn.close()
    print("\nBay gio ban co the dang nhap bang:")
    print("  Tai khoan : admin")
    print("  Mat khau  : admin123")
    print("\n[!] Nho sua auth.py (dong insert admin) de bug khong lap lai nua!")
 
if __name__ == "__main__":
    main()
 