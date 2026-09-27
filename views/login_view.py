"""
views/login_view.py — PHIÊN BẢN V2: Thêm nút "Quên mật khẩu"
THAY THẾ file views/login_view.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import (
    QDialog, QApplication, QMessageBox,
    QLabel, QPushButton, QLineEdit,
    QVBoxLayout, QHBoxLayout, QWidget,
    QFrame, QTabWidget
)
from PyQt6.QtCore import Qt

STYLE = """
QDialog {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
        stop:0 #0a1628, stop:1 #0f1f35);
}
QWidget#card {
    background: #ffffff;
    border-radius: 16px;
    border: none;
}
QLabel { background:transparent; color:#1e293b; font-size:13px; font-weight:700; }
QLabel#lbl_logo   { font-size:26px; font-weight:800; color:#ffffff; }
QLabel#lbl_sub    { font-size:12px; color:rgba(255,255,255,0.6); }
QLabel#lbl_error  { font-size:12px; color:#ef4444; min-height:16px; }
QLabel#lbl_hint   { font-size:11px; color:#94a3b8; }
QLineEdit {
    background:#f8fafc; color:#1e293b;
    border:1.5px solid #e2e8f0; border-radius:8px;
    padding:12px 14px; font-size:14px; font-weight:600; min-height:20px;
}
QLineEdit:focus { border-color:#2563eb; background:#eff6ff; }
QTabWidget::pane { border:none; background:transparent; }
QTabBar::tab {
    background:transparent; color:#64748b; border:none;
    border-bottom:2px solid transparent;
    padding:10px 28px; font-size:14px; font-weight:700;
}
QTabBar::tab:selected { color:#2563eb; border-bottom:2px solid #2563eb; }
QTabBar::tab:hover    { color:#334155; }
QPushButton#btn_admin_login {
    background:#2563eb; color:white; border:none;
    border-radius:10px; font-size:15px; font-weight:800; padding:14px;
}
QPushButton#btn_admin_login:hover   { background:#1d4ed8; }
QPushButton#btn_admin_login:pressed { background:#1e40af; }
QPushButton#btn_nv_login {
    background:#16a34a; color:white; border:none;
    border-radius:10px; font-size:15px; font-weight:800; padding:14px;
}
QPushButton#btn_nv_login:hover   { background:#15803d; }
QPushButton#btn_nv_login:pressed { background:#166534; }
QPushButton#btn_to_reg {
    background:#f0fdf4; color:#16a34a;
    border:1px solid #86efac; border-radius:8px;
    font-size:12px; padding:8px;
}
QPushButton#btn_to_reg:hover { background:#dcfce7; }
QPushButton#btn_forgot {
    background:transparent; color:#2563eb; border:none;
    font-size:12px; text-decoration:underline;
}
QPushButton#btn_forgot:hover { color:#1d4ed8; }
QPushButton#btn_back {
    background:#f8fafc; color:#64748b;
    border:1px solid #e2e8f0; border-radius:8px;
    font-size:13px; padding:10px; min-width:80px;
}
QPushButton#btn_back:hover { background:#f1f5f9; color:#334155; }
QPushButton#btn_do_reg {
    background:#16a34a; color:white; border:none;
    border-radius:8px; font-size:13px; font-weight:700; padding:10px;
}
QPushButton#btn_do_reg:hover { background:#15803d; }
"""

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AutoViet — Đăng nhập")
        self.setFixedSize(440, 560)
        self.setStyleSheet(STYLE)
        self.user_info = None
        self._build()

    def _build(self):
        outer = QVBoxLayout(self); outer.setContentsMargins(28,28,28,28)
        card = QWidget(); card.setObjectName("card")
        card_lv = QVBoxLayout(card); card_lv.setContentsMargins(0,0,0,20); card_lv.setSpacing(0)

        # Header
        hdr = QWidget()
        hdr.setStyleSheet("background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #0f1f35,stop:1 #1e3a5f);border-radius:14px 14px 0 0;")
        hl = QVBoxLayout(hdr); hl.setContentsMargins(30,22,30,16); hl.setSpacing(4)
        logo = QLabel("🚗  AutoViet"); logo.setObjectName("lbl_logo")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub = QLabel("Hệ thống Quản lý Đại lý Xe Hơi v1.0")
        sub.setObjectName("lbl_sub"); sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hl.addWidget(logo); hl.addWidget(sub)
        card_lv.addWidget(hdr)

        # Tabs
        self.tabs = QTabWidget()
        # ─ Tab Admin ─
        ta = QWidget(); tav = QVBoxLayout(ta)
        tav.setContentsMargins(30,18,30,0); tav.setSpacing(10)
        badge_a = QLabel("👑  Đăng nhập với quyền Quản trị viên")
        badge_a.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge_a.setStyleSheet("background:#eff6ff;color:#2563eb;"
                              "border-radius:8px;padding:8px;font-size:12px;")
        lun_a = QLabel("Tên đăng nhập")
        self.txt_a_un = QLineEdit(); self.txt_a_un.setPlaceholderText("admin")
        lpw_a = QLabel("Mật khẩu")
        self.txt_a_pw = QLineEdit(); self.txt_a_pw.setPlaceholderText("Mật khẩu admin...")
        self.txt_a_pw.setEchoMode(QLineEdit.EchoMode.Password)
        self.lbl_a_err = QLabel(""); self.lbl_a_err.setObjectName("lbl_error")
        self.lbl_a_err.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_al = QPushButton("🔓  Đăng nhập Admin"); btn_al.setObjectName("btn_admin_login")
        btn_al.setMinimumHeight(46); btn_al.setCursor(Qt.CursorShape.PointingHandCursor)
        hint_a = QLabel("💡 Mặc định: admin / admin123")
        hint_a.setObjectName("lbl_hint"); hint_a.setAlignment(Qt.AlignmentFlag.AlignCenter)
        for w in [badge_a,lun_a,self.txt_a_un,lpw_a,self.txt_a_pw,
                  self.lbl_a_err,btn_al,hint_a]: tav.addWidget(w)
        tav.addStretch()
        btn_al.clicked.connect(lambda: self._login("admin"))
        self.txt_a_pw.returnPressed.connect(lambda: self._login("admin"))
        self.txt_a_un.returnPressed.connect(lambda: self.txt_a_pw.setFocus())

        # ─ Tab Nhân viên ─
        tn = QWidget(); tnv = QVBoxLayout(tn)
        tnv.setContentsMargins(30,18,30,0); tnv.setSpacing(10)
        badge_n = QLabel("👤  Đăng nhập với tư cách Nhân viên")
        badge_n.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge_n.setStyleSheet("background:#f0fdf4;color:#16a34a;"
                              "border-radius:8px;padding:8px;font-size:12px;")
        lun_n = QLabel("Tên đăng nhập")
        self.txt_n_un = QLineEdit(); self.txt_n_un.setPlaceholderText("Nhập tên đăng nhập...")
        lpw_n = QLabel("Mật khẩu")
        self.txt_n_pw = QLineEdit(); self.txt_n_pw.setPlaceholderText("Nhập mật khẩu...")
        self.txt_n_pw.setEchoMode(QLineEdit.EchoMode.Password)
        self.lbl_n_err = QLabel(""); self.lbl_n_err.setObjectName("lbl_error")
        self.lbl_n_err.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_n_err.setWordWrap(True)
        btn_nl = QPushButton("🔓  Đăng nhập Nhân viên"); btn_nl.setObjectName("btn_nv_login")
        btn_nl.setMinimumHeight(46); btn_nl.setCursor(Qt.CursorShape.PointingHandCursor)

        # Hàng nút dưới: Đăng ký | Quên mật khẩu
        row_btns = QHBoxLayout(); row_btns.setSpacing(8)
        btn_reg = QPushButton("📝 Đăng ký tài khoản")
        btn_reg.setObjectName("btn_to_reg")
        btn_reg.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_forgot = QPushButton("🔑 Quên mật khẩu?")
        btn_forgot.setObjectName("btn_forgot")
        btn_forgot.setCursor(Qt.CursorShape.PointingHandCursor)
        row_btns.addWidget(btn_reg, 1); row_btns.addWidget(btn_forgot, 1)

        for w in [badge_n,lun_n,self.txt_n_un,lpw_n,self.txt_n_pw,
                  self.lbl_n_err,btn_nl]: tnv.addWidget(w)
        tnv.addLayout(row_btns)
        tnv.addStretch()

        btn_nl.clicked.connect(lambda: self._login("nhanvien"))
        btn_reg.clicked.connect(self._open_register)
        btn_forgot.clicked.connect(self._open_forgot)
        self.txt_n_pw.returnPressed.connect(lambda: self._login("nhanvien"))
        self.txt_n_un.returnPressed.connect(lambda: self.txt_n_pw.setFocus())

        self.tabs.addTab(ta, "👑  Admin")
        self.tabs.addTab(tn, "👤  Nhân viên")
        card_lv.addWidget(self.tabs)
        outer.addWidget(card)

    def _login(self, role_tab):
        from auth import login as do_login
        if role_tab == "admin":
            u,p,err_lbl = self.txt_a_un.text().strip(), self.txt_a_pw.text(), self.lbl_a_err
        else:
            u,p,err_lbl = self.txt_n_un.text().strip(), self.txt_n_pw.text(), self.lbl_n_err
        if not u or not p:
            err_lbl.setText("Vui lòng nhập đủ tên đăng nhập và mật khẩu!"); return
        user, status = do_login(u, p)
        if status == "ok":
            if role_tab=="admin" and user.get("role")!="admin":
                err_lbl.setText("❌  Tài khoản này không phải Admin!"); return
            if role_tab=="nhanvien" and user.get("role")=="admin":
                err_lbl.setText("❌  Admin vui lòng dùng tab Admin!"); return
            self.user_info = user; self.accept()
        elif status == "pending":
            err_lbl.setStyleSheet("color:#f59e0b;font-size:12px;background:transparent;")
            err_lbl.setText("⏳  Tài khoản đang chờ Admin duyệt!")
        elif status == "rejected":
            err_lbl.setText("❌  Tài khoản đã bị từ chối. Liên hệ Admin!")
        else:
            err_lbl.setText("❌  Sai tên đăng nhập hoặc mật khẩu!")
            if role_tab=="admin": self.txt_a_pw.clear(); self.txt_a_pw.setFocus()
            else: self.txt_n_pw.clear(); self.txt_n_pw.setFocus()

    def _open_register(self):
        dlg = RegisterDialog(self)
        if dlg.exec():
            self.tabs.setCurrentIndex(1)
            self.txt_n_un.setText(dlg.reg_username); self.txt_n_pw.setFocus()
            self.lbl_n_err.setStyleSheet("color:#4ade80;font-size:12px;background:transparent;")
            self.lbl_n_err.setText("✅ Đăng ký thành công! Chờ Admin duyệt tài khoản.")

    def _open_forgot(self):
        from views.forgot_password_view import ForgotPasswordDialog
        dlg = ForgotPasswordDialog(self)
        if dlg.exec():
            self.lbl_n_err.setStyleSheet("color:#4ade80;font-size:12px;background:transparent;")
            self.lbl_n_err.setText("✅ Đặt lại MK thành công! Đăng nhập ngay.")
            self.txt_n_pw.setFocus()


class RegisterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AutoViet — Đăng ký tài khoản nhân viên")
        self.setFixedSize(440, 540); self.setStyleSheet(STYLE); self.reg_username = ""
        self._build()

    def _build(self):
        outer = QVBoxLayout(self); outer.setContentsMargins(28,28,28,28)
        card = QWidget(); card.setObjectName("card")
        cl = QVBoxLayout(card); cl.setContentsMargins(30,22,30,22); cl.setSpacing(10)
        logo = QLabel("📝  Đăng ký tài khoản")
        logo.setStyleSheet("font-size:20px;font-weight:800;color:#4ade80;background:transparent;")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub = QLabel("Tài khoản cần Admin duyệt trước khi sử dụng")
        sub.setObjectName("lbl_sub"); sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background:#252840;max-height:1px;")
        notice = QLabel("⚠️  Sau khi đăng ký, tài khoản sẽ ở trạng thái 'Chờ duyệt'.\n"
                        "Admin sẽ xem xét và kích hoạt tài khoản cho bạn.")
        notice.setStyleSheet("background:rgba(245,158,11,.1);color:#f59e0b;"
                             "border-radius:8px;padding:10px;font-size:12px;"
                             "font-weight:400;border:1px solid rgba(245,158,11,.3);")
        notice.setWordWrap(True)
        cl.addWidget(logo); cl.addWidget(sub); cl.addWidget(sep); cl.addWidget(notice)

        def row(lbl,ph,pw=False):
            lb=QLabel(lbl); inp=QLineEdit(); inp.setPlaceholderText(ph)
            if pw: inp.setEchoMode(QLineEdit.EchoMode.Password)
            cl.addWidget(lb); cl.addWidget(inp); return inp

        self.f_ten=row("Họ và tên *","Nguyễn Văn A")
        self.f_un =row("Tên đăng nhập *","vd: nhanvien01")
        self.f_em =row("Gmail * (dùng để lấy lại MK)","email@gmail.com")
        self.f_pw =row("Mật khẩu * (tối thiểu 6)","Mật khẩu...",True)
        self.f_cfm=row("Xác nhận mật khẩu *","Nhập lại...",True)

        self.lbl_err=QLabel(""); self.lbl_err.setObjectName("lbl_error")
        self.lbl_err.setAlignment(Qt.AlignmentFlag.AlignCenter); self.lbl_err.setWordWrap(True)
        cl.addWidget(self.lbl_err)
        brow=QHBoxLayout(); brow.setSpacing(10)
        bb=QPushButton("← Quay lại"); bb.setObjectName("btn_back"); bb.setCursor(Qt.CursorShape.PointingHandCursor)
        self.br=QPushButton("📝  Gửi đăng ký"); self.br.setObjectName("btn_do_reg")
        self.br.setMinimumHeight(42); self.br.setCursor(Qt.CursorShape.PointingHandCursor)
        brow.addWidget(bb); brow.addWidget(self.br,1); cl.addLayout(brow)
        outer.addWidget(card)
        bb.clicked.connect(self.reject); self.br.clicked.connect(self._do_reg)
        self.f_cfm.returnPressed.connect(self._do_reg)

    def _do_reg(self):
        from auth import register_nhanvien
        ten=self.f_ten.text().strip(); un=self.f_un.text().strip()
        em=self.f_em.text().strip(); pw=self.f_pw.text(); cfm=self.f_cfm.text()
        if not ten or not un or not pw:
            self.lbl_err.setText("Điền đủ thông tin bắt buộc (*)"); return
        if "@gmail.com" not in em.lower():
            self.lbl_err.setText("❌  Vui lòng nhập địa chỉ Gmail hợp lệ!"); return
        if pw!=cfm:
            self.lbl_err.setText("❌  Mật khẩu xác nhận không khớp!"); return
        self.br.setText("Đang gửi..."); self.br.setEnabled(False)
        QApplication.processEvents()
        ok,msg=register_nhanvien(un,pw,ten,em)
        self.br.setText("📝  Gửi đăng ký"); self.br.setEnabled(True)
        if ok:
            self.reg_username=un
            from PyQt6.QtWidgets import QMessageBox
            # ✅ THAY THẾ QMessageBox.information(... dòng 285-286+) bằng:
            box = QMessageBox(self)
            box.setWindowTitle("Đăng ký thành công!")
            box.setIcon(QMessageBox.Icon.Information)
            box.setText(
                f"<b>✅ Đăng ký thành công!</b><br><br>"
                f"Tài khoản: <b>{un}</b><br>"
                f"Họ Tên: <b>{ten}</b><br><br>"
                f"⏳ Vui lòng chờ Admin phê duyệt tài khoản."
            )
            box.setStyleSheet("""
                QMessageBox { background: #ffffff; }
                QLabel {
                    color: #0f172a; font-size: 13px;
                    font-weight: 500; background: transparent;
                }
                QPushButton {
                    background: #2563eb; color: white;
                    border: none; border-radius: 8px;
                    padding: 8px 24px; font-size: 13px;
                    font-weight: 700; min-width: 80px;
                }
                QPushButton:hover { background: #1d4ed8; }
            """)
            box.exec()
            self.accept()
        else:
            self.lbl_err.setText(f"❌  {msg}")
