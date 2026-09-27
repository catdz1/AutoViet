"""views/login_admin.py — Đăng nhập Admin"""
import hashlib
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from database import get_conn


def _hash(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()


STYLE_ADMIN = """
* { font-family: 'Segoe UI', sans-serif; }
QDialog { background: #0a0a0f; }
QWidget#left_panel {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
        stop:0 #0a0014, stop:0.6 #050d1a, stop:1 #0a0a0f);
}
QWidget#right_panel { background: #0d1117; }

QLineEdit {
    background: #0d1117;
    border: 1.5px solid #21262d;
    border-radius: 10px;
    color: #e6edf3;
    padding: 11px 14px;
    font-size: 13px;
    min-height: 40px;
}
QLineEdit:focus { border-color: #d97706; background: #111827; }

QPushButton#btn_admin {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #b45309, stop:1 #d97706);
    color: white; border: none; border-radius: 10px;
    padding: 12px; font-size: 14px; font-weight: bold;
    min-height: 46px;
}
QPushButton#btn_admin:hover {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #92400e, stop:1 #b45309);
}
QPushButton#btn_admin:pressed { background: #78350f; }

QPushButton#btn_eye {
    background: #0d1117; border: 1.5px solid #21262d;
    border-radius: 8px; color: #8b949e;
    font-size: 14px; min-width: 44px; min-height: 44px;
}
QPushButton#btn_eye:checked { background: #d97706; color: white; border-color: #d97706; }

QPushButton#btn_link {
    background: transparent; color: #d97706;
    border: none; font-size: 12px;
}
QPushButton#btn_link:hover { color: #f59e0b; }

QLabel#lbl_heading { color: #e6edf3; font-size: 22px; font-weight: bold; }
QLabel#lbl_sub     { color: #8b949e; font-size: 13px; }
QLabel#lbl_field   { color: #8b949e; font-size: 12px; }
QLabel#lbl_err {
    color: #f85149; background: rgba(248,81,73,0.1);
    border: 1px solid rgba(248,81,73,0.3);
    border-radius: 8px; padding: 8px 12px; font-size: 12px;
}
QLabel#lbl_badge_admin {
    color: #d97706; background: rgba(217,119,6,0.15);
    border: 1px solid rgba(217,119,6,0.4);
    border-radius: 12px; padding: 4px 14px;
    font-size: 12px; font-weight: bold;
}
QLabel#lbl_warn {
    color: #fbbf24; background: rgba(251,191,36,0.08);
    border: 1px solid rgba(251,191,36,0.25);
    border-radius: 8px; padding: 8px 12px; font-size: 12px;
}
QFrame#separator { background: #21262d; max-height: 1px; }
"""


class LoginAdmin(QDialog):
    """Dialog Đăng nhập dành riêng cho Admin."""
    login_success = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AutoViet — Đăng nhập Quản trị viên")
        self.setFixedSize(860, 540)
        self.setStyleSheet(STYLE_ADMIN)
        self._build_ui()

    # ── UI ───────────────────────────────────────────────────
    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # LEFT — illustration
        left = QWidget(); left.setObjectName("left_panel")
        left.setFixedWidth(380)
        lv = QVBoxLayout(left)
        lv.setContentsMargins(48, 0, 48, 0)
        lv.setAlignment(Qt.AlignmentFlag.AlignCenter)

        shield = QLabel("🛡️")
        shield.setFont(QFont("Segoe UI Emoji", 72))
        shield.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl_t = QLabel("Khu vực\nQuản trị viên")
        lbl_t.setStyleSheet(
            "color:#ffffff;font-size:26px;font-weight:bold;")
        lbl_t.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl_d = QLabel(
            "Chỉ tài khoản Admin mới có\nquyền truy cập khu vực này.")
        lbl_d.setStyleSheet("color:rgba(255,255,255,0.5);font-size:13px;")
        lbl_d.setAlignment(Qt.AlignmentFlag.AlignCenter)

        sep = QFrame(); sep.setObjectName("separator")
        sep.setStyleSheet("background:rgba(217,119,6,0.4);")
        sep.setFixedWidth(50)

        features = [
            "⚙️  Quản lý tài khoản nhân viên",
            "📊  Báo cáo & thống kê toàn hệ thống",
            "🔐  Phân quyền & bảo mật",
            "💾  Sao lưu & khôi phục dữ liệu",
        ]
        for f in features:
            l = QLabel(f)
            l.setStyleSheet(
                "color:rgba(255,255,255,0.6);font-size:12px;padding:2px 0;")
            lv.addWidget(l)

        lv.addStretch()
        for w in [shield, lbl_t, lbl_d, sep]:
            lv.addWidget(w)
            lv.addSpacing(14)
        lv.addSpacing(20)
        for f in features:
            l2 = QLabel(f"  {f}")
            l2.setStyleSheet("color:rgba(255,255,255,0.55);font-size:12px;padding:3px 0;")
            lv.addWidget(l2)
        lv.addStretch()

        root.addWidget(left)

        # RIGHT — form
        right = QWidget(); right.setObjectName("right_panel")
        rv = QVBoxLayout(right)
        rv.setContentsMargins(56, 0, 56, 0)
        rv.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        rv.setSpacing(0)

        # Logo + badge
        logo_row = QHBoxLayout()
        ico = QLabel("🚗"); ico.setFont(QFont("Segoe UI Emoji", 18))
        lbl_logo = QLabel("AutoViet")
        lbl_logo.setStyleSheet("color:#e6edf3;font-size:16px;font-weight:bold;")
        badge = QLabel("🛡  Admin")
        badge.setObjectName("lbl_badge_admin")
        logo_row.addWidget(ico); logo_row.addSpacing(8)
        logo_row.addWidget(lbl_logo); logo_row.addSpacing(10)
        logo_row.addWidget(badge); logo_row.addStretch()
        rv.addLayout(logo_row)
        rv.addSpacing(36)

        lbl_h = QLabel("Đăng nhập Admin")
        lbl_h.setObjectName("lbl_heading")
        rv.addWidget(lbl_h)
        rv.addSpacing(4)

        lbl_s = QLabel("Chỉ dành cho Quản trị viên hệ thống")
        lbl_s.setObjectName("lbl_sub")
        rv.addWidget(lbl_s)
        rv.addSpacing(28)

        # Cảnh báo
        warn = QLabel("⚠  Khu vực bảo mật cao — Không chia sẻ thông tin đăng nhập")
        warn.setObjectName("lbl_warn")
        warn.setWordWrap(True)
        rv.addWidget(warn)
        rv.addSpacing(20)

        # Username
        rv.addWidget(self._lbl("Tên đăng nhập Admin"))
        self.inp_user = QLineEdit()
        self.inp_user.setPlaceholderText("admin username...")
        self.inp_user.returnPressed.connect(self._do_login)
        rv.addSpacing(6); rv.addWidget(self.inp_user)
        rv.addSpacing(14)

        # Password
        rv.addWidget(self._lbl("Mật khẩu"))
        pw_row = QHBoxLayout(); pw_row.setSpacing(8)
        self.inp_pass = QLineEdit()
        self.inp_pass.setPlaceholderText("mật khẩu admin...")
        self.inp_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.inp_pass.returnPressed.connect(self._do_login)
        self.btn_eye = QPushButton("👁")
        self.btn_eye.setObjectName("btn_eye")
        self.btn_eye.setCheckable(True)
        self.btn_eye.setFixedSize(44, 44)
        self.btn_eye.toggled.connect(
            lambda c: self.inp_pass.setEchoMode(
                QLineEdit.EchoMode.Normal if c else QLineEdit.EchoMode.Password))
        pw_row.addWidget(self.inp_pass); pw_row.addWidget(self.btn_eye)
        rv.addSpacing(6); rv.addLayout(pw_row)
        rv.addSpacing(10)

        # Lỗi
        self.lbl_err = QLabel("")
        self.lbl_err.setObjectName("lbl_err")
        self.lbl_err.setWordWrap(True)
        self.lbl_err.hide()
        rv.addWidget(self.lbl_err)
        rv.addSpacing(20)

        # Nút đăng nhập
        btn = QPushButton("🛡  Đăng nhập Admin")
        btn.setObjectName("btn_admin")
        btn.clicked.connect(self._do_login)
        rv.addWidget(btn)
        rv.addSpacing(16)

        sep2 = QFrame(); sep2.setObjectName("separator")
        rv.addWidget(sep2)
        rv.addSpacing(14)

        # Gợi ý
        hint = QLabel("💡 Mặc định: admin / admin123")
        hint.setStyleSheet("color:#374151;font-size:11px;")
        rv.addWidget(hint)

        root.addWidget(right)

    # ── Helpers ──────────────────────────────────────────────
    def _lbl(self, text):
        l = QLabel(text); l.setObjectName("lbl_field"); return l

    # ── Logic ────────────────────────────────────────────────
    def _do_login(self):
        u = self.inp_user.text().strip()
        p = self.inp_pass.text()

        if not u or not p:
            self._err("Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu!"); return

        conn = get_conn()
        user = conn.execute("""
            SELECT * FROM tai_khoan
            WHERE username=? AND password=? AND vai_tro='Admin' AND trang_thai='Hoạt động'
        """, (u, _hash(p))).fetchone()
        conn.close()

        if user:
            self.lbl_err.hide()
            self.login_success.emit(dict(user))
            self.accept()
        else:
            # Kiểm tra có phải tài khoản NV không?
            conn = get_conn()
            row = conn.execute(
                "SELECT vai_tro, trang_thai FROM tai_khoan WHERE username=?", (u,)
            ).fetchone()
            conn.close()

            if not row:
                self._err("❌ Tài khoản không tồn tại!")
            elif row[1] == "Bị khoá":
                self._err("⛔ Tài khoản đã bị khoá!")
            elif row[0] != "Admin":
                self._err("🚫 Tài khoản này không có quyền Admin!")
            else:
                self._err("❌ Sai mật khẩu!")

    def _err(self, msg):
        self.lbl_err.setText(msg)
        self.lbl_err.show()