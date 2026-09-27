"""
views/forgot_password_view.py — Thuần PyQt6, KHÔNG dùng uic
THAY THẾ file views/forgot_password_view.py cũ
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QWidget, QFrame,
    QApplication, QStackedWidget, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer

STYLE = """
QDialog { background-color: #0f1117; }
QWidget#card {
    background-color: #1a1d28;
    border-radius: 14px;
    border: 1px solid #252840;
}
QWidget#hdr {
    background-color: #13151c;
    border-radius: 14px 14px 0 0;
}
QLabel { background:transparent; color:#64748b; font-size:12px; font-weight:600; }
QLabel#lbl_title { font-size:18px; font-weight:800; color:#a78bfa; }
QLabel#lbl_step  { font-size:12px; color:#64748b; }
QLabel#lbl_error { font-size:12px; color:#f87171; min-height:16px; }
QLabel#lbl_info  { font-size:12px; color:#9ca3af; }
QLineEdit {
    background-color:#1e2236; color:#e2e8f0;
    border:1px solid #2c3050; border-radius:8px;
    padding:10px 14px; font-size:13px; min-height:18px;
}
QLineEdit:focus { border-color:#7c3aed; }
QLineEdit#code_input {
    font-size:24px; font-weight:800; letter-spacing:10px;
    color:#a78bfa; background:#1e2236;
    border:2px solid #7c3aed; border-radius:10px; padding:12px;
}
QPushButton#btn_primary {
    background-color:#6d28d9; color:white; border:none;
    border-radius:8px; font-size:13px; font-weight:700; padding:11px;
}
QPushButton#btn_primary:hover   { background-color:#7c3aed; }
QPushButton#btn_primary:pressed { background-color:#5b21b6; }
QPushButton#btn_secondary {
    background-color:#1e2236; color:#9ca3af;
    border:1px solid #2c3050; border-radius:8px;
    font-size:12px; padding:9px; min-width:70px;
}
QPushButton#btn_secondary:hover { background-color:#252a42; color:#e2e8f0; }
QPushButton#btn_resend {
    background:transparent; color:#7c3aed; border:none;
    font-size:12px;
}
QPushButton#btn_resend:hover    { color:#a78bfa; }
QPushButton#btn_resend:disabled { color:#374151; }
"""


class ForgotPasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AutoViet — Quên mật khẩu")
        self.setFixedSize(400, 440)
        self.setStyleSheet(STYLE)
        self._email = ""
        self._timer = None
        self._countdown = 0
        self._build()

    def _build(self):
        # Main layout
        main_lv = QVBoxLayout(self)
        main_lv.setContentsMargins(24, 24, 24, 24)
        main_lv.setSpacing(0)

        # Card
        card = QWidget(); card.setObjectName("card")
        card_lv = QVBoxLayout(card)
        card_lv.setContentsMargins(0, 0, 0, 0)
        card_lv.setSpacing(0)

        # Header
        hdr = QWidget(); hdr.setObjectName("hdr")
        hdr_lv = QVBoxLayout(hdr)
        hdr_lv.setContentsMargins(20, 16, 20, 14)
        hdr_lv.setSpacing(4)
        t = QLabel("🔐  Quên mật khẩu"); t.setObjectName("lbl_title")
        t.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hdr_lv.addWidget(t)
        card_lv.addWidget(hdr)

        # Step bar
        self.lbl_step = QLabel("Bước 1/3 — Nhập Gmail đã đăng ký")
        self.lbl_step.setObjectName("lbl_step")
        self.lbl_step.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_step.setStyleSheet(
            "background:#1e2236; color:#64748b; font-size:11px; "
            "padding:7px; border-bottom:1px solid #252840;")
        card_lv.addWidget(self.lbl_step)

        # Stack
        self.stack = QStackedWidget()
        card_lv.addWidget(self.stack, 1)

        # Footer
        foot_lv = QHBoxLayout()
        foot_lv.setContentsMargins(20, 8, 20, 16)
        self.btn_back = QPushButton("← Quay lại")
        self.btn_back.setObjectName("btn_secondary")
        self.btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_back.hide()
        self.btn_back.clicked.connect(self._go_back)
        foot_lv.addWidget(self.btn_back)
        foot_lv.addStretch()
        card_lv.addLayout(foot_lv)

        main_lv.addWidget(card)

        # Build pages
        self._build_page0()
        self._build_page1()
        self._build_page2()

    def _build_page0(self):
        p = QWidget()
        lv = QVBoxLayout(p)
        lv.setContentsMargins(24, 16, 24, 8)
        lv.setSpacing(10)

        icon = QLabel("📧"); icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet("font-size:36px; background:transparent;")
        desc = QLabel("Nhập Gmail đã đăng ký trong hệ thống.\nMã xác nhận sẽ được gửi đến email đó.")
        desc.setObjectName("lbl_info"); desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl = QLabel("Địa chỉ Gmail *")
        self.txt_email = QLineEdit()
        self.txt_email.setPlaceholderText("example@gmail.com")
        self.lbl_err0 = QLabel(""); self.lbl_err0.setObjectName("lbl_error")
        self.lbl_err0.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.btn_send = QPushButton("📨  Gửi mã xác nhận")
        self.btn_send.setObjectName("btn_primary")
        self.btn_send.setMinimumHeight(44)
        self.btn_send.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_send.clicked.connect(self._send_code)
        self.txt_email.returnPressed.connect(self._send_code)

        for w in [icon, desc, lbl, self.txt_email, self.lbl_err0, self.btn_send]:
            lv.addWidget(w)
        lv.addStretch()
        self.stack.addWidget(p)

    def _build_page1(self):
        p = QWidget()
        lv = QVBoxLayout(p)
        lv.setContentsMargins(24, 16, 24, 8)
        lv.setSpacing(10)

        icon = QLabel("📬"); icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet("font-size:36px; background:transparent;")
        self.lbl_desc1 = QLabel("Mã đã gửi đến:\n...")
        self.lbl_desc1.setObjectName("lbl_info")
        self.lbl_desc1.setWordWrap(True)
        self.lbl_desc1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl = QLabel("Nhập mã 6 chữ số *")
        self.txt_code = QLineEdit(); self.txt_code.setObjectName("code_input")
        self.txt_code.setPlaceholderText("000000")
        self.txt_code.setMaxLength(6)
        self.txt_code.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_err1 = QLabel(""); self.lbl_err1.setObjectName("lbl_error")
        self.lbl_err1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.btn_verify = QPushButton("✅  Xác nhận mã")
        self.btn_verify.setObjectName("btn_primary")
        self.btn_verify.setMinimumHeight(44)
        self.btn_verify.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_verify.clicked.connect(self._verify_code)
        self.txt_code.returnPressed.connect(self._verify_code)
        self.btn_resend = QPushButton("📨 Gửi lại mã (60s)")
        self.btn_resend.setObjectName("btn_resend")
        self.btn_resend.setEnabled(False)
        self.btn_resend.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_resend.clicked.connect(self._resend_code)

        for w in [icon, self.lbl_desc1, lbl, self.txt_code,
                  self.lbl_err1, self.btn_verify, self.btn_resend]:
            lv.addWidget(w)
        lv.addStretch()
        self.stack.addWidget(p)

    def _build_page2(self):
        p = QWidget()
        lv = QVBoxLayout(p)
        lv.setContentsMargins(24, 16, 24, 8)
        lv.setSpacing(10)

        icon = QLabel("🔓"); icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet("font-size:36px; background:transparent;")
        desc = QLabel("Xác nhận thành công!\nĐặt mật khẩu mới cho tài khoản.")
        desc.setObjectName("lbl_info"); desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl1 = QLabel("Mật khẩu mới * (tối thiểu 6 ký tự)")
        self.txt_pw1 = QLineEdit(); self.txt_pw1.setPlaceholderText("Mật khẩu mới...")
        self.txt_pw1.setEchoMode(QLineEdit.EchoMode.Password)
        lbl2 = QLabel("Xác nhận mật khẩu *")
        self.txt_pw2 = QLineEdit(); self.txt_pw2.setPlaceholderText("Nhập lại...")
        self.txt_pw2.setEchoMode(QLineEdit.EchoMode.Password)
        self.lbl_err2 = QLabel(""); self.lbl_err2.setObjectName("lbl_error")
        self.lbl_err2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.btn_reset = QPushButton("🔑  Đặt lại mật khẩu")
        self.btn_reset.setObjectName("btn_primary")
        self.btn_reset.setMinimumHeight(44)
        self.btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_reset.clicked.connect(self._reset_pw)
        self.txt_pw2.returnPressed.connect(self._reset_pw)

        for w in [icon, desc, lbl1, self.txt_pw1, lbl2, self.txt_pw2,
                  self.lbl_err2, self.btn_reset]:
            lv.addWidget(w)
        lv.addStretch()
        self.stack.addWidget(p)

    # ── ACTIONS ─────────────────────────────────────────────────────────
    def _send_code(self):
        from email_sender import send_reset_code
        from database import get_conn
        email = self.txt_email.text().strip().lower()
        if not email or "@" not in email:
            self.lbl_err0.setText("Nhập địa chỉ Gmail hợp lệ!"); return
        conn = get_conn()
        user = conn.execute(
            "SELECT ho_ten FROM users WHERE LOWER(email)=? AND active=1",
            (email,)).fetchone()
        conn.close()
        if not user:
            self.lbl_err0.setText("❌  Không tìm thấy tài khoản với Gmail này!"); return
        self.btn_send.setText("Đang gửi..."); self.btn_send.setEnabled(False)
        QApplication.processEvents()
        ok, msg = send_reset_code(email, user["ho_ten"])
        self.btn_send.setText("📨  Gửi mã xác nhận"); self.btn_send.setEnabled(True)
        if ok:
            self._email = email
            self.lbl_desc1.setText(f"Mã xác nhận đã gửi đến:\n{email}")
            self._go_to(1); self._start_timer()
        else:
            self.lbl_err0.setText(f"❌  {msg}")

    def _verify_code(self):
        from email_sender import verify_code
        code = self.txt_code.text().strip()
        if len(code) != 6:
            self.lbl_err1.setText("Mã xác nhận gồm 6 chữ số!"); return
        self.btn_verify.setText("Đang xác nhận..."); self.btn_verify.setEnabled(False)
        QApplication.processEvents()
        ok, msg = verify_code(self._email, code)
        self.btn_verify.setText("✅  Xác nhận mã"); self.btn_verify.setEnabled(True)
        if ok:
            self._go_to(2)
        else:
            self.lbl_err1.setText(f"❌  {msg}")

    def _reset_pw(self):
        from email_sender import reset_password_by_email
        pw1 = self.txt_pw1.text(); pw2 = self.txt_pw2.text()
        if not pw1:
            self.lbl_err2.setText("Nhập mật khẩu mới!"); return
        if len(pw1) < 6:
            self.lbl_err2.setText("Mật khẩu tối thiểu 6 ký tự!"); return
        if pw1 != pw2:
            self.lbl_err2.setText("❌  Mật khẩu xác nhận không khớp!"); return
        self.btn_reset.setText("Đang xử lý..."); self.btn_reset.setEnabled(False)
        QApplication.processEvents()
        ok, msg = reset_password_by_email(self._email, pw1)
        self.btn_reset.setText("🔑  Đặt lại mật khẩu"); self.btn_reset.setEnabled(True)
        if ok:
            QMessageBox.information(self, "Thành công! 🎉",
                "✅ Đặt lại mật khẩu thành công!\n\n"
                "Đăng nhập bằng mật khẩu mới ngay bây giờ.")
            self.accept()
        else:
            self.lbl_err2.setText(f"❌  {msg}")

    def _resend_code(self):
        self.btn_resend.setEnabled(False)
        self.lbl_err1.setStyleSheet("color:#4ade80; font-size:12px; background:transparent;")
        self.lbl_err1.setText("Đang gửi lại...")
        QApplication.processEvents()
        from email_sender import send_reset_code
        from database import get_conn
        conn = get_conn()
        user = conn.execute("SELECT ho_ten FROM users WHERE LOWER(email)=?",
                            (self._email,)).fetchone()
        conn.close()
        ok, _ = send_reset_code(self._email, user["ho_ten"] if user else "Nhân viên")
        if ok:
            self.lbl_err1.setText("✅ Đã gửi lại mã!")
            self._start_timer()
        else:
            self.lbl_err1.setStyleSheet("color:#f87171; font-size:12px; background:transparent;")
            self.lbl_err1.setText("❌ Gửi lại thất bại!")
            self.btn_resend.setEnabled(True)

    def _start_timer(self):
        self._countdown = 60
        self.btn_resend.setEnabled(False)
        if self._timer: self._timer.stop()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(1000)

    def _tick(self):
        self._countdown -= 1
        if self._countdown <= 0:
            self._timer.stop()
            self.btn_resend.setEnabled(True)
            self.btn_resend.setText("📨 Gửi lại mã")
        else:
            self.btn_resend.setText(f"Gửi lại mã ({self._countdown}s)")

    def _go_to(self, step):
        self.stack.setCurrentIndex(step)
        steps = ["Bước 1/3 — Nhập Gmail đã đăng ký",
                 "Bước 2/3 — Nhập mã xác nhận",
                 "Bước 3/3 — Đặt mật khẩu mới"]
        self.lbl_step.setText(steps[step])
        self.btn_back.setVisible(step > 0)
        if step == 1: self.txt_code.setFocus()
        if step == 2: self.txt_pw1.setFocus()

    def _go_back(self):
        cur = self.stack.currentIndex()
        if cur > 0: self._go_to(cur - 1)