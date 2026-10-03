import sqlite3
import pytest

import auth

@pytest.fixture
def test_db(tmp_path, monkeypatch):
    """
    Tạo database riêng cho Unit Test.
    """
    db_path = tmp_path / "test_users.db"

    monkeypatch.setattr(auth, "DB_PATH", str(db_path))

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    conn.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            ho_ten TEXT NOT NULL,
            email TEXT,
            role TEXT DEFAULT 'nhanvien',
            nv_id INTEGER,
            active INTEGER DEFAULT 1,
            status TEXT DEFAULT 'approved'
        )
    """)

    # Thêm bảng nhan_vien vì auth.login() có truy vấn bảng này
    conn.execute("""
        CREATE TABLE nhan_vien (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ho_ten TEXT NOT NULL
        )
    """)

    # Tạo nhân viên tương ứng với tài khoản testuser
    conn.execute("""
        INSERT INTO nhan_vien (ho_ten)
        VALUES (?)
    """, ("Nguyen Van Test",))

    conn.execute("""
        INSERT INTO users
        (username, password, ho_ten, role, active, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        "testuser",
        auth.hash_pw("123456"),
        "Nguyen Van Test",
        "nhanvien",
        1,
        "approved"
    ))

    conn.commit()
    conn.close()

    return db_path

def test_login_correct_password(test_db):
    user, message = auth.login("testuser", "123456")

    assert user is not None
    assert message == "ok"


def test_login_wrong_password(test_db):
    user, message = auth.login("testuser", "wrong123")

    assert user is None
    assert message == "wrong_password"


def test_login_nonexistent_user(test_db):
    user, message = auth.login("not_exist_999", "123456")

    assert user is None
    assert message == "wrong_password"


def test_login_pending_user(test_db):
    conn = sqlite3.connect(test_db)

    conn.execute("""
        INSERT INTO users
        (username, password, ho_ten, role, active, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        "pending_user",
        auth.hash_pw("123456"),
        "Pending User",
        "nhanvien",
        1,
        "pending"
    ))

    conn.commit()
    conn.close()

    user, message = auth.login("pending_user", "123456")

    assert user is None
    assert message == "pending"


def test_login_rejected_user(test_db):
    conn = sqlite3.connect(test_db)

    conn.execute("""
        INSERT INTO users
        (username, password, ho_ten, role, active, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        "rejected_user",
        auth.hash_pw("123456"),
        "Rejected User",
        "nhanvien",
        1,
        "rejected"
    ))

    conn.commit()
    conn.close()

    user, message = auth.login("rejected_user", "123456")

    assert user is None
    assert message == "rejected"


def test_register_success(test_db):
    success, message = auth.register_nhanvien(
        "new_user",
        "123456",
        "New User",
        "new@example.com"
    )

    assert success is True
    assert "thành công" in message


def test_register_duplicate_username(test_db):
    success, message = auth.register_nhanvien(
        "testuser",
        "123456",
        "Another User"
    )

    assert success is False
    assert "đã tồn tại" in message


def test_register_short_password(test_db):
    success, message = auth.register_nhanvien(
        "short_pw",
        "123",
        "Test User"
    )

    assert success is False
    assert "6 ký tự" in message
