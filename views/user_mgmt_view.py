"""
views/user_mgmt_view.py — Khi duyệt NV → tự thêm vào bảng nhan_vien
THAY THẾ file views/user_mgmt_view.py cũ
"""
import hashlib
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QMessageBox, QHeaderView, QDialog,
    QFormLayout, QLineEdit, QComboBox, QTabWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
from database import get_conn


def hash_pw(pw): return hashlib.sha256(pw.encode()).hexdigest()


def _auto_add_nhanvien(user_id, ho_ten):
    """Tự động thêm vào bảng nhan_vien khi duyệt tài khoản"""
    conn = get_conn()
    try:
        # Kiểm tra đã có trong nhan_vien chưa
        exists = conn.execute(
            "SELECT id FROM nhan_vien WHERE ho_ten=?", (ho_ten,)
        ).fetchone()
        if exists:
            # Cập nhật nv_id trong users
            conn.execute("UPDATE users SET nv_id=? WHERE id=?", (exists[0], user_id))
            conn.commit(); conn.close()
            return exists[0]

        # Tạo mã NV tự động
        cnt = conn.execute("SELECT COUNT(*) FROM nhan_vien").fetchone()[0]
        ma_nv = f"NV{cnt+1:03d}"
        # Đảm bảo không trùng
        while conn.execute("SELECT id FROM nhan_vien WHERE ma_nv=?", (ma_nv,)).fetchone():
            cnt += 1; ma_nv = f"NV{cnt+1:03d}"

        # Thêm vào nhan_vien
        c = conn.cursor()
        c.execute("""
                    INSERT INTO nhan_vien(ma_nv, ho_ten, chuc_vu, trang_thai)
                    VALUES(?, ?, 'Nhân viên BH', 'Đang làm')
                """, (ma_nv, ho_ten))
        conn.commit()
        nv_id = c.lastrowid
        # Liên kết users.nv_id
        conn.execute("UPDATE users SET nv_id=? WHERE id=?", (nv_id, user_id))
        conn.commit()
        print(f"[✓] Tạo NV mới: {ma_nv} — {ho_ten}")
        return nv_id
    except Exception as e:
        print(f"[!] Lỗi tạo NV: {e}")
        return None
    finally:
        conn.close()


def _auto_update_nhanvien_status(nv_id, trang_thai):
    """Cập nhật trạng thái NV khi khóa/xoá tài khoản"""
    if not nv_id: return
    conn = get_conn()
    conn.execute("UPDATE nhan_vien SET trang_thai=? WHERE id=?", (trang_thai, nv_id))
    conn.commit(); conn.close()


def approve_user(user_id: int):
    conn = get_conn()
    user = conn.execute("SELECT ho_ten, nv_id FROM users WHERE id=?", (user_id,)).fetchone()
    conn.execute("UPDATE users SET status='approved', active=1 WHERE id=?", (user_id,))
    conn.commit(); conn.close()
    if user:
        # Tự động thêm vào nhan_vien
        _auto_add_nhanvien(user_id, user[0])


def reject_user(user_id: int):
    conn = get_conn()
    conn.execute("UPDATE users SET status='rejected', active=0 WHERE id=?", (user_id,))
    conn.commit(); conn.close()


def get_all_users():
    conn = get_conn()
    rows = [dict(r) for r in conn.execute("""
        SELECT u.*, nv.ho_ten as ten_nv, nv.chuc_vu, nv.trang_thai as nv_tt
        FROM users u LEFT JOIN nhan_vien nv ON u.nv_id=nv.id
        ORDER BY u.id
    """).fetchall()]
    conn.close(); return rows


def toggle_user_active(user_id: int):
    conn = get_conn()
    user = conn.execute("SELECT active, nv_id FROM users WHERE id=?", (user_id,)).fetchone()
    new_active = 0 if user[0] == 1 else 1
    conn.execute("UPDATE users SET active=? WHERE id=?", (new_active, user_id))
    conn.commit(); conn.close()
    # Cập nhật trạng thái NV
    if user[1]:
        _auto_update_nhanvien_status(
            user[1],
            "Đang làm" if new_active == 1 else "Nghỉ việc"
        )


