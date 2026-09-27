"""views/login_nhanvien.py — Đăng nhập & Đăng ký Nhân viên"""
import hashlib
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QLabel, QLineEdit, QPushButton, QFrame, QMessageBox, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QPainter, QColor, QLinearGradient
from database import get_conn


def _hash(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()


STYLE_NV = """
* { font-family: 'Segoe UI', sans-serif; }
QDialog  { background: #0d1117; }
QWidget#left_panel { background: #0d1117; }
QWidget#right_panel {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
        stop:0 #1a0533, stop:0.5 #0d1b3e, stop:1 #001a2e);
}

/* Fields */
QLineEdit {
    background: #161b22;
    border: 1.5px solid #30363d;
    border-radius: 10px;
    color: #e6edf3;
    padding: 11px 14px;
    font-size: 13px;
    min-height: 40px;
}
QLineEdit:focus { border-color: #7c3aed; background: #1c2128; }
QLineEdit::placeholder { color: #484f58; }

/* Buttons */
QPushButton#btn_primary {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #7c3aed, stop:1 #4f46e5);
    color: white; border: none; border-radius: 10px;
    padding: 12px; font-size: 14px; font-weight: bold;
    min-height: 46px;
}
QPushButton#btn_primary:hover {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #6d28d9, stop:1 #4338ca);
}
QPushButton#btn_primary:pressed { background: #5b21b6; }

QPushButton#btn_ghost {
    background: transparent; color: #7c3aed;
    border: 1.5px solid #7c3aed; border-radius: 10px;
    padding: 10px; font-size: 13px; min-height: 40px;
}
QPushButton#btn_ghost:hover { background: rgba(124,58,237,0.1); }

QPushButton#btn_link {
    background: transparent; color: #7c3aed;
    border: none; font-size: 13px;
    text-decoration: underline;
}
QPushButton#btn_link:hover { color: #a78bfa; }

QPushButton#btn_eye {
    background: #161b22; border: 1.5px solid #30363d;
    border-radius: 8px; color: #8b949e;
    font-size: 14px; min-width: 42px; min-height: 42px;
}
QPushButton#btn_eye:checked { background: #7c3aed; color: white; border-color: #7c3aed; }

/* Labels */
QLabel#lbl_heading {
    color: #e6edf3; font-size: 22px; font-weight: bold;
}
QLabel#lbl_sub { color: #8b949e; font-size: 13px; }
QLabel#lbl_field { color: #8b949e; font-size: 12px; }
QLabel#lbl_err {
    color: #f85149; background: rgba(248,81,73,0.1);
    border: 1px solid rgba(248,81,73,0.3);
    border-radius: 8px; padding: 8px 12px; font-size: 12px;
}
QLabel#lbl_ok {
    color: #3fb950; background: rgba(63,185,80,0.1);
    border: 1px solid rgba(63,185,80,0.3);
    border-radius: 8px; padding: 8px 12px; font-size: 12px;
}
QLabel#lbl_title_right {
    color: #ffffff; font-size: 24px; font-weight: bold;
}
QLabel#lbl_desc_right { color: rgba(255,255,255,0.65); font-size: 13px; }
QLabel#lbl_badge {
    color: #a78bfa; background: rgba(124,58,237,0.2);
    border: 1px solid rgba(124,58,237,0.4);
    border-radius: 12px; padding: 4px 14px; font-size: 12px; font-weight: bold;
}
QFrame#separator { background: #21262d; max-height: 1px; min-height: 1px; }
"""


class LoginNhanVien(QDialog):
    """Dialog Đăng nhập / Đăng ký Nhân viên."""
    login_success = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AutoViet — Đăng nhập Nhân viên")
        self.setFixedSize(860, 580)
        self.setStyleSheet(STYLE_NV)
        self._init_db()
        self._build_ui()

    # ── DB ───────────────────────────────────────────────────
    def _init_db(self):
        conn = get_conn()
        conn.execute("""CREATE TABLE IF NOT EXISTS tai_khoan (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            ma_nv       TEXT,
            ho_ten      TEXT NOT NULL,
            username    TEXT UNIQUE NOT NULL,
            password    TEXT NOT NULL,
            vai_tro     TEXT DEFAULT 'Nhân viên',
            trang_thai  TEXT DEFAULT 'Hoạt động',
            ngay_tao    TEXT DEFAULT (date('now'))
        )""")
        # Admin mặc định
        if not conn.execute("SELECT 1 FROM tai_khoan WHERE vai_tro='Admin'").fetchone():
            conn.execute("INSERT INTO tai_khoan(ho_ten,username,password,vai_tro) VALUES(?,?,?,?)",
                         ("Quản trị viên", "admin", _hash("admin123"), "Admin"))
        conn.commit(); conn.close()

    # ── UI ───────────────────────────────────────────────────
    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # LEFT — form
        left = QWidget(); left.setObjectName("left_panel")
        left.setFixedWidth(460)
        lv = QVBoxLayout(left)
        lv.setContentsMargins(48, 40, 48, 40)
        lv.setSpacing(0)

        # Logo
        logo_row = QHBoxLayout()
        ico = QLabel("🚗"); ico.setFont(QFont("Segoe UI Emoji", 20))
        lbl_logo = QLabel("AutoViet")
        lbl_logo.setStyleSheet("color:#e6edf3;font-size:17px;font-weight:bold;")
        badge = QLabel("Nhân viên")
        badge.setObjectName("lbl_badge")
        logo_row.addWidget(ico)
        logo_row.addSpacing(8)
        logo_row.addWidget(lbl_logo)
        logo_row.addSpacing(8)
        logo_row.addWidget(badge)
        logo_row.addStretch()
        lv.addLayout(logo_row)
        lv.addSpacing(32)

        # Stack login / register
        self.stack = QStackedWidget()
        self.stack.addWidget(self._page_login())
        self.stack.addWidget(self._page_register())
        lv.addWidget(self.stack)

        root.addWidget(left)

        # RIGHT — illustration
        right = QWidget(); right.setObjectName("right_panel")
        rv = QVBoxLayout(right)
        rv.setContentsMargins(40, 0, 40, 0)
        rv.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl_icon = QLabel("🚗")
        lbl_icon.setFont(QFont("Segoe UI Emoji", 64))
        lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl_t = QLabel("Hệ thống Quản lý\nĐại lý Xe Hơi")
        lbl_t.setObjectName("lbl_title_right")
        lbl_t.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl_d = QLabel("Quản lý xe • Khách hàng • Đơn hàng\nNhân viên • Dịch vụ • Báo cáo")
        lbl_d.setObjectName("lbl_desc_right")
        lbl_d.setAlignment(Qt.AlignmentFlag.AlignCenter)

        sep = QFrame(); sep.setObjectName("separator")
        sep.setStyleSheet("background:rgba(255,255,255,0.15);")
        sep.setFixedWidth(60)

        ver = QLabel("AutoViet v1.0 • Python + PyQt6")
        ver.setStyleSheet("color:rgba(255,255,255,0.35);font-size:11px;")
        ver.setAlignment(Qt.AlignmentFlag.AlignCenter)

        for w in [lbl_icon, lbl_t, lbl_d, sep, ver]:
            rv.addWidget(w)
            if w != ver: rv.addSpacing(16)

        root.addWidget(right)

    # ── Trang Login ──────────────────────────────────────────
    def _page_login(self):
        p = QWidget()
        v = QVBoxLayout(p); v.setContentsMargins(0,0,0,0); v.setSpacing(0)

        lbl_h = QLabel("Đăng nhập"); lbl_h.setObjectName("lbl_heading")
        lbl_s = QLabel("Chào mừng trở lại!"); lbl_s.setObjectName("lbl_sub")
        v.addWidget(lbl_h); v.addSpacing(4); v.addWidget(lbl_s)
        v.addSpacing(28)

        v.addWidget(self._lbl("Tên đăng nhập"))
        self.inp_user = QLineEdit(); self.inp_user.setPlaceholderText("username...")
        self.inp_user.returnPressed.connect(self._do_login)
        v.addSpacing(6); v.addWidget(self.inp_user); v.addSpacing(14)

        v.addWidget(self._lbl("Mật khẩu"))
        pw_row = QHBoxLayout(); pw_row.setSpacing(8)
        self.inp_pass = QLineEdit()
        self.inp_pass.setPlaceholderText("mật khẩu...")
        self.inp_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.inp_pass.returnPressed.connect(self._do_login)
        self.btn_eye = QPushButton("👁"); self.btn_eye.setObjectName("btn_eye")
        self.btn_eye.setCheckable(True); self.btn_eye.setFixedSize(44,44)
        self.btn_eye.toggled.connect(
            lambda c: self.inp_pass.setEchoMode(
                QLineEdit.EchoMode.Normal if c else QLineEdit.EchoMode.Password))
        pw_row.addWidget(self.inp_pass); pw_row.addWidget(self.btn_eye)
        v.addSpacing(6); v.addLayout(pw_row); v.addSpacing(10)

        self.lbl_login_err = QLabel(""); self.lbl_login_err.setObjectName("lbl_err")
        self.lbl_login_err.setWordWrap(True); self.lbl_login_err.hide()
        v.addWidget(self.lbl_login_err); v.addSpacing(20)

        btn = QPushButton("🔐  Đăng nhập"); btn.setObjectName("btn_primary")
        btn.clicked.connect(self._do_login)
        v.addWidget(btn); v.addSpacing(20)

        sep = QFrame(); sep.setObjectName("separator")
        v.addWidget(sep); v.addSpacing(16)

        row = QHBoxLayout()
        row.addWidget(QLabel("Chưa có tài khoản?") if True else None)
        lbl_c = QLabel("Chưa có tài khoản?"); lbl_c.setObjectName("lbl_sub")
        btn_r = QPushButton("Đăng ký ngay"); btn_r.setObjectName("btn_link")
        btn_r.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        row.addWidget(lbl_c); row.addWidget(btn_r); row.addStretch()
        v.addLayout(row); v.addStretch()

        hint = QLabel("💡 Mặc định: admin / admin123")
        hint.setStyleSheet("color:#484f58;font-size:11px;")
        v.addWidget(hint)
        return p

    # ── Trang Register ───────────────────────────────────────
    def _page_register(self):
        outer = QWidget()
        ov = QVBoxLayout(outer); ov.setContentsMargins(0,0,0,0); ov.setSpacing(0)

        lbl_h = QLabel("Tạo tài khoản"); lbl_h.setObjectName("lbl_heading")
        lbl_s = QLabel("Đăng ký tài khoản nhân viên"); lbl_s.setObjectName("lbl_sub")
        ov.addWidget(lbl_h); ov.addSpacing(4); ov.addWidget(lbl_s)
        ov.addSpacing(20)

        # Họ tên
        ov.addWidget(self._lbl("Họ và tên *"))
        self.inp_hoten = QLineEdit(); self.inp_hoten.setPlaceholderText("Nguyễn Văn A")
        ov.addSpacing(6); ov.addWidget(self.inp_hoten); ov.addSpacing(10)

        # Mã NV
        ov.addWidget(self._lbl("Mã nhân viên"))
        self.inp_manv = QLineEdit(); self.inp_manv.setPlaceholderText("VD: NV006 (tuỳ chọn)")
        ov.addSpacing(6); ov.addWidget(self.inp_manv); ov.addSpacing(10)

        # Username
        ov.addWidget(self._lbl("Tên đăng nhập *"))
        self.inp_reg_user = QLineEdit(); self.inp_reg_user.setPlaceholderText("Không dấu, không khoảng trắng")
        ov.addSpacing(6); ov.addWidget(self.inp_reg_user); ov.addSpacing(10)

        # Password
        ov.addWidget(self._lbl("Mật khẩu * (tối thiểu 6 ký tự)"))
        self.inp_reg_pass = QLineEdit()
        self.inp_reg_pass.setPlaceholderText("Nhập mật khẩu")
        self.inp_reg_pass.setEchoMode(QLineEdit.EchoMode.Password)
        ov.addSpacing(6); ov.addWidget(self.inp_reg_pass); ov.addSpacing(10)

        # Confirm password
        ov.addWidget(self._lbl("Xác nhận mật khẩu *"))
        self.inp_reg_pass2 = QLineEdit()
        self.inp_reg_pass2.setPlaceholderText("Nhập lại mật khẩu")
        self.inp_reg_pass2.setEchoMode(QLineEdit.EchoMode.Password)
        ov.addSpacing(6); ov.addWidget(self.inp_reg_pass2); ov.addSpacing(10)

        # Thông báo
        self.lbl_reg_msg = QLabel(""); self.lbl_reg_msg.setWordWrap(True)
        self.lbl_reg_msg.hide()
        ov.addWidget(self.lbl_reg_msg); ov.addSpacing(16)

        btn = QPushButton("✅  Đăng ký tài khoản"); btn.setObjectName("btn_primary")
        btn.clicked.connect(self._do_register)
        ov.addWidget(btn); ov.addSpacing(14)

        row = QHBoxLayout()
        lbl_c = QLabel("Đã có tài khoản?"); lbl_c.setObjectName("lbl_sub")
        btn_b = QPushButton("Đăng nhập"); btn_b.setObjectName("btn_link")
        btn_b.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        row.addWidget(lbl_c); row.addWidget(btn_b); row.addStretch()
        ov.addLayout(row)
        return outer

    # ── Helpers ──────────────────────────────────────────────
    def _lbl(self, text):
        l = QLabel(text); l.setObjectName("lbl_field"); return l

    # ── Logic ────────────────────────────────────────────────
    def _do_login(self):
        u = self.inp_user.text().strip()
        p = self.inp_pass.text()
        if not u or not p:
            self._err_login("Vui lòng nhập đầy đủ thông tin!"); return
        conn = get_conn()
        user = conn.execute(
            "SELECT * FROM tai_khoan WHERE username=? AND password=? AND trang_thai='Hoạt động'",
            (u, _hash(p))).fetchone()
        conn.close()
        if user:
            self.lbl_login_err.hide()
            self.login_success.emit(dict(user))
            self.accept()
        else:
            conn = get_conn()
            locked = conn.execute(
                "SELECT trang_thai FROM tai_khoan WHERE username=?", (u,)).fetchone()
            conn.close()
            if locked and locked[0] == "Bị khoá":
                self._err_login("⛔ Tài khoản đã bị khoá! Liên hệ Admin.")
            else:
                self._err_login("❌ Sai tên đăng nhập hoặc mật khẩu!")

    def _err_login(self, msg):
        self.lbl_login_err.setText(msg)
        self.lbl_login_err.setObjectName("lbl_err")
        self.lbl_login_err.setStyleSheet(
            "color:#f85149;background:rgba(248,81,73,0.1);"
            "border:1px solid rgba(248,81,73,0.3);border-radius:8px;padding:8px 12px;")
        self.lbl_login_err.show()

    def _do_register(self):
        ho_ten = self.inp_hoten.text().strip()
        ma_nv  = self.inp_manv.text().strip()
        uname  = self.inp_reg_user.text().strip()
        pw     = self.inp_reg_pass.text()
        pw2    = self.inp_reg_pass2.text()

        if not ho_ten:
            self._err_reg("Vui lòng nhập họ và tên!"); return
        if not uname:
            self._err_reg("Vui lòng nhập tên đăng nhập!"); return
        if " " in uname:
            self._err_reg("Tên đăng nhập không được có khoảng trắng!"); return
        if len(pw) < 6:
            self._err_reg("Mật khẩu phải có ít nhất 6 ký tự!"); return
        if pw != pw2:
            self._err_reg("Mật khẩu xác nhận không khớp!"); return

        conn = get_conn()
        if conn.execute("SELECT 1 FROM tai_khoan WHERE username=?", (uname,)).fetchone():
            conn.close(); self._err_reg(f"Tên đăng nhập '{uname}' đã tồn tại!"); return
        try:
            conn.execute(
                "INSERT INTO tai_khoan(ma_nv,ho_ten,username,password,vai_tro,trang_thai) VALUES(?,?,?,?,?,?)",
                (ma_nv or None, ho_ten, uname, _hash(pw), "Nhân viên", "Hoạt động"))
            conn.commit(); conn.close()
            self.lbl_reg_msg.setText(f"✅ Đăng ký thành công! Hãy đăng nhập.")
            self.lbl_reg_msg.setStyleSheet(
                "color:#3fb950;background:rgba(63,185,80,0.1);"
                "border:1px solid rgba(63,185,80,0.3);border-radius:8px;padding:8px 12px;")
            self.lbl_reg_msg.show()
            # Tự chuyển sang trang login sau 1.5s
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(1500, lambda: (
                self.stack.setCurrentIndex(0),
                self.inp_user.setText(uname),
                self.inp_pass.setFocus()
            ))
        except Exception as e:
            conn.close(); self._err_reg(str(e))

    def _err_reg(self, msg):
        self.lbl_reg_msg.setText(f"⚠ {msg}")
        self.lbl_reg_msg.setStyleSheet(
            "color:#f85149;background:rgba(248,81,73,0.1);"
            "border:1px solid rgba(248,81,73,0.3);border-radius:8px;padding:8px 12px;")
        self.lbl_reg_msg.show()