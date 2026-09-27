"""
views/doi_matkhau_view.py — Quản lý Thông tin nhân viên (Chính) + Đổi mật khẩu (Phụ)
Admin: Xem/Quản lý tất cả nhân viên
Nhân viên: Xem/Chỉnh sửa thông tin của mình
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget,
    QPushButton, QLineEdit, QWidget, QFrame, QMessageBox, QApplication,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox, QDateEdit,
    QSpinBox, QScrollArea, QFormLayout
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QColor
from database import get_conn
from datetime import datetime

STYLE = """
QDialog { background:#ffffff; }
QWidget#emp_card { background:#ffffff; border-radius:12px; border:1px solid #e2e8f0; }
QWidget#pwd_card { background:#f8fafc; border-radius:12px; border:1px solid #e2e8f0; }
QLabel#title { font-size:17px; font-weight:800; color:#0f172a; }
QLabel#subtitle { font-size:13px; color:#64748b; font-weight:500; }
QLabel#section { font-size:13px; font-weight:700; color:#ffffff; background:#7c3aed; padding:8px 12px; border-radius:6px; }
QLabel#info_label { font-size:11px; color:#64748b; font-weight:600; background:transparent; min-width:120px; }
QLabel#info_value { font-size:12px; color:#0f172a; font-weight:500; background:transparent; }
QLabel#error { color:#dc2626; font-size:12px; min-height:14px; }
QLabel#ok { color:#16a34a; font-size:12px; }
QLineEdit {
    background:#ffffff; color:#0f172a;
    border:1px solid #cbd5e1; border-radius:6px;
    padding:8px 10px; font-size:14px; font-weight:600;
}
QLineEdit:focus { border:2px solid #7c3aed; }
QLineEdit::placeholder { color:#94a3b8; }
QComboBox {
    background:#ffffff; color:#0f172a;
    border:1px solid #cbd5e1; border-radius:6px;
    padding:8px 10px; font-size:14px; font-weight:600;
}
QComboBox:focus { border:2px solid #7c3aed; }
QComboBox QAbstractItemView {
    background:#ffffff; color:#0f172a;
    border:1px solid #cbd5e1;
    outline:none;
}
QComboBox QAbstractItemView::item {
    background:#ffffff; color:#0f172a;
    padding:8px 12px; font-size:14px; font-weight:600;
    height:32px;
}
QComboBox QAbstractItemView::item:selected {
    background:#e0e7ff; color:#0f172a;
}
QComboBox QAbstractItemView::item:hover {
    background:#f1f5f9; color:#0f172a;
}
QDateEdit {
    background:#ffffff; color:#0f172a;
    border:1px solid #cbd5e1; border-radius:6px;
    padding:8px 10px; font-size:14px; font-weight:600;
}
QSpinBox {
    background:#ffffff; color:#0f172a;
    border:1px solid #cbd5e1; border-radius:6px;
    padding:8px 10px; font-size:14px; font-weight:600;
}
QTabBar::tab{padding:10px 16px;font-size:12px;font-weight:600;
    color:#64748b;background:#f1f5f9;border:none;border-bottom:2px solid transparent;}
QTabBar::tab:selected{color:#7c3aed;border-bottom:2px solid #7c3aed;background:#ffffff;}
QTabWidget::pane{border:none;background:#ffffff;}
QTableWidget{background-color:#ffffff;}
QTableWidget::item{padding:6px;color:#0f172a;}
QTableWidget::item:alternate{background-color:#f8fafc;}
QHeaderView::section{background-color:#f1f5f9;color:#0f172a;font-weight:bold;padding:8px;border:none;}
QPushButton#btn_save {
    background:#7c3aed; color:white; border:none;
    border-radius:6px; font-size:12px; font-weight:700; padding:9px 16px;
}
QPushButton#btn_save:hover { background:#6d28d9; }
QPushButton#btn_edit {
    background:#3b82f6; color:white; border:none;
    border-radius:6px; font-size:11px; font-weight:600; padding:6px 12px;
}
QPushButton#btn_edit:hover { background:#2563eb; }
QPushButton#btn_cancel {
    background:#f1f5f9; color:#475569;
    border:1px solid #e2e8f0; border-radius:6px;
    font-size:12px; padding:9px 16px; font-weight:600;
}
QPushButton#btn_cancel:hover { background:#e2e8f0; color:#1e293b; }
QPushButton#btn_pwd {
    background:#10b981; color:white; border:none;
    border-radius:6px; font-size:11px; font-weight:600; padding:6px 12px;
}
QPushButton#btn_pwd:hover { background:#059669; }
QPushButton#btn_view {
    background:#06b6d4; color:white; border:none;
    border-radius:6px; font-size:11px; font-weight:600; padding:5px 10px;
}
QPushButton#btn_view:hover { background:#0891b2; }
"""


class DoiMatKhauDialog(QDialog):
    def __init__(self, parent=None, user_id=None, username="", is_admin=False):
        super().__init__(parent)
        print(f"[DoiMatKhauDialog] __init__ called - is_admin={is_admin}")

        self.user_id  = user_id
        self.username = username
        self.is_admin = is_admin
        self.is_editing = False
        self.selected_emp_id = user_id

        if is_admin:
            self.setWindowTitle("🔐 Đổi mật khẩu")
        else:
            self.setWindowTitle("Quản lý thông tin nhân viên")

        if is_admin:
            self.setMinimumSize(500, 300)
            self.resize(500, 300)
        else:
            screen = QApplication.primaryScreen().availableGeometry()
            w = min(1300, int(screen.width() * 0.9))
            h = min(700, int(screen.height() * 0.85))
            self.setMinimumSize(w, h)
            self.resize(w, h)

        self.setStyleSheet(STYLE)
        self._employee_data = {}

        print(f"[DoiMatKhauDialog] About to call _load_employee_info or _build - is_admin={is_admin}")
        if not is_admin:
            print("[DoiMatKhauDialog] Loading employee info...")
            self._load_employee_info()

        print("[DoiMatKhauDialog] About to call _build...")
        self._build()
        print("[DoiMatKhauDialog] __init__ completed successfully")

    def _load_employee_info(self, emp_id=None):
        """Load thông tin nhân viên"""
        emp_id = emp_id or self.user_id
        self.selected_emp_id = emp_id
        try:
            conn = get_conn()
            row = conn.execute("""
                SELECT id, ma_nv, ho_ten, chuc_vu, so_dt, email,
                       ngay_vao, luong, trang_thai
                FROM nhan_vien WHERE id = ?
            """, (emp_id,)).fetchone()
            conn.close()

            if row:
                self._employee_data = {
                    "id": row[0],
                    "ma_nv": row[1],
                    "ho_ten": row[2],
                    "chuc_vu": row[3],
                    "so_dt": row[4],
                    "email": row[5],
                    "ngay_vao": row[6],
                    "luong": row[7],
                    "trang_thai": row[8]
                }
                if hasattr(self, 'info_widgets'):
                    self._refresh_employee_fields()
                    # Hiển thị nút chỉnh sửa chỉ khi xem thông tin của mình
                    if emp_id == self.user_id:
                        self.btn_edit.setVisible(True)
                    else:
                        self.btn_edit.setVisible(False)
                    self.btn_save_emp.setVisible(False)
                    self.btn_cancel_emp.setVisible(False)
        except Exception as e:
            print(f"Error: {e}")

    def _build(self):
        print(f"[_build] Called - is_admin={self.is_admin}")
        outer = QVBoxLayout(self)
        outer.setContentsMargins(20, 20, 20, 20)
        outer.setSpacing(16)

        # If admin, show only password change
        if self.is_admin:
            print("[_build] Admin mode - building password form only")
            header = QLabel("🔐  Đổi mật khẩu")
            header_font = QFont("Segoe UI", 16)
            header_font.setBold(True)
            header.setFont(header_font)
            header.setStyleSheet("color:#0f172a;")
            outer.addWidget(header)

            print("[_build] Calling _build_password_form...")
            pwd_form = self._build_password_form()
            print("[_build] _build_password_form returned")
            outer.addWidget(pwd_form, 1)
            print("[_build] Admin mode completed")
            return

        # If not admin, show full dialog with tabs
        print("[_build] Non-admin mode - building full dialog")
        header = QLabel("👤  Quản lý thông tin nhân viên")
        header_font = QFont("Segoe UI", 17)
        header_font.setBold(True)
        header.setFont(header_font)
        header.setStyleSheet("color:#0f172a;")
        outer.addWidget(header)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(STYLE)

        tab1 = self._build_tab_employee()
        self.tabs.addTab(tab1, "👤  Thông tin nhân viên")

        if self.is_admin:
            tab2 = self._build_tab_employees_list()
            self.tabs.addTab(tab2, "👥  Danh sách nhân viên")

        outer.addWidget(self.tabs, 1)
        print("[_build] Non-admin mode completed")

    def _build_password_form(self):
        """Build password change form for admin"""
        print("[_build_password_form] Starting...")
        w = QWidget()
        lv = QVBoxLayout(w)
        lv.setContentsMargins(40, 40, 40, 40)
        lv.setSpacing(14)

        # Mật khẩu hiện tại
        lbl1 = QLabel("🔑  Mật khẩu hiện tại:")
        lbl1.setStyleSheet("font-size:13px; font-weight:700; color:#374151;")
        self.pwd_old = QLineEdit()
        self.pwd_old.setEchoMode(QLineEdit.EchoMode.Password)
        self.pwd_old.setMinimumHeight(40)
        self.pwd_old.setStyleSheet("""
            QLineEdit {
                background:#ffffff; color:#0f172a;
                border:1px solid #d1d5db; border-radius:8px;
                padding:10px 12px; font-size:14px; font-weight:600;
            }
            QLineEdit:focus { border:2px solid #2563eb; }
        """)
        lv.addWidget(lbl1)
        lv.addWidget(self.pwd_old)

        # Mật khẩu mới
        lbl2 = QLabel("🆕  Mật khẩu mới:")
        lbl2.setStyleSheet("font-size:13px; font-weight:700; color:#374151; margin-top:8px;")
        self.pwd_new = QLineEdit()
        self.pwd_new.setEchoMode(QLineEdit.EchoMode.Password)
        self.pwd_new.setMinimumHeight(40)
        self.pwd_new.setStyleSheet(self.pwd_old.styleSheet())
        lv.addWidget(lbl2)
        lv.addWidget(self.pwd_new)

        # Xác nhận mật khẩu
        lbl3 = QLabel("✔️  Xác nhận mật khẩu:")
        lbl3.setStyleSheet("font-size:13px; font-weight:700; color:#374151; margin-top:8px;")
        self.pwd_confirm = QLineEdit()
        self.pwd_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        self.pwd_confirm.setMinimumHeight(40)
        self.pwd_confirm.setStyleSheet(self.pwd_old.styleSheet())
        lv.addWidget(lbl3)
        lv.addWidget(self.pwd_confirm)

        lv.addStretch()

        # Nút bấm
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        btn_row.addStretch()

        btn_cancel = QPushButton("❌  Huỷ")
        btn_cancel.setMinimumWidth(120)
        btn_cancel.setMinimumHeight(42)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background:#f3f4f6; color:#374151; border:1px solid #d1d5db;
                border-radius:8px; font-size:13px; font-weight:700;
            }
            QPushButton:hover { background:#e5e7eb; }
        """)
        btn_cancel.clicked.connect(self.reject)

        btn_ok = QPushButton("💾  Đổi mật khẩu")
        btn_ok.setMinimumWidth(140)
        btn_ok.setMinimumHeight(42)
        btn_ok.setStyleSheet("""
            QPushButton {
                background:#2563eb; color:white; border:none;
                border-radius:8px; font-size:13px; font-weight:700;
            }
            QPushButton:hover { background:#1d4ed8; }
        """)
        btn_ok.clicked.connect(self._change_password_admin)

        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_ok)
        lv.addLayout(btn_row)

        print("[_build_password_form] Completed")
        return w

    def _change_password_admin(self):
        """Change admin password"""
        old_pwd = self.pwd_old.text().strip()
        new_pwd = self.pwd_new.text().strip()
        confirm = self.pwd_confirm.text().strip()

        if not old_pwd:
            print("⚠️ Nhập mật khẩu hiện tại!")
            return
        if not new_pwd:
            print("⚠️ Nhập mật khẩu mới!")
            return
        if len(new_pwd) < 6:
            print("⚠️ Mật khẩu tối thiểu 6 ký tự!")
            return
        if new_pwd != confirm:
            print("⚠️ Mật khẩu không khớp!")
            return

        try:
            conn = get_conn()
            user = conn.execute(
                "SELECT password FROM users WHERE id=?", (self.user_id,)
            ).fetchone()
            conn.close()

            if not user or user[0] != old_pwd:
                print("❌ Mật khẩu hiện tại sai!")
                return

            conn = get_conn()
            conn.execute("UPDATE users SET password=? WHERE id=?", (new_pwd, self.user_id))
            conn.commit()
            conn.close()

            print("✅ Đổi mật khẩu thành công!")
            self.accept()
        except Exception as e:
            print(f"❌ Lỗi: {e}")
            import traceback
            traceback.print_exc()

    def _build_tab_employee(self):
        w = QWidget()
        layout = QHBoxLayout(w)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # CỘT TRÁI: THÔNG TIN NHÂN VIÊN
        emp_card = QWidget()
        emp_card.setObjectName("emp_card")
        emp_card.setMinimumWidth(650)
        emp_lv = QVBoxLayout(emp_card)
        emp_lv.setContentsMargins(24, 24, 24, 24)
        emp_lv.setSpacing(14)

        title_row = QHBoxLayout()
        title = QLabel("📋  THÔNG TIN NHÂN VIÊN")
        title.setObjectName("title")
        title_row.addWidget(title, 1)

        self.btn_edit = QPushButton("✏️  Chỉnh sửa")
        self.btn_edit.setObjectName("btn_edit")
        self.btn_edit.clicked.connect(self._toggle_edit_mode)
        title_row.addWidget(self.btn_edit)

        emp_lv.addLayout(title_row)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea{background:transparent; border:none;}")

        scroll_widget = QWidget()
        scroll_widget.setStyleSheet("background:transparent;")
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(12)

        self.info_widgets = {}

        # SECTION 1
        sec1 = QLabel("🪪  THÔNG TIN CƠ BẢN")
        sec1.setObjectName("section")
        scroll_layout.addWidget(sec1)

        fields_1 = [
            ("Mã NV:", "ma_nv", "text", False),
            ("Họ tên:", "ho_ten", "text", True),
            ("Chức vụ:", "chuc_vu", "combo", True),
            ("Số điện thoại:", "so_dt", "text", True),
        ]

        for label_text, key, widget_type, editable in fields_1:
            row = self._create_field(label_text, key, widget_type, editable)
            scroll_layout.addLayout(row)

        # SECTION 2
        sec2 = QLabel("📧  LIÊN HỆ & CÔNG TY")
        sec2.setObjectName("section")
        scroll_layout.addWidget(sec2)

        fields_2 = [
            ("Email:", "email", "text", True),
            ("Ngày vào làm:", "ngay_vao", "date", False),
            ("Lương:", "luong", "spin", False),
            ("Trạng thái:", "trang_thai", "combo", True),
        ]

        for label_text, key, widget_type, editable in fields_2:
            row = self._create_field(label_text, key, widget_type, editable)
            scroll_layout.addLayout(row)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        emp_lv.addWidget(scroll, 1)

        self.lbl_emp_err = QLabel("")
        self.lbl_emp_err.setObjectName("error")
        self.lbl_emp_err.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_emp_err.setWordWrap(True)
        emp_lv.addWidget(self.lbl_emp_err)

        btn_row = QHBoxLayout()

        self.btn_cancel_emp = QPushButton("Huỷ")
        self.btn_cancel_emp.setObjectName("btn_cancel")
        self.btn_cancel_emp.clicked.connect(self._toggle_edit_mode)
        self.btn_cancel_emp.setVisible(False)

        self.btn_save_emp = QPushButton("💾  Cập nhật")
        self.btn_save_emp.setObjectName("btn_save")
        self.btn_save_emp.clicked.connect(self._save_employee_info)
        self.btn_save_emp.setVisible(False)

        btn_row.addStretch()
        btn_row.addWidget(self.btn_cancel_emp)
        btn_row.addWidget(self.btn_save_emp)
        emp_lv.addLayout(btn_row)

        layout.addWidget(emp_card, 2)

        # CỘT PHẢI: ĐỔI MẬT KHẨU
        pwd_card = QWidget()
        pwd_card.setObjectName("pwd_card")
        pwd_card.setMaximumWidth(380)
        pwd_lv = QVBoxLayout(pwd_card)
        pwd_lv.setContentsMargins(20, 20, 20, 20)
        pwd_lv.setSpacing(12)

        pwd_title = QLabel("🔐  ĐỔI MẬT KHẨU")
        pwd_title.setObjectName("title")
        pwd_lv.addWidget(pwd_title)

        account = QLabel(f"Tài khoản: <b>{self.username}</b>")
        account.setStyleSheet("color:#64748b; font-size:12px;")
        pwd_lv.addWidget(account)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background:#cbd5e1;")
        pwd_lv.addWidget(sep)

        lbl_old = QLabel("Mật khẩu hiện tại")
        lbl_old.setObjectName("info_label")
        self.txt_old = QLineEdit()
        self.txt_old.setPlaceholderText("Nhập mật khẩu cũ...")
        self.txt_old.setEchoMode(QLineEdit.EchoMode.Password)
        pwd_lv.addWidget(lbl_old)
        pwd_lv.addWidget(self.txt_old)

        lbl_new = QLabel("Mật khẩu mới (≥6 ký tự)")
        lbl_new.setObjectName("info_label")
        self.txt_new = QLineEdit()
        self.txt_new.setPlaceholderText("Nhập mật khẩu mới...")
        self.txt_new.setEchoMode(QLineEdit.EchoMode.Password)
        pwd_lv.addWidget(lbl_new)
        pwd_lv.addWidget(self.txt_new)

        lbl_cfm = QLabel("Xác nhận mật khẩu")
        lbl_cfm.setObjectName("info_label")
        self.txt_cfm = QLineEdit()
        self.txt_cfm.setPlaceholderText("Nhập lại mật khẩu mới...")
        self.txt_cfm.setEchoMode(QLineEdit.EchoMode.Password)
        pwd_lv.addWidget(lbl_cfm)
        pwd_lv.addWidget(self.txt_cfm)

        self.btn_show_pwd = QPushButton("👁  Hiển thị")
        self.btn_show_pwd.setObjectName("btn_edit")
        self.btn_show_pwd.setMaximumWidth(120)
        self.btn_show_pwd.setCheckable(True)
        self.btn_show_pwd.toggled.connect(self._toggle_password_visibility)
        pwd_lv.addWidget(self.btn_show_pwd)

        self.lbl_pwd_err = QLabel("")
        self.lbl_pwd_err.setObjectName("error")
        self.lbl_pwd_err.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_pwd_err.setWordWrap(True)
        pwd_lv.addWidget(self.lbl_pwd_err)

        pwd_lv.addSpacing(6)

        btn_pwd_save = QPushButton("🔑  Đổi mật khẩu")
        btn_pwd_save.setObjectName("btn_pwd")
        btn_pwd_save.clicked.connect(self._save_password)
        pwd_lv.addWidget(btn_pwd_save)

        pwd_lv.addStretch()

        layout.addWidget(pwd_card, 1)
        return w

    def _build_tab_employees_list(self):
        w = QWidget()
        lv = QVBoxLayout(w)
        lv.setContentsMargins(16, 16, 16, 16)
        lv.setSpacing(12)

        header_row = QHBoxLayout()
        header = QLabel("📋  Danh sách toàn bộ nhân viên")
        header.setObjectName("title")
        header_row.addWidget(header, 1)

        btn_refresh = QPushButton("🔄  Làm mới")
        btn_refresh.setObjectName("btn_view")
        btn_refresh.clicked.connect(self._load_employees_list)
        header_row.addWidget(btn_refresh)

        lv.addLayout(header_row)

        self.tbl_employees = QTableWidget()
        self.tbl_employees.setAlternatingRowColors(True)
        self.tbl_employees.setColumnCount(8)
        self.tbl_employees.setHorizontalHeaderLabels([
            "Mã NV", "Họ tên", "Chức vụ", "Điện thoại",
            "Email", "Ngày vào", "Lương", "Trạng thái"
        ])

        header = self.tbl_employees.horizontalHeader()
        for i in range(8):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)

        self.tbl_employees.setShowGrid(False)
        self.tbl_employees.verticalHeader().setVisible(False)
        self.tbl_employees.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tbl_employees.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl_employees.doubleClicked.connect(self._on_employee_selected)

        lv.addWidget(self.tbl_employees, 1)

        info = QLabel("💡 Gợi ý: Nhấp đôi vào hàng để xem/chỉnh sửa thông tin")
        info.setStyleSheet("color:#64748b; font-size:11px; font-style:italic;")
        lv.addWidget(info)

        self._load_employees_list()

        return w

    def _load_employees_list(self):
        """Load danh sách nhân viên"""
        try:
            conn = get_conn()
            rows = conn.execute("""
                SELECT id, ma_nv, ho_ten, chuc_vu, so_dt, email,
                       ngay_vao, luong, trang_thai
                FROM nhan_vien ORDER BY ho_ten
            """).fetchall()
            conn.close()

            self.tbl_employees.setRowCount(0)
            for r, row in enumerate(rows):
                self.tbl_employees.insertRow(r)
                self.tbl_employees.setRowHeight(r, 36)

                for c, val in enumerate(row[1:]):
                    item = QTableWidgetItem(str(val) if val else "")

                    if c == 7:
                        color_map = {
                            "Dang lam": "#10b981",
                            "Nghi phep": "#f59e0b",
                            "Thoi viec": "#ef4444",
                            "Tam dung": "#6b7280"
                        }
                        item.setForeground(QColor(color_map.get(str(val), "#0f172a")))
                        item.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))

                    self.tbl_employees.setItem(r, c, item)

                self.tbl_employees.item(r, 0).emp_id = row[0]
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Lỗi: {str(e)}")

    def _on_employee_selected(self, index):
        """Khi click vào nhân viên"""
        row = index.row()
        emp_id = self.tbl_employees.item(row, 0).emp_id
        self._load_employee_info(emp_id)

        # Nếu không phải thông tin của mình, ẩn nút chỉnh sửa
        if emp_id != self.user_id:
            self.btn_edit.setVisible(False)
            self.btn_save_emp.setVisible(False)
            self.btn_cancel_emp.setVisible(False)
        else:
            self.btn_edit.setVisible(True)
            self.btn_save_emp.setVisible(False)
            self.btn_cancel_emp.setVisible(False)

        self.tabs.setCurrentIndex(0)

    def _create_field(self, label_text, key, widget_type, editable):
        """Tạo trường dữ liệu"""
        lbl = QLabel(label_text)
        lbl.setObjectName("info_label")
        lbl.setFixedWidth(130)

        if widget_type == "text":
            widget = QLineEdit()
            widget.setText(str(self._employee_data.get(key, "")))
        elif widget_type == "combo":
            widget = QComboBox()
            if key == "chuc_vu":
                widget.addItems(["Quản lý", "Nhân viên bán hàng", "Nhân viên dịch vụ", "Kỹ thuật", "Khác"])
            elif key == "trang_thai":
                widget.addItems(["Dang lam", "Nghi phep", "Thoi viec", "Tam dung"])
            widget.setCurrentText(str(self._employee_data.get(key, "")))
        elif widget_type == "date":
            widget = QDateEdit()
            try:
                date_str = str(self._employee_data.get(key, ""))
                date = QDate.fromString(date_str, "yyyy-MM-dd")
                widget.setDate(date if date.isValid() else QDate.currentDate())
            except Exception:
                widget.setDate(QDate.currentDate())
        elif widget_type == "spin":
            widget = QSpinBox()
            widget.setMaximum(999999999)
            widget.setValue(int(self._employee_data.get(key, 0)))
            widget.setSuffix(" ₫")

        widget.setEnabled(editable and self.is_editing)
        self.info_widgets[key] = widget

        row = QHBoxLayout()
        row.addWidget(lbl, 0)
        row.addWidget(widget, 1)
        return row

    def _refresh_employee_fields(self):
        """Cập nhật lại tất cả trường"""
        for key, widget in self.info_widgets.items():
            val = self._employee_data.get(key, "")
            if isinstance(widget, QLineEdit):
                widget.setText(str(val))
            elif isinstance(widget, QComboBox):
                widget.setCurrentText(str(val))
            elif isinstance(widget, QDateEdit):
                try:
                    date = QDate.fromString(str(val), "yyyy-MM-dd")
                    widget.setDate(date if date.isValid() else QDate.currentDate())
                except Exception:
                    widget.setDate(QDate.currentDate())
            elif isinstance(widget, QSpinBox):
                widget.setValue(int(val) if val else 0)

    def _toggle_edit_mode(self):
        """Bật/tắt chế độ chỉnh sửa"""
        # Chỉ cho phép nhân viên chỉnh sửa thông tin của chính mình
        if self.selected_emp_id != self.user_id:
            self.lbl_emp_err.setText("❌ Bạn chỉ có thể chỉnh sửa thông tin của mình!")
            return

        self.is_editing = not self.is_editing

        editable_fields = ["ho_ten", "chuc_vu", "so_dt", "email", "trang_thai"]

        for key, widget in self.info_widgets.items():
            if key in editable_fields:
                widget.setEnabled(self.is_editing)

        self.btn_edit.setVisible(not self.is_editing)
        self.btn_save_emp.setVisible(self.is_editing)
        self.btn_cancel_emp.setVisible(self.is_editing)
        self.lbl_emp_err.setText("")

    def _save_employee_info(self):
        """Lưu thông tin nhân viên - chỉ nhân viên mình mới chỉnh được"""
        if self.selected_emp_id != self.user_id:
            self.lbl_emp_err.setText("❌ Bạn không có quyền chỉnh sửa thông tin người khác!")
            return

        try:
            conn = get_conn()
            conn.execute("""
                UPDATE nhan_vien SET
                    ho_ten=?, chuc_vu=?, so_dt=?,
                    email=?, trang_thai=?
                WHERE id=?
            """, (
                self.info_widgets["ho_ten"].text(),
                self.info_widgets["chuc_vu"].currentText(),
                self.info_widgets["so_dt"].text(),
                self.info_widgets["email"].text(),
                self.info_widgets["trang_thai"].currentText(),
                self.selected_emp_id
            ))
            conn.commit()
            conn.close()

            self.lbl_emp_err.setObjectName("ok")
            self.lbl_emp_err.setText("✅ Lưu thành công!")
            self.lbl_emp_err.setStyleSheet("color:#16a34a;")

            self._toggle_edit_mode()
            self._load_employee_info(self.selected_emp_id)
            if self.is_admin:
                self._load_employees_list()
        except Exception as e:
            self.lbl_emp_err.setText(f"❌ Lỗi: {str(e)[:50]}")

    def _toggle_password_visibility(self, checked):
        """Hiển thị/ẩn mật khẩu"""
        mode = QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password
        self.txt_old.setEchoMode(mode)
        self.txt_new.setEchoMode(mode)
        self.txt_cfm.setEchoMode(mode)

    def _save_password(self):
        """Đổi mật khẩu"""
        old = self.txt_old.text()
        new = self.txt_new.text()
        cfm = self.txt_cfm.text()

        if not old or not new:
            self.lbl_pwd_err.setText("❌ Điền đầy đủ!")
            return
        if len(new) < 6:
            self.lbl_pwd_err.setText("❌ Mật khẩu ≥ 6 ký tự!")
            return
        if new != cfm:
            self.lbl_pwd_err.setText("❌ Không khớp!")
            return

        from auth import change_password
        ok, msg = change_password(self.user_id, old, new)
        if ok:
            self.lbl_pwd_err.setObjectName("ok")
            self.lbl_pwd_err.setText("✅ Thành công!")
            self.lbl_pwd_err.setStyleSheet("color:#16a34a;")

            self.txt_old.clear()
            self.txt_new.clear()
            self.txt_cfm.clear()
            self.btn_show_pwd.setChecked(False)
        else:
            self.lbl_pwd_err.setText(f"❌ {msg}")


class DoiMatKhauView(QWidget):
    """Fullscreen view for password change - for main window"""
    def __init__(self, is_admin=False, user_id=None):
        super().__init__()
        self.is_admin = is_admin
        self.user_id = user_id
        self.setObjectName("page_doi_matkhau")
        self.setStyleSheet(STYLE)
        self._employee_data = {}
        self.is_editing = False
        self.selected_emp_id = user_id
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Header
        hdr = QWidget()
        hdr.setStyleSheet("background:#ffffff;border-bottom:2px solid #e5e7eb;")
        hl = QHBoxLayout(hdr)
        hl.setContentsMargins(24, 16, 24, 16)
        hl.setSpacing(16)

        if self.is_admin:
            title = QLabel("🔐  Đổi mật khẩu")
        else:
            title = QLabel("👤  Quản lý thông tin nhân viên")

        title.setStyleSheet("font-size:18px;font-weight:900;color:#0f172a;background:transparent;")
        hl.addWidget(title)
        hl.addStretch()

        root.addWidget(hdr)

        # Content - khác nhau dựa trên is_admin
        if self.is_admin:
            # Admin: chỉ form đổi mật khẩu
            content = QWidget()
            content.setStyleSheet("background:#ffffff;")
            cl = QVBoxLayout(content)
            cl.setContentsMargins(0, 0, 0, 0)

            # Center form
            form_w = QWidget()
            form_l = QVBoxLayout(form_w)
            form_l.setContentsMargins(40, 40, 40, 40)
            form_l.setSpacing(14)

            # Mật khẩu hiện tại
            lbl1 = QLabel("🔑  Mật khẩu hiện tại:")
            lbl1.setStyleSheet("font-size:14px; font-weight:700; color:#374151;")
            self.pwd_old = QLineEdit()
            self.pwd_old.setEchoMode(QLineEdit.EchoMode.Password)
            self.pwd_old.setMinimumHeight(40)
            self.pwd_old.setStyleSheet("""
                QLineEdit {
                    background:#ffffff; color:#0f172a;
                    border:1px solid #d1d5db; border-radius:8px;
                    padding:10px 12px; font-size:14px; font-weight:600;
                    max-width:400px;
                }
                QLineEdit:focus { border:2px solid #2563eb; }
            """)
            form_l.addWidget(lbl1)
            form_l.addWidget(self.pwd_old)

            # Mật khẩu mới
            lbl2 = QLabel("🆕  Mật khẩu mới:")
            lbl2.setStyleSheet("font-size:14px; font-weight:700; color:#374151; margin-top:8px;")
            self.pwd_new = QLineEdit()
            self.pwd_new.setEchoMode(QLineEdit.EchoMode.Password)
            self.pwd_new.setMinimumHeight(40)
            self.pwd_new.setStyleSheet(self.pwd_old.styleSheet())
            form_l.addWidget(lbl2)
            form_l.addWidget(self.pwd_new)

            # Xác nhận
            lbl3 = QLabel("✔️  Xác nhận mật khẩu:")
            lbl3.setStyleSheet("font-size:14px; font-weight:700; color:#374151; margin-top:8px;")
            self.pwd_confirm = QLineEdit()
            self.pwd_confirm.setEchoMode(QLineEdit.EchoMode.Password)
            self.pwd_confirm.setMinimumHeight(40)
            self.pwd_confirm.setStyleSheet(self.pwd_old.styleSheet())
            form_l.addWidget(lbl3)
            form_l.addWidget(self.pwd_confirm)

            form_l.addStretch()

            # Buttons
            btn_row = QHBoxLayout()
            btn_row.setSpacing(12)

            btn_cancel = QPushButton("❌  Huỷ")
            btn_cancel.setMinimumWidth(140)
            btn_cancel.setMinimumHeight(44)
            btn_cancel.setStyleSheet("""
                QPushButton {
                    background:#f3f4f6; color:#374151; border:1px solid #d1d5db;
                    border-radius:8px; font-size:14px; font-weight:700;
                }
                QPushButton:hover { background:#e5e7eb; }
            """)
            btn_cancel.clicked.connect(self._on_cancel)

            btn_ok = QPushButton("💾  Đổi mật khẩu")
            btn_ok.setMinimumWidth(160)
            btn_ok.setMinimumHeight(44)
            btn_ok.setStyleSheet("""
                QPushButton {
                    background:#2563eb; color:white; border:none;
                    border-radius:8px; font-size:14px; font-weight:700;
                }
                QPushButton:hover { background:#1d4ed8; }
            """)
            btn_ok.clicked.connect(self._change_password)

            btn_row.addStretch()
            btn_row.addWidget(btn_cancel)
            btn_row.addWidget(btn_ok)
            form_l.addLayout(btn_row)

            cl.addStretch()
            cl.addWidget(form_w)
            cl.addStretch()
            root.addWidget(content, 1)
        else:
            # Nhân viên: hiển thị tabs đầy đủ (từ DoiMatKhauDialog)
            # Load thông tin nhân viên
            self._load_employee_info()

            # Tabs
            self.tabs = QTabWidget()
            self.tabs.setStyleSheet(STYLE)

            tab1 = self._build_tab_employee()
            self.tabs.addTab(tab1, "👤  Thông tin nhân viên")

            tab2 = self._build_tab_password_change()
            self.tabs.addTab(tab2, "🔐  Đổi mật khẩu")

            root.addWidget(self.tabs, 1)

    def _on_cancel(self):
        """Back to dashboard"""
        from views.main_window import MainWindow
        # Find parent window and navigate back
        parent = self.parent()
        while parent:
            if hasattr(parent, '_nav'):
                parent._nav("Dashboard")
                break
            parent = parent.parent()

    def _load_employee_info(self, emp_id=None):
        """Load thông tin nhân viên"""
        emp_id = emp_id or self.user_id
        self.selected_emp_id = emp_id
        try:
            conn = get_conn()
            row = conn.execute("""
                SELECT id, ma_nv, ho_ten, chuc_vu, so_dt, email,
                       ngay_vao, luong, trang_thai
                FROM nhan_vien WHERE id = ?
            """, (emp_id,)).fetchone()
            conn.close()

            if row:
                self._employee_data = {
                    "id": row[0],
                    "ma_nv": row[1],
                    "ho_ten": row[2],
                    "chuc_vu": row[3],
                    "so_dt": row[4],
                    "email": row[5],
                    "ngay_vao": row[6],
                    "luong": row[7],
                    "trang_thai": row[8]
                }
        except Exception as e:
            print(f"Error loading employee info: {e}")

    def _build_tab_employee(self):
        """Build employee info tab - from DoiMatKhauDialog"""
        tab = QWidget()
        lv = QVBoxLayout(tab)
        lv.setContentsMargins(20, 20, 20, 20)
        lv.setSpacing(16)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content_w = QWidget()
        content_l = QVBoxLayout(content_w)
        content_l.setSpacing(16)

        # Form fields
        form_l = QFormLayout()
        form_l.setSpacing(12)

        self.info_widgets = {}

        # Mã NV
        self.inp_ma_nv = QLineEdit()
        self.inp_ma_nv.setReadOnly(True)
        self.inp_ma_nv.setMinimumHeight(40)
        self.inp_ma_nv.setText(self._employee_data.get("ma_nv", ""))
        form_l.addRow("Mã NV:", self.inp_ma_nv)

        # Họ tên
        self.inp_ho_ten = QLineEdit()
        self.inp_ho_ten.setReadOnly(True)
        self.inp_ho_ten.setMinimumHeight(40)
        self.inp_ho_ten.setText(self._employee_data.get("ho_ten", ""))
        form_l.addRow("Họ tên:", self.inp_ho_ten)

        # Chức vụ
        self.inp_chuc_vu = QLineEdit()
        self.inp_chuc_vu.setReadOnly(True)
        self.inp_chuc_vu.setMinimumHeight(40)
        self.inp_chuc_vu.setText(self._employee_data.get("chuc_vu", ""))
        form_l.addRow("Chức vụ:", self.inp_chuc_vu)

        # SĐT
        self.inp_so_dt = QLineEdit()
        self.inp_so_dt.setReadOnly(True)
        self.inp_so_dt.setMinimumHeight(40)
        self.inp_so_dt.setText(self._employee_data.get("so_dt", ""))
        form_l.addRow("Số điện thoại:", self.inp_so_dt)

        # Email
        self.inp_email = QLineEdit()
        self.inp_email.setReadOnly(True)
        self.inp_email.setMinimumHeight(40)
        self.inp_email.setText(self._employee_data.get("email", ""))
        form_l.addRow("Email:", self.inp_email)

        # Ngày vào
        self.inp_ngay_vao = QLineEdit()
        self.inp_ngay_vao.setReadOnly(True)
        self.inp_ngay_vao.setMinimumHeight(40)
        self.inp_ngay_vao.setText(self._employee_data.get("ngay_vao", ""))
        form_l.addRow("Ngày vào làm:", self.inp_ngay_vao)

        # Lương
        self.inp_luong = QLineEdit()
        self.inp_luong.setReadOnly(True)
        self.inp_luong.setMinimumHeight(40)
        self.inp_luong.setText(str(self._employee_data.get("luong", "")))
        form_l.addRow("Lương:", self.inp_luong)

        # Trạng thái
        self.inp_trang_thai = QLineEdit()
        self.inp_trang_thai.setReadOnly(True)
        self.inp_trang_thai.setMinimumHeight(40)
        self.inp_trang_thai.setText(self._employee_data.get("trang_thai", ""))
        form_l.addRow("Trạng thái:", self.inp_trang_thai)

        content_l.addLayout(form_l)
        content_l.addStretch()

        scroll.setWidget(content_w)
        lv.addWidget(scroll, 1)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        btn_row.addStretch()

        self.btn_edit = QPushButton("✏️  Chỉnh sửa")
        self.btn_edit.setMinimumWidth(140)
        self.btn_edit.setMinimumHeight(40)
        self.btn_edit.setStyleSheet("""
            QPushButton {
                background:#f3f4f6; color:#374151; border:1px solid #d1d5db;
                border-radius:8px; font-size:13px; font-weight:700;
            }
            QPushButton:hover { background:#e5e7eb; }
        """)
        self.btn_edit.clicked.connect(self._toggle_edit_mode)

        self.btn_save = QPushButton("💾  Cập nhật")
        self.btn_save.setMinimumWidth(140)
        self.btn_save.setMinimumHeight(40)
        self.btn_save.setStyleSheet("""
            QPushButton {
                background:#2563eb; color:white; border:none;
                border-radius:8px; font-size:13px; font-weight:700;
            }
            QPushButton:hover { background:#1d4ed8; }
        """)
        self.btn_save.clicked.connect(self._save_employee_info)
        self.btn_save.setVisible(False)

        self.btn_cancel = QPushButton("❌  Huỷ")
        self.btn_cancel.setMinimumWidth(100)
        self.btn_cancel.setMinimumHeight(40)
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background:#f3f4f6; color:#374151; border:1px solid #d1d5db;
                border-radius:8px; font-size:13px; font-weight:700;
            }
            QPushButton:hover { background:#e5e7eb; }
        """)
        self.btn_cancel.clicked.connect(self._cancel_edit)
        self.btn_cancel.setVisible(False)

        btn_row.addWidget(self.btn_edit)
        btn_row.addWidget(self.btn_save)
        btn_row.addWidget(self.btn_cancel)
        lv.addLayout(btn_row)

        return tab

    def _toggle_edit_mode(self):
        """Toggle edit mode"""
        self.is_editing = True
        self.inp_ho_ten.setReadOnly(False)
        self.inp_chuc_vu.setReadOnly(False)
        self.inp_so_dt.setReadOnly(False)
        self.inp_email.setReadOnly(False)

        self.btn_edit.setVisible(False)
        self.btn_save.setVisible(True)
        self.btn_cancel.setVisible(True)

    def _cancel_edit(self):
        """Cancel edit mode"""
        self.is_editing = False
        self._load_employee_info()
        self.inp_ho_ten.setText(self._employee_data.get("ho_ten", ""))
        self.inp_chuc_vu.setText(self._employee_data.get("chuc_vu", ""))
        self.inp_so_dt.setText(self._employee_data.get("so_dt", ""))
        self.inp_email.setText(self._employee_data.get("email", ""))

        self.inp_ho_ten.setReadOnly(True)
        self.inp_chuc_vu.setReadOnly(True)
        self.inp_so_dt.setReadOnly(True)
        self.inp_email.setReadOnly(True)

        self.btn_edit.setVisible(True)
        self.btn_save.setVisible(False)
        self.btn_cancel.setVisible(False)

    def _save_employee_info(self):
        """Save employee info"""
        try:
            conn = get_conn()
            conn.execute("""
                UPDATE nhan_vien 
                SET ho_ten=?, chuc_vu=?, so_dt=?, email=?
                WHERE id=?
            """, (
                self.inp_ho_ten.text(),
                self.inp_chuc_vu.text(),
                self.inp_so_dt.text(),
                self.inp_email.text(),
                self.user_id
            ))
            conn.commit()
            conn.close()

            print("✅ Cập nhật thông tin thành công!")
            self._cancel_edit()
        except Exception as e:
            print(f"❌ Lỗi: {e}")

    def _build_tab_password_change(self):
        """Build password change tab"""
        tab = QWidget()
        lv = QVBoxLayout(tab)
        lv.setContentsMargins(40, 40, 40, 40)
        lv.setSpacing(14)

        # Mật khẩu hiện tại
        lbl1 = QLabel("🔑  Mật khẩu hiện tại:")
        lbl1.setStyleSheet("font-size:14px; font-weight:700; color:#374151;")
        self.pwd_old = QLineEdit()
        self.pwd_old.setEchoMode(QLineEdit.EchoMode.Password)
        self.pwd_old.setMinimumHeight(40)
        self.pwd_old.setStyleSheet("""
            QLineEdit {
                background:#ffffff; color:#0f172a;
                border:1px solid #d1d5db; border-radius:8px;
                padding:10px 12px; font-size:14px; font-weight:600;
                max-width:400px;
            }
            QLineEdit:focus { border:2px solid #2563eb; }
        """)
        lv.addWidget(lbl1)
        lv.addWidget(self.pwd_old)

        # Mật khẩu mới
        lbl2 = QLabel("🆕  Mật khẩu mới:")
        lbl2.setStyleSheet("font-size:14px; font-weight:700; color:#374151; margin-top:8px;")
        self.pwd_new = QLineEdit()
        self.pwd_new.setEchoMode(QLineEdit.EchoMode.Password)
        self.pwd_new.setMinimumHeight(40)
        self.pwd_new.setStyleSheet(self.pwd_old.styleSheet())
        lv.addWidget(lbl2)
        lv.addWidget(self.pwd_new)

        # Xác nhận
        lbl3 = QLabel("✔️  Xác nhận mật khẩu:")
        lbl3.setStyleSheet("font-size:14px; font-weight:700; color:#374151; margin-top:8px;")
        self.pwd_confirm = QLineEdit()
        self.pwd_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        self.pwd_confirm.setMinimumHeight(40)
        self.pwd_confirm.setStyleSheet(self.pwd_old.styleSheet())
        lv.addWidget(lbl3)
        lv.addWidget(self.pwd_confirm)

        lv.addStretch()

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        btn_row.addStretch()

        btn_cancel = QPushButton("❌  Huỷ")
        btn_cancel.setMinimumWidth(120)
        btn_cancel.setMinimumHeight(44)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background:#f3f4f6; color:#374151; border:1px solid #d1d5db;
                border-radius:8px; font-size:14px; font-weight:700;
            }
            QPushButton:hover { background:#e5e7eb; }
        """)
        btn_cancel.clicked.connect(lambda: (
            self.pwd_old.clear(),
            self.pwd_new.clear(),
            self.pwd_confirm.clear()
        ))

        btn_ok = QPushButton("💾  Đổi mật khẩu")
        btn_ok.setMinimumWidth(160)
        btn_ok.setMinimumHeight(44)
        btn_ok.setStyleSheet("""
            QPushButton {
                background:#2563eb; color:white; border:none;
                border-radius:8px; font-size:14px; font-weight:700;
            }
            QPushButton:hover { background:#1d4ed8; }
        """)
        btn_ok.clicked.connect(self._change_password)

        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_ok)
        lv.addLayout(btn_row)

        return tab

    def _change_password(self):
        import hashlib

        old_pwd = self.pwd_old.text().strip()
        new_pwd = self.pwd_new.text().strip()
        confirm = self.pwd_confirm.text().strip()

        if not old_pwd:
            print("⚠️ Nhập mật khẩu hiện tại!")
            return
        if not new_pwd:
            print("⚠️ Nhập mật khẩu mới!")
            return
        if len(new_pwd) < 6:
            print("⚠️ Mật khẩu tối thiểu 6 ký tự!")
            return
        if new_pwd != confirm:
            print("⚠️ Mật khẩu không khớp!")
            return

        try:
            # Hash the passwords for comparison
            old_pwd_hash = hashlib.sha256(old_pwd.encode()).hexdigest()
            new_pwd_hash = hashlib.sha256(new_pwd.encode()).hexdigest()

            conn = get_conn()
            user = conn.execute(
                "SELECT password FROM users WHERE id=?", (self.user_id,)
            ).fetchone()
            conn.close()

            if not user or user[0] != old_pwd_hash:
                print("❌ Mật khẩu hiện tại sai!")
                return

            conn = get_conn()
            conn.execute("UPDATE users SET password=? WHERE id=?", (new_pwd_hash, self.user_id))
            conn.commit()
            conn.close()

            print("✅ Đổi mật khẩu thành công!")
            self.pwd_old.clear()
            self.pwd_new.clear()
            self.pwd_confirm.clear()

            # Navigate back
            self._on_cancel()
        except Exception as e:
            print(f"❌ Lỗi: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    app = QApplication([])
    dialog = DoiMatKhauDialog(user_id=1, username="admin", is_admin=True)
    dialog.exec()