class UserMgmtView(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("page_user_mgmt")
        self._rows = []
        self._sel_id = None
        self._sel_nv_id = None
        self._build()
        self._load()

    def _build(self):
        root = QVBoxLayout(self); root.setContentsMargins(0,0,0,0); root.setSpacing(0)

        # Title
        tw = QWidget(); tw.setObjectName("toolbar_widget")
        th = QHBoxLayout(tw); th.setContentsMargins(18,14,18,14)
        title = QLabel("🔑  Quản lý tài khoản người dùng")
        title.setStyleSheet("font-size:17px;font-weight:700;color:#e2e8f0;background:transparent;")
        self.lbl_pending = QLabel("")
        self.lbl_pending.setStyleSheet(
            "background:rgba(245,158,11,.15);color:#f59e0b;"
            "border-radius:6px;padding:4px 12px;font-size:12px;font-weight:600;")
        th.addWidget(title); th.addStretch(); th.addWidget(self.lbl_pending)
        root.addWidget(tw)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabBar::tab{padding:8px 20px;font-size:12px;font-weight:600;
                color:#64748b;background:#1a1d28;border:none;
                border-bottom:2px solid transparent;}
            QTabBar::tab:selected{color:#a78bfa;border-bottom:2px solid #7c3aed;}
            QTabBar::tab:hover{color:#c8d0e0;background:#252a42;}
            QTabWidget::pane{border:none;}
        """)

        # ── Tab 1: Chờ duyệt ────────────────────────────────────────────
        tab_pending = QWidget()
        pv = QVBoxLayout(tab_pending); pv.setContentsMargins(0,0,0,0); pv.setSpacing(0)

        ptb = QWidget(); ptb.setObjectName("toolbar_widget")
        pth = QHBoxLayout(ptb); pth.setContentsMargins(12,8,12,8); pth.setSpacing(6)

        self.btn_approve = QPushButton("✅  Duyệt — Thêm vào NV")
        self.btn_approve.setObjectName("btn_add")
        self.btn_approve.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_approve.clicked.connect(self._approve)

        self.btn_reject = QPushButton("❌  Từ chối")
        self.btn_reject.setObjectName("btn_del")
        self.btn_reject.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_reject.clicked.connect(self._reject)

        notice = QLabel("✨ Khi duyệt → tự động thêm NV vào hệ thống")
        notice.setStyleSheet("color:#4a5568;font-size:12px;background:transparent;")
        pth.addWidget(self.btn_approve); pth.addWidget(self.btn_reject)
        pth.addStretch(); pth.addWidget(notice)
        pv.addWidget(ptb)

        cols_p = ["ID","TÊN ĐĂNG NHẬP","HỌ TÊN","EMAIL","NGÀY ĐĂNG KÝ"]
        self.tbl_pending = self._make_table(cols_p, [2,3])
        self.tbl_pending.selectionModel().selectionChanged.connect(
            lambda: self._on_sel(self.tbl_pending, "_sel_pending"))
        self._sel_pending = None
        pv.addWidget(self.tbl_pending)

        # ── Tab 2: Tất cả tài khoản ─────────────────────────────────────
        tab_all = QWidget()
        av = QVBoxLayout(tab_all); av.setContentsMargins(0,0,0,0); av.setSpacing(0)

        atb = QWidget(); atb.setObjectName("toolbar_widget")
        ath = QHBoxLayout(atb); ath.setContentsMargins(12,8,12,8); ath.setSpacing(6)

        self.btn_add_user  = QPushButton("+ Thêm TK")
        self.btn_add_user.setObjectName("btn_add")
        self.btn_add_user.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add_user.clicked.connect(self._add_user)

        self.btn_toggle = QPushButton("🔒 Bật/Tắt TK")
        self.btn_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle.clicked.connect(self._toggle)

        self.btn_reset_pw = QPushButton("🔑 Đặt lại MK → 123456")
        self.btn_reset_pw.setObjectName("btn_print")
        self.btn_reset_pw.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_reset_pw.clicked.connect(self._reset_pw)

        self.btn_del_user = QPushButton("🗑  Xoá TK + NV")
        self.btn_del_user.setObjectName("btn_del")
        self.btn_del_user.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_del_user.clicked.connect(self._delete)

        for b in [self.btn_add_user,self.btn_toggle,self.btn_reset_pw,self.btn_del_user]:
            ath.addWidget(b)
        ath.addStretch()
        av.addWidget(atb)

        cols_a = ["ID","TÊN ĐN","HỌ TÊN","VAI TRÒ","TK STATUS","MÃ NV","TRẠNG THÁI NV","NGÀY TẠO"]
        self.tbl_all = self._make_table(cols_a, [2])
        self.tbl_all.selectionModel().selectionChanged.connect(
            lambda: self._on_sel(self.tbl_all, "_sel_all"))
        self._sel_all = None
        self._rows_all = []
        av.addWidget(self.tbl_all)

        self.tabs.addTab(tab_pending, "⏳  Chờ duyệt")
        self.tabs.addTab(tab_all,    "📋  Tất cả tài khoản")
        root.addWidget(self.tabs)

    def _make_table(self, cols, stretch_cols):
        t = QTableWidget(0, len(cols))
        t.setHorizontalHeaderLabels(cols)
        t.setAlternatingRowColors(True)
        t.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        t.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        t.setShowGrid(False); t.verticalHeader().setVisible(False)
        h = t.horizontalHeader()
        for i in stretch_cols:
            h.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
        return t

    def _on_sel(self, tbl, attr):
        r = tbl.currentRow()
        item = tbl.item(r, 0)
        setattr(self, attr, int(item.text()) if item else None)
        if attr == "_sel_all" and item:
            uid = int(item.text())
            row = next((r for r in self._rows_all if r["id"]==uid), None)
            self._sel_nv_id = row.get("nv_id") if row else None

    def _load(self):
        all_users = get_all_users()

        # Pending tab
        pending = [u for u in all_users if u.get("status")=="pending"]
        self.tbl_pending.setRowCount(0)
        for u in pending:
            r = self.tbl_pending.rowCount(); self.tbl_pending.insertRow(r)
            self.tbl_pending.setRowHeight(r, 44)
            for c,val in enumerate([str(u["id"]),u["username"],u["ho_ten"],
                                     u.get("email","") or "",
                                     (u.get("created_at","") or "")[:10]]):
                item = QTableWidgetItem(val)
                item.setData(Qt.ItemDataRole.UserRole, u["id"])
                self.tbl_pending.setItem(r,c,item)

        cnt = len(pending)
        self.lbl_pending.setText(f"⏳ {cnt} tài khoản chờ duyệt" if cnt else "")
        self.lbl_pending.setVisible(cnt > 0)

        # All tab
        self._rows_all = all_users
        self.tbl_all.setRowCount(0)
        STATUS_COL = {"admin":"#f59e0b","nhanvien":"#60a5fa"}
        ACT_COL    = {"approved":"#4ade80","pending":"#f59e0b",
                      "rejected":"#f87171","active":"#4ade80","locked":"#f87171"}
        NV_COL     = {"Đang làm":"#4ade80","Thử việc":"#fbbf24","Nghỉ việc":"#f87171"}

        for u in all_users:
            r = self.tbl_all.rowCount(); self.tbl_all.insertRow(r)
            self.tbl_all.setRowHeight(r, 44)

            nv_ma  = u.get("ten_nv","") or "—"
            nv_tt  = u.get("nv_tt","") or "—"
            tk_st  = "✅ Hoạt động" if u["active"] else "🔒 Bị khóa"

            vals = [str(u["id"]),u["username"],u["ho_ten"],u["role"],
                    u.get("status","approved"), nv_ma, nv_tt,
                    (u.get("created_at","") or "")[:10]]

            for c,val in enumerate(vals):
                item = QTableWidgetItem(val)
                item.setData(Qt.ItemDataRole.UserRole, u["id"])
                if c==3: item.setForeground(QColor(STATUS_COL.get(val,"#94a3b8")))
                if c==4:
                    col = {"approved":"#4ade80","pending":"#f59e0b","rejected":"#f87171"}.get(val,"#94a3b8")
                    item.setForeground(QColor(col))
                    item.setFont(QFont("Segoe UI",12,QFont.Weight.Bold))
                if c==6:
                    item.setForeground(QColor(NV_COL.get(val,"#94a3b8")))
                self.tbl_all.setItem(r,c,item)

    def _approve(self):
        if not self._sel_pending:
            QMessageBox.warning(self,"","Chọn tài khoản cần duyệt!"); return
        conn = get_conn()
        row = conn.execute("SELECT username,ho_ten FROM users WHERE id=?",
                           (self._sel_pending,)).fetchone()
        conn.close()
        if QMessageBox.question(self,"Xác nhận duyệt",
            f"Duyệt tài khoản '{row['username']}' ({row['ho_ten']})?\n\n"
            f"✨ Tài khoản sẽ được tạo hồ sơ nhân viên tự động!",
            QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No
        )==QMessageBox.StandardButton.Yes:
            approve_user(self._sel_pending)
            QMessageBox.information(self,"✅ Thành công!",
                f"Đã duyệt tài khoản '{row['username']}'!\n"
                f"Hồ sơ nhân viên đã được tạo tự động.\n"
                f"Nhân viên có thể đăng nhập ngay!")
            self._sel_pending = None; self._load()

    def _reject(self):
        if not self._sel_pending:
            QMessageBox.warning(self,"","Chọn tài khoản cần từ chối!"); return
        conn = get_conn()
        row = conn.execute("SELECT username FROM users WHERE id=?",
                           (self._sel_pending,)).fetchone()
        conn.close()
        if QMessageBox.question(self,"Từ chối",
            f"Từ chối tài khoản '{row['username']}'?",
            QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No
        )==QMessageBox.StandardButton.Yes:
            reject_user(self._sel_pending)
            self._sel_pending = None; self._load()

    def _toggle(self):
        if not self._sel_all:
            QMessageBox.warning(self,"","Chọn tài khoản!"); return
        row = next((r for r in self._rows_all if r["id"]==self._sel_all), None)
        if row and row["role"]=="admin":
            QMessageBox.warning(self,"","Không thể khóa Admin!"); return

        action = "khóa" if row["active"] else "mở khóa"
        nv_note = f"\n\nNhân viên '{row['ho_ten']}' sẽ được cập nhật trạng thái tương ứng." if row.get("nv_id") else ""

        if QMessageBox.question(self,"Xác nhận",
            f"Bạn muốn {action} tài khoản '{row['username']}'?{nv_note}",
            QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No
        )==QMessageBox.StandardButton.Yes:
            toggle_user_active(self._sel_all)
            self._load()

    def _reset_pw(self):
        if not self._sel_all:
            QMessageBox.warning(self,"","Chọn tài khoản!"); return
        row = next((r for r in self._rows_all if r["id"]==self._sel_all), None)
        if not row: return
        if QMessageBox.question(self,"Đặt lại MK",
            f"Đặt lại MK tài khoản '{row['username']}' về '123456'?",
            QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No
        )==QMessageBox.StandardButton.Yes:
            conn = get_conn()
            conn.execute("UPDATE users SET password=? WHERE id=?",
                         (hash_pw("123456"),self._sel_all))
            conn.commit(); conn.close()
            QMessageBox.information(self,"✅ OK","Mật khẩu đặt lại về: 123456")

    def _delete(self):
        if not self._sel_all:
            QMessageBox.warning(self,"","Chọn tài khoản!"); return
        row = next((r for r in self._rows_all if r["id"]==self._sel_all), None)
        if row and row["role"]=="admin":
            QMessageBox.warning(self,"","Không thể xoá Admin!"); return

        nv_note = f"\n⚠️ Hồ sơ nhân viên '{row['ho_ten']}' sẽ bị đánh dấu 'Nghỉ việc'." if row.get("nv_id") else ""

        if QMessageBox.question(self,"Xác nhận xoá",
            f"Xoá tài khoản '{row['username']}'?{nv_note}",
            QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No
        )==QMessageBox.StandardButton.Yes:
            # Đánh dấu NV nghỉ việc
            if row.get("nv_id"):
                _auto_update_nhanvien_status(row["nv_id"], "Nghỉ việc")
            conn = get_conn()
            conn.execute("DELETE FROM users WHERE id=?", (self._sel_all,))
            conn.commit(); conn.close()
            self._sel_all = None; self._load()

    def _add_user(self):
        dlg = AddUserDialog(self)
        if dlg.exec(): self._load()

    def refresh(self): self._load()


class AddUserDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Thêm tài khoản mới")
        self.setMinimumWidth(420); self._build()

    def _build(self):
        lv = QVBoxLayout(self); lv.setSpacing(12); lv.setContentsMargins(24,20,24,20)
        form = QFormLayout(); form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.f_ten  = QLineEdit(); self.f_ten.setPlaceholderText("Nguyễn Văn A")
        self.f_un   = QLineEdit(); self.f_un.setPlaceholderText("vd: nhanvien01")
        self.f_em   = QLineEdit(); self.f_em.setPlaceholderText("nv@auto.vn")
        self.f_pw   = QLineEdit(); self.f_pw.setPlaceholderText("Tối thiểu 6 ký tự")
        self.f_pw.setEchoMode(QLineEdit.EchoMode.Password)
        self.f_role = QComboBox(); self.f_role.addItems(["nhanvien","admin"])
        for l,w in [("Họ tên *",self.f_ten),("Tên ĐN *",self.f_un),
                    ("Email",self.f_em),("Mật khẩu *",self.f_pw),
                    ("Vai trò",self.f_role)]:
            form.addRow(l,w)
        lv.addLayout(form)
        bh = QHBoxLayout(); bh.addStretch()
        bc = QPushButton("Huỷ"); bc.clicked.connect(self.reject)
        bs = QPushButton("✅  Tạo"); bs.setObjectName("btn_add")
        bs.clicked.connect(self._save)
        bh.addWidget(bc); bh.addWidget(bs); lv.addLayout(bh)

    def _save(self):
        ten = self.f_ten.text().strip();
        un = self.f_un.text().strip().lower()
        pw = self.f_pw.text();
        em = self.f_em.text();
        role = self.f_role.currentText()
        if not all([ten, un, pw]):
            QMessageBox.warning(self, "", "Điền đủ thông tin!");
            return
        if len(pw) < 6:
            QMessageBox.warning(self, "", "MK tối thiểu 6 ký tự!");
            return
        conn = get_conn()
        try:
            c = conn.cursor()  # ✅ thêm dòng này
            c.execute(  # ✅ đổi conn → c
                "INSERT INTO users(username,password,ho_ten,email,role,status) VALUES(?,?,?,?,?,?)",
                (un, hash_pw(pw), ten, em, role, "approved"))
            user_id = c.lastrowid  # ✅ đúng rồi
            conn.commit()
            if role == "nhanvien":
                _auto_add_nhanvien(user_id, ten)
            QMessageBox.information(self, "✅ OK",
                                    f"Tạo tài khoản '{un}' thành công!\n"
                                    f"{'Hồ sơ NV đã được tạo tự động.' if role == 'nhanvien' else ''}")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", "Tên ĐN đã tồn tại!" if "UNIQUE" in str(e) else str(e))
        finally:
            conn.close()
