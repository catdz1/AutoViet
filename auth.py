"""
auth.py — Quản lý tài khoản, đăng nhập, đăng ký
Thêm trường status: pending / approved / rejected
"""
import hashlib, sqlite3, os
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dealership.db")
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
def hash_pw(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def init_users_table():
    conn = get_conn(); c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        username   TEXT UNIQUE NOT NULL,
        password   TEXT NOT NULL,
        ho_ten     TEXT NOT NULL,
        email      TEXT,
        role       TEXT DEFAULT 'nhanvien',
        nv_id      INTEGER,
        active     INTEGER DEFAULT 1,
        status     TEXT DEFAULT 'approved',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")
        # Thêm cột status nếu chưa có (migrate)
    try:
        c.execute("ALTER TABLE users ADD COLUMN status TEXT DEFAULT 'approved'")
    except Exception:
        pass
    # Thêm cột active nếu chưa có (migrate)
    try:
        c.execute("ALTER TABLE users ADD COLUMN active INTEGER DEFAULT 1")
    except Exception:
        pass
    # Admin mặc định

    if not c.execute("SELECT COUNT(*) FROM users WHERE username='admin'").fetchone()[0]:
        c.execute("INSERT INTO users(username,password,ho_ten,email,role,status,active) VALUES(?,?,?,?,?,?,?)",
                  ("admin", hash_pw("admin123"), "Quản trị viên", "admin@auto.vn", "admin", "approved", 1))
        print("[✓] Tạo tài khoản admin: admin / admin123")
    conn.commit(); conn.close()
    print("[✓] Bảng users đã sẵn sàng!")
def login(username: str, password: str):
    """Đăng nhập — kiểm tra status"""
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM users WHERE username=? AND password=? AND active=1",
        (username.strip(), hash_pw(password))
    ).fetchone()
    conn.close()
    if not row:
        return None, "wrong_password"
    row = dict(row)
    if row.get("status") == "pending":
        return None, "pending"
    if row.get("status") == "rejected":
        return None, "rejected"
    # Tự tìm nv_id nếu chưa có
    if not row.get("nv_id"):
        conn2 = get_conn()
        nv = conn2.execute(
            "SELECT id FROM nhan_vien WHERE LOWER(TRIM(ho_ten))=LOWER(TRIM(?))",
            (row.get("ho_ten",""),)
        ).fetchone()
        if nv:
            row["nv_id"] = nv["id"]
            conn2.execute("UPDATE users SET nv_id=? WHERE id=?",
                         (nv["id"], row["id"]))
            conn2.commit()
        conn2.close()
    return row, "ok"
def register_nhanvien(username, password, ho_ten, email="", nv_id=None):
    username = username.strip().lower()
    if not username or not password or not ho_ten:
        return False, "Vui lòng điền đầy đủ thông tin bắt buộc!"
    if len(password) < 6:
        return False, "Mật khẩu phải có ít nhất 6 ký tự!"
    if not username.replace("_","").isalnum():
        return False, "Tên đăng nhập chỉ dùng chữ cái, số và dấu _!"
    conn = get_conn()
    try:
        nv_pk = None
        if nv_id:
            nv = conn.execute("SELECT id FROM nhan_vien WHERE ma_nv=?", (nv_id,)).fetchone()
            if nv: nv_pk = nv["id"]
        # Đăng ký NV → status = pending, chờ admin duyệt
        conn.execute(
            "INSERT INTO users(username,password,ho_ten,email,role,nv_id,status) VALUES(?,?,?,?,?,?,?)",
            (username, hash_pw(password), ho_ten.strip(), email.strip(), "nhanvien", nv_pk, "pending")
        )
        conn.commit()
        return True, f"Đăng ký thành công! Chờ Admin duyệt tài khoản."
    except sqlite3.IntegrityError:
        return False, f"Tên đăng nhập '{username}' đã tồn tại!"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()
def get_all_users(filter_status=None):
    conn = get_conn()
    sql = """SELECT u.*, nv.ho_ten as ten_nv, nv.chuc_vu
             FROM users u LEFT JOIN nhan_vien nv ON u.nv_id=nv.id"""
    if filter_status:
        sql += f" WHERE u.status='{filter_status}'"
    sql += " ORDER BY u.id"
    rows = [dict(r) for r in conn.execute(sql).fetchall()]
    conn.close(); return rows
def approve_user(user_id: int):
    conn = get_conn()
    user = conn.execute("SELECT id, ho_ten, nv_id FROM users WHERE id=?", (user_id,)).fetchone()
    if user and not user["nv_id"]:
        ho_ten = user["ho_ten"]
        existing = conn.execute("SELECT id FROM nhan_vien WHERE LOWER(TRIM(ho_ten))=LOWER(TRIM(?))", (ho_ten,)).fetchone()
        if existing:
            nv_pk = existing["id"]
        else:
            last = conn.execute("SELECT ma_nv FROM nhan_vien WHERE ma_nv LIKE 'NV%' ORDER BY ma_nv DESC LIMIT 1").fetchone()
            try:
                so = int(last["ma_nv"][2:]) + 1 if last else 1
            except (ValueError, TypeError):
                so = 1
            ma_nv = f"NV{so:03d}"
            while conn.execute("SELECT id FROM nhan_vien WHERE ma_nv=?", (ma_nv,)).fetchone():
                so += 1
                ma_nv = f"NV{so:03d}"
            conn.execute("INSERT INTO nhan_vien(ma_nv,ho_ten,chuc_vu,trang_thai) VALUES(?,?,?,?)",
                         (ma_nv, ho_ten, "Nhân viên", "Đang làm"))
            nv_pk = conn.execute("SELECT id FROM nhan_vien WHERE ma_nv=?", (ma_nv,)).fetchone()["id"]
        conn.execute("UPDATE users SET nv_id=? WHERE id=?", (nv_pk, user_id))
    conn.execute("UPDATE users SET status='approved', active=1 WHERE id=?", (user_id,))
    conn.commit()
    conn.close()
def reject_user(user_id: int):
    conn = get_conn()
    conn.execute("UPDATE users SET status='rejected', active=0 WHERE id=?", (user_id,))
    conn.commit(); conn.close()
def toggle_user_active(user_id: int):
    conn = get_conn()
    conn.execute("UPDATE users SET active=CASE WHEN active=1 THEN 0 ELSE 1 END WHERE id=?", (user_id,))
    conn.commit(); conn.close()
def change_password(user_id, old_pw, new_pw):
    if len(new_pw) < 6: return False, "Mật khẩu mới tối thiểu 6 ký tự!"
    conn = get_conn()
    row = conn.execute("SELECT id FROM users WHERE id=? AND password=?",
                       (user_id, hash_pw(old_pw))).fetchone()
    if not row: conn.close(); return False, "Mật khẩu cũ không đúng!"
    conn.execute("UPDATE users SET password=? WHERE id=?", (hash_pw(new_pw), user_id))
    conn.commit(); conn.close()
    return True, "Đổi mật khẩu thành công!"
