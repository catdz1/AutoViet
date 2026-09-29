"""
views/thanh_toan_view.py — Quản lý Phương thức Thanh toán
+ Danh sách phương thức thanh toán
+ Gắn vào đơn hàng
+ Báo cáo doanh thu theo phương thức
+ Trạng thái thanh toán
"""
from views.payment_success_dialog import PaymentSuccessDialog
import sys, os
from database import get_conn

# ── AI SERVICES ──────────────────────────────────────────────
from ai_services.vietqr import tao_ma_qr
from ai_services.claude_ai import hoi_tro_ly
from ai_services.zalo_oa import gui_zalo_admin
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QLineEdit, QDialog, QFormLayout, QComboBox, QTextEdit,
    QMessageBox, QScrollArea, QSplitter, QTabWidget,
    QDoubleSpinBox, QDateEdit, QGridLayout
)
from PyQt6.QtCore import Qt, QDate, QThread, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from database import get_conn
from ai_services.cohere_ai import hoi_tro_ly, soan_nhac_no


STYLE = """
QWidget { font-family: 'Segoe UI', Arial; }

QTabWidget::pane {
    border: none;
    background: #f0f4f8;
}
QTabBar::tab {
    background: #f8fafc;
    color: #64748b;
    padding: 10px 24px;
    font-size: 12px;
    font-weight: 600;
    border: none;
    border-bottom: 2px solid transparent;
}
QTabBar::tab:selected {
    color: #2563eb;
    border-bottom: 2px solid #2563eb;
    background: #ffffff;
}
QTabBar::tab:hover { color: #1e40af; background: #eff6ff; }

QWidget#toolbar_widget {
    background: #ffffff;
    border-bottom: 1px solid #dbeafe;
}

QPushButton#btn_add {
    background: #2563eb;
    color: white; border: none; border-radius: 9px;
    font-size: 13px; font-weight: 700; padding: 9px 18px;
}
QPushButton#btn_add:hover { background: #1d4ed8; }
QPushButton#btn_edit {
    background: #eff6ff; color: #1e40af;
    border: 1px solid #bfdbfe; border-radius: 8px;
    font-size: 12px; padding: 8px 14px; font-weight: 600;
}
QPushButton#btn_edit:hover { background: #2563eb; color: white; }
QPushButton#btn_del {
    background: #fee2e2; color: #991b1b;
    border: 1px solid #fecaca; border-radius: 8px;
    font-size: 12px; padding: 8px 14px;
}
QPushButton#btn_del:hover { background: #dc2626; color: white; }
QPushButton#btn_refresh {
    background: #f1f5f9; color: #475569;
    border: 1px solid #e2e8f0; border-radius: 8px;
    font-size: 12px; padding: 8px 14px;
}
QPushButton#btn_refresh:hover { background: #e2e8f0; }

QLineEdit#search_box {
    background: #ffffff; color: #00274c;
    border: 1px solid #dbeafe; border-radius: 9px;
    padding: 8px 16px; font-size: 13px; min-width: 220px;
}
QLineEdit#search_box:focus { border-color: #2563eb; }

QTableWidget {
    background: #ffffff;
    alternate-background-color: #f8fafc;
    gridline-color: #f1f5f9;
    border: none;
    selection-background-color: #dbeafe;
    font-size: 14px;
}
QTableWidget::item { padding: 8px 12px; color: #1e293b; }
QTableWidget::item:selected { color: #2563eb; background: #dbeafe; }
QHeaderView::section {
    background: #f8fafc; color: #2563eb;
    font-size: 12px; font-weight: 800;
    letter-spacing: 1px; padding: 12px; border: none;
    border-bottom: 2px solid #2563eb;
}

QWidget#stat_card {
    background: #ffffff;
    border: 0.5px solid #dbeafe;
    border-radius: 12px;
}
QLabel#stat_value {
    font-size: 22px; font-weight: 800;
    background: transparent;
}
QLabel#stat_label {
    font-size: 11px; color: #64748b;
    background: transparent; font-weight: 600;
    letter-spacing: 1px;
}

QComboBox#filter_combo {
    background: #ffffff; color: #00274c;
    border: 1px solid #dbeafe; border-radius: 8px;
    padding: 7px 12px; font-size: 12px; min-width: 140px;
}
QComboBox#filter_combo:focus { border-color: #2563eb; }
QComboBox#filter_combo::drop-down { border: none; }
QComboBox QAbstractItemView {
    background: #ffffff; color: #00274c;
    border: 1px solid #dbeafe; selection-background-color: #eff6ff;
}
"""
PT_ICONS = {
    "Tiền mặt": "💵",
    "Chuyển khoản": "🏦",
    "Trả góp": "📅",
    "Thẻ tín dụng": "💳",
    "Vay NH": "🏧",
}

TT_COLORS = {
    "Đã thanh toán": "#4ade80",
    "Chưa thanh toán": "#f87171",
    "Thanh toán một phần": "#fbbf24",
    "Chờ xử lý": "#a78bfa",
}

TT_BG = {
    "Đã thanh toán": "rgba(74,222,128,.12)",
    "Chưa thanh toán": "rgba(248,113,113,.12)",
    "Thanh toán một phần": "rgba(251,191,36,.12)",
    "Chờ xử lý": "rgba(167,139,250,.12)",
}

def validate_payment(order_total, paid_amount):
        if paid_amount < 0:
            return False, "Số tiền thanh toán không hợp lệ"

        if paid_amount > order_total:
            return False, "Số tiền thanh toán vượt giá trị đơn hàng"

        return True, ""

class ThanhToanView(QWidget):
    def __init__(self, current_user=None):
        super().__init__()
        self.setObjectName("page_thanh_toan")
        self.setStyleSheet(STYLE)
        self.current_user = current_user or {}
        self.is_admin = current_user.get("role") == "admin" if current_user else False
        self._sel_id = None
        self._rows = []
        self._build()
        self._ensure_columns()
        self._load()


    def _ensure_columns(self):
        """Thêm cột thanh toán vào bảng don_hang nếu chưa có"""
        conn = get_conn()
        try:
            conn.execute("ALTER TABLE don_hang ADD COLUMN trang_thai_tt TEXT DEFAULT 'Chưa thanh toán'")
            conn.commit()
        except Exception: pass
        try:
            conn.execute("ALTER TABLE don_hang ADD COLUMN so_tien_da_tt REAL DEFAULT 0")
            conn.commit()
        except Exception: pass
        try:
            conn.execute("ALTER TABLE don_hang ADD COLUMN ghi_chu_tt TEXT")
            conn.commit()
        except Exception: pass
        conn.close()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Header
        hdr = QWidget(); hdr.setObjectName("toolbar_widget")
        hdr.setStyleSheet("background:#00274c;border-bottom:1px solid #1a3a6b;")
        hl = QHBoxLayout(hdr); hl.setContentsMargins(20, 14, 20, 14)
        t = QLabel("💳  Quản lý Thanh toán")
        t.setStyleSheet("font-size:16px;font-weight:800;color:#e2e8f0;background:transparent;")
        t.setStyleSheet("font-size:11px;color:#4a5568;background:transparent;")
        s = QLabel("Phương thức • Trạng thái • Báo cáo doanh thu")
        s.setStyleSheet("font-size:11px;color:rgba(255,255,255,0.6);background:transparent;")
        col = QVBoxLayout(); col.setSpacing(2)
        col.addWidget(t); col.addWidget(s)
        hl.addLayout(col); hl.addStretch()
        root.addWidget(hdr)

        # Stats bar
        self._stats_w = QWidget()
        self._stats_w.setStyleSheet("background:#f0f4f8;border-bottom:1px solid #dbeafe;")
        sl = QHBoxLayout(self._stats_w)
        sl.setContentsMargins(16, 10, 16, 10); sl.setSpacing(10)
        self._stat_labels = {}
        STAT_DEFS = [
            ("tong_don", "📋 Tổng đơn", "#1e40af", "#eff6ff", "#bfdbfe"),
            ("da_tt", "✅ Đã TT", "#065f46", "#f0fdf4", "#a7f3d0"),
            ("chua_tt", "❌ Chưa TT", "#991b1b", "#fff1f2", "#fecdd3"),
            ("mot_phan", "⏳ Một phần", "#92400e", "#fffbeb", "#fde68a"),
            ("tong_dt", "💰 Tổng DT", "#065f46", "#f0fdf4", "#a7f3d0"),
        ]
        for key, icon, color, bg, border in STAT_DEFS:
            card = QWidget()
            card.setStyleSheet(f"""
                QWidget {{
                    background: {bg};
                    border: 0.5px solid {border};
                    border-radius: 12px;
                    border-top: 3px solid {color};
                }}
            """)
            cl = QVBoxLayout(card)
            cl.setContentsMargins(16, 12, 16, 12)
            cl.setSpacing(4)
            lbl_v = QLabel("—")
            lbl_v.setStyleSheet(
                f"font-size:22px;font-weight:800;color:{color};background:transparent;")
            lbl_l = QLabel(icon)
            lbl_l.setStyleSheet(
                f"font-size:11px;color:{color};background:transparent;"
                "font-weight:700;letter-spacing:0.5px;opacity:0.8;")
            cl.addWidget(lbl_v)
            cl.addWidget(lbl_l)
            sl.addWidget(card, 1)
            self._stat_labels[key] = lbl_v
        root.addWidget(self._stats_w)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(STYLE)

        # Tab 1: Danh sách thanh toán
        tab1 = self._build_tab_danhsach()
        self.tabs.addTab(tab1, "📋  Danh sách thanh toán")

        # Tab 2: Phương thức
        tab2 = self._build_tab_phuongthuc()
        self.tabs.addTab(tab2, "💳  Phương thức")

        # Tab 3: Báo cáo
        tab3 = self._build_tab_baocao()
        self.tabs.addTab(tab3, "📊  Báo cáo")
        # Tab 4: AI Assistant
        tab4 = self._build_tab_ai()
        self.tabs.addTab(tab4, '🤖  AI Assistant')


        root.addWidget(self.tabs, 1)

    def _build_tab_danhsach(self):
        w = QWidget(); w.setStyleSheet("background:#f0f4f8;")
        lv = QVBoxLayout(w); lv.setContentsMargins(0, 0, 0, 0); lv.setSpacing(0)

        # Toolbar
        tb = QWidget(); tb.setObjectName("toolbar_widget")
        tbh = QHBoxLayout(tb); tbh.setContentsMargins(14, 8, 14, 8); tbh.setSpacing(8)

        btn_cap = QPushButton("✏️  Cập nhật TT");
        btn_cap.setObjectName("btn_edit")
        btn_cap.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        btn_cap.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cap.clicked.connect(self._cap_nhat_tt)

        btn_ref = QPushButton("🔄  Làm mới");
        btn_ref.setObjectName("btn_refresh")
        btn_ref.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        btn_ref.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ref.clicked.connect(self._load)

        self.filter_tt = QComboBox();
        self.filter_tt.setObjectName("filter_combo")
        self.filter_tt.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        self.filter_tt.addItems(["Tất cả", "Đã thanh toán", "Chưa thanh toán",
                                 "Thanh toán một phần", "Chờ xử lý"])
        self.filter_tt.currentTextChanged.connect(self._load)

        self.filter_pt = QComboBox();
        self.filter_pt.setObjectName("filter_combo")
        self.filter_pt.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        self.filter_pt.addItems(["Tất cả PT", "Tiền mặt", "Chuyển khoản",
                                 "Trả góp", "Thẻ tín dụng", "Vay NH"])
        self.filter_pt.currentTextChanged.connect(self._load)

        self.search = QLineEdit();
        self.search.setObjectName("search_box")
        self.search.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        self.search.setPlaceholderText("🔍  Tìm mã đơn, khách hàng...")
        self.search.textChanged.connect(lambda t: self._load())

        tbh.addWidget(btn_cap);
        tbh.addWidget(btn_ref)
        lbl_tt = QLabel("  Trạng thái:")
        lbl_tt.setStyleSheet("color:#1e40af;font-size:13px;font-weight:700;background:transparent;")
        tbh.addWidget(lbl_tt)
        tbh.addWidget(self.filter_tt)
        tbh.addWidget(self.filter_pt)
        tbh.addStretch()
        tbh.addWidget(self.search)
        lv.addWidget(tb)

        # Table
        cols = ["MÃ ĐƠN", "KHÁCH HÀNG", "XE", "PHƯƠNG THỨC",
                "GIÁ BÁN", "ĐÃ THANH TOÁN", "CÒN LẠI", "TRẠNG THÁI TT", "NGÀY ĐẶT"]
        self.tbl = QTableWidget(0, len(cols))
        self.tbl.setHorizontalHeaderLabels(cols)
        self.tbl.setAlternatingRowColors(True)
        self.tbl.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tbl.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl.setShowGrid(False)
        self.tbl.verticalHeader().setVisible(False)
        h = self.tbl.horizontalHeader()
        h.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        h.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        h.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.tbl.setColumnWidth(0, 90)   # Mã đơn
        self.tbl.setColumnWidth(3, 120)  # Phương thức
        self.tbl.setColumnWidth(4, 110)  # Giá bán
        self.tbl.setColumnWidth(5, 110)  # Đã TT
        self.tbl.setColumnWidth(6, 90)   # Còn lại
        self.tbl.setColumnWidth(7, 130)  # Trạng thái
        self.tbl.setColumnWidth(8, 100)  # Ngày đặt
        self.tbl.selectionModel().selectionChanged.connect(self._on_sel)
        self.tbl.doubleClicked.connect(self._cap_nhat_tt)
        lv.addWidget(self.tbl, 1)
        return w

    def _build_tab_phuongthuc(self):
        w = QWidget(); w.setStyleSheet("background:#f0f4f8;")
        lv = QVBoxLayout(w); lv.setContentsMargins(20, 20, 20, 20); lv.setSpacing(16)

        title = QLabel("💳  Các phương thức thanh toán")
        title.setStyleSheet("font-size:15px;font-weight:700;color:#e2e8f0;background:transparent;")
        lv.addWidget(title)

        grid = QGridLayout(); grid.setSpacing(12)

        methods = [
            ("💵", "Tiền mặt", "Thanh toán trực tiếp tại đại lý.\nKhách hàng mang tiền mặt đến thanh toán 100%.","#4ade80"),
            ("🏦", "Chuyển khoản", "Chuyển khoản qua ngân hàng.\nNhận tiền trong 1-2 ngày làm việc.","#60a5fa"),
            ("📅", "Trả góp", "Thanh toán theo kỳ hạn hàng tháng.\nXem chi tiết tại mục Trả góp.","#fbbf24"),
            ("💳", "Thẻ tín dụng", "Thanh toán bằng thẻ Visa/Mastercard.\nHỗ trợ trả góp 0% lãi suất.","#a78bfa"),
            ("🏧", "Vay NH", "Vay ngân hàng để mua xe.\nLãi suất từ 7-9%/năm.","#f97316"),
        ]

        for i, (icon, name, desc, color) in enumerate(methods):
            card = QWidget()
            card.setStyleSheet(f"""
                QWidget {{
                    background: #ffffff;
                    border: 0.5px solid #dbeafe;
                    border-radius: 14px;
                    border-top: 3px solid {color};
                }}
                QWidget:hover {{
                    border: 0.5px solid {color};
                    border-top: 3px solid {color};
                    background: #f8faff;
                }}
            """)
            cl = QVBoxLayout(card); cl.setContentsMargins(20, 18, 20, 18); cl.setSpacing(8)

            ic = QLabel(f"{icon}  {name}")
            ic.setStyleSheet(f"font-size:16px;font-weight:800;color:{color};background:transparent;border:none;")
            ds = QLabel(desc)
            ds.setStyleSheet("font-size:13px;color:#374151;font-weight:500;background:transparent;border:none;")
            ds.setWordWrap(True)

            # Stats cho phương thức này
            conn = get_conn()
            count = conn.execute(
                "SELECT COUNT(*) FROM don_hang WHERE phuong_thuc=?", (name,)
            ).fetchone()[0]
            total = conn.execute(
                "SELECT SUM(gia_ban_thuc) FROM don_hang WHERE phuong_thuc=?", (name,)
            ).fetchone()[0] or 0
            conn.close()

            st = QLabel(f"📋 {count} đơn hàng  •  💰 {total/1e9:.2f} tỷ ₫")
            st.setStyleSheet(f"font-size:11px;color:{color};background:transparent;border:none;font-weight:600;")

            cl.addWidget(ic); cl.addWidget(ds); cl.addWidget(st)
            grid.addWidget(card, i // 3, i % 3)

        lv.addLayout(grid)
        lv.addStretch()
        return w

    def _build_tab_baocao(self):
        w = QWidget(); w.setStyleSheet("background:#f0f4f8;")
        lv = QVBoxLayout(w); lv.setContentsMargins(20, 16, 20, 16); lv.setSpacing(14)

        title = QLabel("📊  Báo cáo doanh thu theo phương thức thanh toán")
        title.setStyleSheet("font-size:15px;font-weight:700;color:#e2e8f0;background:transparent;")
        lv.addWidget(title)

        # Bảng báo cáo
        cols = ["PHƯƠNG THỨC", "SỐ ĐƠN", "DOANH THU", "ĐÃ TT", "CHƯA TT", "TỶ LỆ"]
        self.tbl_bc = QTableWidget(0, len(cols))
        self.tbl_bc.setHorizontalHeaderLabels(cols)
        self.tbl_bc.setAlternatingRowColors(True)
        self.tbl_bc.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl_bc.setShowGrid(False)
        self.tbl_bc.verticalHeader().setVisible(False)
        h2 = self.tbl_bc.horizontalHeader()
        h2.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tbl_bc.setMaximumHeight(240)
        lv.addWidget(self.tbl_bc)

        sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background:#1e2236;max-height:1px;")
        lv.addWidget(sep)

        # Báo cáo trạng thái
        title2 = QLabel("📋  Báo cáo theo trạng thái thanh toán")
        title2.setStyleSheet("font-size:14px;font-weight:700;color:#e2e8f0;background:transparent;")
        lv.addWidget(title2)

        cols2 = ["TRẠNG THÁI", "SỐ ĐƠN", "TỔNG GIÁ TRỊ", "ĐÃ THU", "CÒN PHẢI THU"]
        self.tbl_bc2 = QTableWidget(0, len(cols2))
        self.tbl_bc2.setHorizontalHeaderLabels(cols2)
        self.tbl_bc2.setAlternatingRowColors(True)
        self.tbl_bc2.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl_bc2.setShowGrid(False)
        self.tbl_bc2.verticalHeader().setVisible(False)
        h3 = self.tbl_bc2.horizontalHeader()
        h3.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tbl_bc2.setMaximumHeight(200)
        lv.addWidget(self.tbl_bc2)
        lv.addStretch()
        return w

    def _load(self):
        conn = get_conn()
        q = self.search.text().strip() if hasattr(self, 'search') else ""
        tt_filter = self.filter_tt.currentText() if hasattr(self, 'filter_tt') else "Tất cả"
        pt_filter = self.filter_pt.currentText() if hasattr(self, 'filter_pt') else "Tất cả PT"

        sql = """
            SELECT dh.id, dh.ma_don, kh.ho_ten, x.hang_xe||' '||x.dong_xe as ten_xe,
                   dh.phuong_thuc, dh.gia_ban_thuc, dh.chiet_khau,
                   COALESCE(dh.trang_thai_tt,'Chưa thanh toán') as trang_thai_tt,
                   COALESCE(dh.so_tien_da_tt, 0) as da_tt,
                   dh.ngay_dat, dh.trang_thai
            FROM don_hang dh
            JOIN khach_hang kh ON dh.kh_id = kh.id
            JOIN xe x ON dh.xe_id = x.id
            WHERE 1=1
        """
        params = []
        if tt_filter != "Tất cả":
            sql += " AND COALESCE(dh.trang_thai_tt,'Chưa thanh toán')=?"; params.append(tt_filter)
        if pt_filter != "Tất cả PT":
            sql += " AND dh.phuong_thuc=?"; params.append(pt_filter)
        if q:
            sql += " AND (dh.ma_don LIKE ? OR kh.ho_ten LIKE ?)"; params += [f"%{q}%", f"%{q}%"]
        sql += " ORDER BY dh.id DESC"

        self._rows = [dict(r) for r in conn.execute(sql, params).fetchall()]

        # Stats
        total = conn.execute("SELECT COUNT(*) FROM don_hang").fetchone()[0]
        da_tt = conn.execute("SELECT COUNT(*) FROM don_hang WHERE trang_thai_tt='Đã thanh toán'").fetchone()[0]
        chua_tt = conn.execute("SELECT COUNT(*) FROM don_hang WHERE COALESCE(trang_thai_tt,'Chưa thanh toán')='Chưa thanh toán'").fetchone()[0]
        mot_phan = conn.execute("SELECT COUNT(*) FROM don_hang WHERE trang_thai_tt='Thanh toán một phần'").fetchone()[0]
        tong_dt = conn.execute("SELECT SUM(so_tien_da_tt) FROM don_hang").fetchone()[0] or 0
        conn.close()

        self._stat_labels["tong_don"].setText(str(total))
        self._stat_labels["da_tt"].setText(str(da_tt))
        self._stat_labels["chua_tt"].setText(str(chua_tt))
        self._stat_labels["mot_phan"].setText(str(mot_phan))
        self._stat_labels["tong_dt"].setText(f"{tong_dt/1e9:.2f} tỷ")

        self._render()
        self._render_baocao()

    def _render(self):
        self.tbl.setRowCount(0)
        for row in self._rows:
            r = self.tbl.rowCount(); self.tbl.insertRow(r)
            self.tbl.setRowHeight(r, 46)

            gia = row["gia_ban_thuc"] - row.get("chiet_khau", 0)
            da_tt = row.get("da_tt", 0)
            con_lai = max(0, gia - da_tt)
            tt = row.get("trang_thai_tt", "Chưa thanh toán")
            pt = row.get("phuong_thuc", "")
            icon = PT_ICONS.get(pt, "💰")

            vals = [
                row["ma_don"],
                row["ho_ten"],
                row["ten_xe"],
                f"{icon} {pt}",
                f"{gia/1e9:.3f} tỷ",
                f"{da_tt/1e9:.3f} tỷ" if da_tt > 0 else "—",
                f"{con_lai/1e9:.3f} tỷ" if con_lai > 0 else "✅ Đủ",
                tt,
                row.get("ngay_dat", ""),
            ]
            for c, val in enumerate(vals):
                item = QTableWidgetItem(val)
                item.setData(Qt.ItemDataRole.UserRole, row["id"])
                if c == 0:
                    item.setForeground(QColor("#1e40af"))
                    item.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
                elif c == 4:
                    item.setForeground(QColor("#059669"))
                    item.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
                elif c == 5:
                    item.setForeground(QColor("#2563eb"))
                    item.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
                elif c == 6:
                    color = "#059669" if con_lai == 0 else "#dc2626"
                    item.setForeground(QColor(color))
                    item.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
                elif c == 7:
                    STATUS_COL_LIGHT = {
                        "Đã thanh toán": "#065f46",
                        "Chưa thanh toán": "#991b1b",
                        "Thanh toán một phần": "#92400e",
                        "Chờ xử lý": "#5b21b6",
                    }
                    item.setForeground(QColor(STATUS_COL_LIGHT.get(tt, "#374151")))
                    item.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
                self.tbl.setItem(r, c, item)

    def _render_baocao(self):
        conn = get_conn()

        # Báo cáo theo phương thức
        self.tbl_bc.setRowCount(0)
        methods = ["Tiền mặt", "Chuyển khoản", "Trả góp", "Thẻ tín dụng", "Vay NH"]
        total_all = conn.execute("SELECT SUM(gia_ban_thuc) FROM don_hang").fetchone()[0] or 1

        for pt in methods:
            data = conn.execute("""
                SELECT COUNT(*), SUM(gia_ban_thuc), SUM(COALESCE(so_tien_da_tt,0))
                FROM don_hang WHERE phuong_thuc=?
            """, (pt,)).fetchone()
            count, dt, da = data[0] or 0, data[1] or 0, data[2] or 0
            if count == 0: continue

            r = self.tbl_bc.rowCount(); self.tbl_bc.insertRow(r)
            self.tbl_bc.setRowHeight(r, 42)
            icon = PT_ICONS.get(pt, "💰")
            ty_le = (dt / total_all * 100) if total_all > 0 else 0

            for c, val in enumerate([
                f"{icon} {pt}",
                str(count),
                f"{dt/1e9:.3f} tỷ",
                f"{da/1e9:.3f} tỷ",
                f"{max(0,dt-da)/1e9:.3f} tỷ",
                f"{ty_le:.1f}%",
            ]):
                item = QTableWidgetItem(val)
                if c == 2:
                    item.setForeground(QColor("#4ade80"))
                    item.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
                elif c == 3:
                    item.setForeground(QColor("#60a5fa"))
                elif c == 4:
                    item.setForeground(QColor("#f87171"))
                elif c == 5:
                    item.setForeground(QColor("#fbbf24"))
                self.tbl_bc.setItem(r, c, item)

        # Báo cáo theo trạng thái
        self.tbl_bc2.setRowCount(0)
        statuses = ["Đã thanh toán", "Chưa thanh toán", "Thanh toán một phần", "Chờ xử lý"]
        for tt in statuses:
            data = conn.execute("""
                SELECT COUNT(*), SUM(gia_ban_thuc), SUM(COALESCE(so_tien_da_tt,0))
                FROM don_hang WHERE COALESCE(trang_thai_tt,'Chưa thanh toán')=?
            """, (tt,)).fetchone()
            count, tong, da = data[0] or 0, data[1] or 0, data[2] or 0
            if count == 0: continue

            r = self.tbl_bc2.rowCount(); self.tbl_bc2.insertRow(r)
            self.tbl_bc2.setRowHeight(r, 42)
            color = TT_COLORS.get(tt, "#94a3b8")

            for c, val in enumerate([
                tt, str(count),
                f"{tong/1e9:.3f} tỷ",
                f"{da/1e9:.3f} tỷ",
                f"{max(0,tong-da)/1e9:.3f} tỷ",
            ]):
                item = QTableWidgetItem(val)
                if c == 0:
                    item.setForeground(QColor(color))
                    item.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
                elif c == 2:
                    item.setForeground(QColor("#4ade80"))
                elif c == 4:
                    item.setForeground(QColor("#f87171"))
                self.tbl_bc2.setItem(r, c, item)

        conn.close()

    def _on_sel(self):
        r = self.tbl.currentRow()
        if 0 <= r < len(self._rows):
            self._sel_id = self._rows[r]["id"]

    def _cap_nhat_tt(self):
        if not self._sel_id:
            QMessageBox.warning(self, "", "Chọn đơn hàng cần cập nhật!"); return
        row = next((r for r in self._rows if r["id"] == self._sel_id), None)
        if row and ThanhToanDialog(self, row).exec():
            self._load()

    def refresh(self):
        self._ensure_columns()
        self._load()



    def _build_tab_ai(self):
        w = QWidget()
        w.setStyleSheet("background:#f0f4f8;")
        lv = QVBoxLayout(w)
        lv.setContentsMargins(20, 20, 20, 20)
        lv.setSpacing(12)
        title = QLabel("🤖  Trợ lý AI AutoViet")
        title.setStyleSheet("font-size:15px;font-weight:700;color:#1e40af;background:transparent;")
        lv.addWidget(title)
        self.ai_output = QTextEdit()
        self.ai_output.setReadOnly(True)
        self.ai_output.setStyleSheet("background:#ffffff;border:1px solid #dbeafe;border-radius:10px;padding:12px;font-size:13px;color:#1e293b;")
        self.ai_output.setPlaceholderText("Câu trả lời của AI sẽ hiển thị ở đây...")
        self.ai_output.setMinimumHeight(200)
        lv.addWidget(self.ai_output, 1)
        hl = QHBoxLayout()
        hl.setSpacing(8)
        self.ai_input = QLineEdit()
        self.ai_input.setStyleSheet("background:#ffffff;border:1px solid #dbeafe;border-radius:8px;padding:10px 14px;font-size:13px;")
        self.ai_input.setPlaceholderText("Hỏi AI: Doanh thu hôm nay? Đơn nào chưa TT?...")
        self.ai_input.returnPressed.connect(self._ai_ask)
        hl.addWidget(self.ai_input, 1)
        btn_ask = QPushButton("🚀 Hỏi AI")
        btn_ask.setStyleSheet("background:#2563eb;color:white;border:none;border-radius:8px;padding:14px 28px;font-size:14px;font-weight:700;")
        btn_ask.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ask.clicked.connect(self._ai_ask)
        hl.addWidget(btn_ask)
        lv.addLayout(hl)
        lbl_quick = QLabel("Câu hỏi nhanh:")
        lbl_quick.setStyleSheet("font-size:12px;color:#64748b;background:transparent;")
        lv.addWidget(lbl_quick)
        quick_hl = QHBoxLayout()
        quick_hl.setSpacing(8)
        for q in ["Doanh thu hôm nay?", "Đơn nào chưa thanh toán?", "Tổng đơn tháng này?", "Khách nào nợ nhiều nhất?"]:
            btn_q = QPushButton(q)
            btn_q.setStyleSheet("background:#eff6ff;color:#1e40af;border:1px solid #bfdbfe;border-radius:6px;padding:6px 10px;font-size:11px;")
            btn_q.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_q.clicked.connect(lambda checked, qq=q: self._ai_quick(qq))
            quick_hl.addWidget(btn_q)
        quick_hl.addStretch()
        lv.addLayout(quick_hl)
        hl2 = QHBoxLayout()
        hl2.setSpacing(8)
        btn_qr = QPushButton("📱 Tạo QR Thanh Toán")
        btn_qr.setStyleSheet("background:#059669;color:white;border:none;border-radius:8px;padding:14px 24px;font-size:13px;font-weight:700;")
        btn_qr.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_qr.clicked.connect(self._tao_qr)
        hl2.addWidget(btn_qr)
        btn_nhac = QPushButton("📨 Soạn Tin Nhắc Nợ")
        btn_nhac.setStyleSheet("background:#d97706;color:white;border:none;border-radius:8px;padding:14px 24px;font-size:13px;font-weight:700;")
        btn_nhac.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_nhac.clicked.connect(self._soan_nhac_no)
        hl2.addWidget(btn_nhac)
        hl2.addStretch()
        lv.addLayout(hl2)
        return w

    def _lay_du_lieu_tt(self):
        try:
            conn = get_conn()
            rows = conn.execute("""
                SELECT dh.ma_don, 
                       kh.ho_ten, 
                       x.hang_xe||' '||x.dong_xe as ten_xe, 
                       COALESCE(dh.so_tien_da_tt, 0) as so_tien_da_tt, 
                       dh.gia_ban_thuc, 
                       COALESCE(dh.trang_thai_tt, 'Chưa thanh toán') as trang_thai_tt
                FROM don_hang dh
                LEFT JOIN khach_hang kh ON dh.kh_id = kh.id
                LEFT JOIN xe x ON dh.xe_id = x.id
                ORDER BY dh.id DESC LIMIT 20
            """).fetchall()
            conn.close()
            result = []
            for r in rows:
                result.append(
                    str(r[0]) + ": " + str(r[1]) + " - " + str(r[2]) +
                    " - Da TT: " + str(int(r[3]) / 1e9) + " / " + str(int(r[4]) / 1e9) + " - " + str(r[5])
                )
            return "\n".join(result)
        except Exception as e:
            return "Khong lay duoc du lieu: " + str(e)

    def _lay_du_lieu_tt_OLD(self):
        try:
            conn = get_conn()
            rows = conn.execute(
                "SELECT d.ma_don, kh.ho_ten, xe.hang_xe || ' ' || xe.dong_xe, "
                "d.so_tien_da_tt, d.gia_ban_thuc, d.trang_thai_tt "
                "FROM don_hang d "
                "LEFT JOIN khach_hang kh ON d.kh_id = kh.id "
                "LEFT JOIN xe ON d.xe_id = xe.id "
                "ORDER BY d.id DESC LIMIT 20"
            ).fetchall()
            conn.close()
            result = []
            for r in rows:
                result.append(
                    str(r[0]) + ": " + str(r[1]) + " - " + str(r[2]) +
                    " - Da TT: " + str(r[3]) + " / " + str(r[4]) + " - " + str(r[5])
                )
            return "\n".join(result)
        except Exception as e:
            return "Khong lay duoc du lieu: " + str(e)

    def _lay_du_lieu_tt_OLD(self):
        try:
            conn = get_conn()
            rows = conn.execute("SELECT ma_don, ho_ten, ten_xe, so_tien_da_tt, gia_ban, trang_thai_tt FROM don_hang ORDER BY id DESC LIMIT 20").fetchall()
            conn.close()
            result = []
            for r in rows:
                result.append(str(r[0]) + ": " + str(r[1]) + " - " + str(r[2]) + " - Da TT: " + str(r[3]) + " / " + str(r[4]) + " - " + str(r[5]))
            return "\n".join(result)
        except Exception as e:
            return "Khong lay duoc du lieu: " + str(e)

    def _ai_ask(self):
        cau_hoi = self.ai_input.text().strip()
        if not cau_hoi:
            return
        self.ai_output.setText("⏳ Đang hỏi AI...")
        du_lieu = self._lay_du_lieu_tt()
        ket_qua = hoi_tro_ly(cau_hoi, du_lieu)
        self.ai_output.setText(ket_qua)
        self.ai_input.clear()


    def _ai_quick(self, cau_hoi):
        self.ai_input.setText(cau_hoi)
        self._ai_ask()

    def _tao_qr(self):
        row = self.tbl.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Chú ý", "Vui lòng chọn một đơn hàng trong tab Danh sách!")
            return
        ma_don = self.tbl.item(row, 0).text()
        ho_ten = self.tbl.item(row, 1).text()
        try:
            con_lai_text = self.tbl.item(row, 6).text().replace(",", "").replace(" đ", "").replace("đ", "").strip()
            so_tien = int(float(con_lai_text))
        except Exception:
            so_tien = 0
        if so_tien <= 0:
            QMessageBox.information(self, "Thông báo", "Đơn này đã thanh toán đủ rồi!")
            return
        try:
            qr_path = tao_ma_qr(ma_don, so_tien, ho_ten)
            QMessageBox.information(self, "QR Thanh Toán",
                "Đã tạo mã QR cho đơn " + ma_don + "\nKhách: " + ho_ten + "\nSố tiền: " + str(so_tien) + " đ\nFile: " + qr_path)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))

    def _soan_nhac_no(self):
        row = self.tbl.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Chú ý", "Vui lòng chọn một đơn hàng trong tab Danh sách!")
            return
        ma_don = self.tbl.item(row, 0).text()
        ho_ten = self.tbl.item(row, 1).text()
        trang_thai = self.tbl.item(row, 7).text()
        if "Đã thanh toán" in trang_thai:
            QMessageBox.information(self, "Thông báo", "Đơn này đã thanh toán đủ rồi!")
            return
        try:
            con_lai_text = self.tbl.item(row, 6).text().replace(",", "").replace(" đ", "").replace("đ", "").strip()
            so_tien = int(float(con_lai_text))
        except Exception:
            so_tien = 0
        self.ai_output.setText("⏳ AI đang soạn tin nhắn...")
        self.tabs.setCurrentIndex(3)
        tin_nhan = soan_nhac_no(ho_ten, ma_don, so_tien)
        self.ai_output.setText("📨 Tin nhắn nhắc nợ:\n\n" + tin_nhan)

class ThanhToanDialog(QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.data = data or {}
        self.setWindowTitle(f"💳 Cập nhật thanh toán — {data.get('ma_don','')}")
        self.setMinimumWidth(500)
        self.setStyleSheet("""
            QDialog { background: #f0f4f8; }
            QLabel { color: #1e40af; font-size: 12px; font-weight: 700;
                     background: transparent; letter-spacing: .8px; }
            QLineEdit, QDoubleSpinBox, QComboBox, QTextEdit {
                background: #ffffff; color: #00274c; border: 0.5px solid #dbeafe;
                border-radius: 8px; padding: 8px 12px; font-size: 14px;
                font-weight: 600; }
            QLineEdit:focus, QDoubleSpinBox:focus, QComboBox:focus { border-color: #2563eb; }
            QPushButton#save { background: #2563eb; color: white; border: none;
                border-radius: 9px; font-size: 14px; font-weight: 700; padding: 11px 24px; }
            QPushButton#save:hover { background: #1d4ed8; }
            QPushButton#cancel { background: #ffffff; color: #64748b;
                border: 0.5px solid #dbeafe; border-radius: 9px;
                font-size: 13px; font-weight: 600; padding: 10px 20px; }
            QPushButton#cancel:hover { background: #eff6ff; color: #1e40af; }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView { background: #ffffff; color: #00274c;
                border: 0.5px solid #dbeafe; selection-background-color: #eff6ff; }
        """)
        self._build()

    def _build(self):
        outer = QVBoxLayout(self); outer.setContentsMargins(24, 20, 24, 20); outer.setSpacing(14)

        title = QLabel(f"💳  CẬP NHẬT THANH TOÁN")
        title.setStyleSheet("font-size:15px;font-weight:700;color:#00274c;background:transparent;")
        sep = QFrame();
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background:#dbeafe;max-height:1px;")
        outer.addWidget(title); outer.addWidget(sep)

        # Thông tin đơn hàng (chỉ đọc)
        gia = self.data.get("gia_ban_thuc", 0) - self.data.get("chiet_khau", 0)
        info = QLabel(
            f"📋  {self.data.get('ma_don','')}  |  "
            f"👤 {self.data.get('ho_ten','')}  |  "
            f"🚗 {self.data.get('ten_xe','')}  |  "
            f"💰 {gia/1e9:.3f} tỷ ₫"
        )
        info.setStyleSheet("font-size:13px;font-weight:600;color:#1e40af;"
                           "background:#eff6ff;border-radius:8px;padding:10px;"
                           "border:0.5px solid #bfdbfe;")
        info.setWordWrap(True)
        outer.addWidget(info)

        def lbl(t):
            l = QLabel(t)
            l.setStyleSheet("color:#4a5568;font-size:11px;font-weight:700;"
                            "background:transparent;letter-spacing:.8px;")
            return l

        form = QFormLayout(); form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        # Phương thức
        self.f_pt = QComboBox()
        self.f_pt.addItems(["Tiền mặt", "Chuyển khoản", "Trả góp", "Thẻ tín dụng", "Vay NH"])
        idx = self.f_pt.findText(self.data.get("phuong_thuc", "Tiền mặt"))
        if idx >= 0: self.f_pt.setCurrentIndex(idx)

        # Trạng thái
        self.f_tt = QComboBox()
        self.f_tt.addItems(["Chưa thanh toán", "Thanh toán một phần", "Đã thanh toán", "Chờ xử lý"])
        idx2 = self.f_tt.findText(self.data.get("trang_thai_tt", "Chưa thanh toán"))
        if idx2 >= 0: self.f_tt.setCurrentIndex(idx2)
        self.f_tt.currentTextChanged.connect(self._on_tt_change)

        # Số tiền đã thanh toán
        self.f_da_tt = QDoubleSpinBox()
        self.f_da_tt.setRange(0, 100e9)
        self.f_da_tt.setSingleStep(50e6)
        self.f_da_tt.setDecimals(0)
        self.f_da_tt.setSuffix(" ₫")
        self.f_da_tt.setValue(float(self.data.get("da_tt", 0)))
        self.f_da_tt.valueChanged.connect(self._update_conlai)

        # Còn lại (readonly)
        self.f_con_lai = QLineEdit()
        self.f_con_lai.setReadOnly(True)
        self.f_con_lai.setStyleSheet("color:#dc2626;font-weight:700;background:#fff1f2;"
                                     "border:0.5px solid #fecaca;"
                                     "border-radius:8px;padding:8px 12px;font-size:14px;")

        # Ghi chú
        self.f_gchu = QTextEdit()
        self.f_gchu.setMaximumHeight(70)
        self.f_gchu.setPlaceholderText("Ghi chú thanh toán...")
        self.f_gchu.setPlainText(self.data.get("ghi_chu_tt", "") or "")

        form.addRow(lbl("PHƯƠNG THỨC"), self.f_pt)
        form.addRow(lbl("TRẠNG THÁI TT"), self.f_tt)
        form.addRow(lbl("ĐÃ THANH TOÁN"), self.f_da_tt)
        form.addRow(lbl("CÒN PHẢI THU"), self.f_con_lai)
        form.addRow(lbl("GHI CHÚ"), self.f_gchu)
        outer.addLayout(form)

        self._update_conlai()

        bh = QHBoxLayout(); bh.addStretch()
        bc = QPushButton("Huỷ bỏ"); bc.setObjectName("cancel"); bc.clicked.connect(self.reject)
        bs = QPushButton("💾  Lưu"); bs.setObjectName("save"); bs.clicked.connect(self._save)
        bh.addWidget(bc); bh.addWidget(bs); outer.addLayout(bh)

    def _on_tt_change(self, tt):
        gia = self.data.get("gia_ban_thuc", 0) - self.data.get("chiet_khau", 0)
        if tt == "Đã thanh toán":
            self.f_da_tt.setValue(gia)
        elif tt == "Chưa thanh toán":
            self.f_da_tt.setValue(0)
    def _update_conlai(self): 
        gia = (
            self.data.get("gia_ban_thuc", 0)
            - self.data.get("chiet_khau", 0)
        )

        con = gia - self.f_da_tt.value()

        self.f_con_lai.setText(f"{con:,.0f} ₫")

        if con < 0:
            self.f_con_lai.setStyleSheet(
                "color:#dc2626;font-weight:700;"
                "background:#fef2f2;"
                "border:1px solid #fecaca;"
                "border-radius:8px;"
                "padding:8px 12px;font-size:14px;"
            )
        elif con == 0:
                self.f_con_lai.setStyleSheet(
                "color:#065f46;font-weight:700;"
                "background:#f0fdf4;"
                "border:0.5px solid #a7f3d0;"
                "border-radius:8px;padding:8px 12px;font-size:14px;"
            )
        else:
            self.f_con_lai.setStyleSheet(
                "color:#f87171;background:#13151c;"
                "border:1px solid #2c3050;"
                "border-radius:8px;padding:8px 12px;font-size:13px;"
            )

    def _save(self):
        gia = (
            self.data.get("gia_ban_thuc", 0)
            - self.data.get("chiet_khau", 0)
        )

        so_tien = self.f_da_tt.value()

        # Kiểm tra số tiền thanh toán
        ok, message = validate_payment(gia, so_tien)

        if not ok:
            QMessageBox.warning(
                self,
                "Cảnh báo",
                message
            )
            return

        conn = get_conn()

        try:
            # Lưu database
            conn.execute("""
                UPDATE don_hang SET
                    phuong_thuc=?,
                    trang_thai_tt=?,
                    so_tien_da_tt=?,
                    ghi_chu_tt=?
                WHERE id=?
            """, (
                self.f_pt.currentText(),
                self.f_tt.currentText(),
                int(self.f_da_tt.value()),
                self.f_gchu.toPlainText(),
                self.data["id"]
            ))

            conn.commit()

        # =========================
        # HIỆN POPUP THÀNH CÔNG
        # =========================

            if self.f_tt.currentText() == "Đã thanh toán":

                dlg = PaymentSuccessDialog(
                    customer=self.data.get("ho_ten", ""),
                    car=self.data.get("ten_xe", ""),
                    amount=f"{self.f_da_tt.value():,.0f} ₫",
                    order_id=self.data.get("ma_don", ""),
                    method=self.f_pt.currentText()
                )

                dlg.exec()

            else:
                QMessageBox.information(
                    self,
                    "Thông báo",
                    "Đã cập nhật trạng thái thanh toán!"
                )

            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))

        finally:
            conn.close()

    def _build_tab_ai(self):
        w = QWidget()
        w.setStyleSheet("background:#f0f4f8;")
        lv = QVBoxLayout(w)
        lv.setContentsMargins(20, 20, 20, 20)
        lv.setSpacing(12)

        title = QLabel("🤖  Trợ lý AI AutoViet")
        title.setStyleSheet("font-size:15px;font-weight:700;color:#1e40af;background:transparent;")
        lv.addWidget(title)

        self.ai_output = QTextEdit()
        self.ai_output.setReadOnly(True)
        self.ai_output.setStyleSheet("background:#ffffff;border:1px solid #dbeafe;border-radius:10px;padding:12px;font-size:13px;color:#1e293b;")
        self.ai_output.setPlaceholderText("Câu trả lời của AI sẽ hiển thị ở đây...")
        self.ai_output.setMinimumHeight(200)
        lv.addWidget(self.ai_output, 1)

        hl = QHBoxLayout()
        hl.setSpacing(8)
        self.ai_input = QLineEdit()
        self.ai_input.setStyleSheet("background:#ffffff;border:1px solid #dbeafe;border-radius:8px;padding:10px 14px;font-size:13px;")
        self.ai_input.setPlaceholderText("Hỏi AI: Doanh thu hôm nay? Đơn nào chưa TT?...")
        self.ai_input.returnPressed.connect(self._ai_ask)
        hl.addWidget(self.ai_input, 1)

        btn_ask = QPushButton("🚀 Hỏi AI")
        btn_ask.setStyleSheet("background:#2563eb;color:white;border:none;border-radius:8px;padding:14px 28px;font-size:14px;font-weight:700;")
        btn_ask.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ask.clicked.connect(self._ai_ask)
        hl.addWidget(btn_ask)
        lv.addLayout(hl)

        lbl_quick = QLabel("Câu hỏi nhanh:")
        lbl_quick.setStyleSheet("font-size:12px;color:#64748b;background:transparent;")
        lv.addWidget(lbl_quick)

        quick_hl = QHBoxLayout()
        quick_hl.setSpacing(8)
        for q in ["Doanh thu hôm nay?", "Đơn nào chưa thanh toán?", "Tổng đơn tháng này?", "Khách nào nợ nhiều nhất?"]:
            btn_q = QPushButton(q)
            btn_q.setStyleSheet("background:#eff6ff;color:#1e40af;border:1px solid #bfdbfe;border-radius:6px;padding:6px 10px;font-size:11px;")
            btn_q.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_q.clicked.connect(lambda checked, qq=q: self._ai_quick(qq))
            quick_hl.addWidget(btn_q)
        quick_hl.addStretch()
        lv.addLayout(quick_hl)

        hl2 = QHBoxLayout()
        hl2.setSpacing(8)

        btn_qr = QPushButton("📱 Tạo QR Thanh Toán")
        btn_qr.setStyleSheet("background:#059669;color:white;border:none;border-radius:8px;padding:14px 24px;font-size:13px;font-weight:700;")
        btn_qr.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_qr.clicked.connect(self._tao_qr)
        hl2.addWidget(btn_qr)

        btn_nhac = QPushButton("📨 Soạn Tin Nhắc Nợ")
        btn_nhac.setStyleSheet("background:#d97706;color:white;border:none;border-radius:8px;padding:14px 24px;font-size:13px;font-weight:700;")
        btn_nhac.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_nhac.clicked.connect(self._soan_nhac_no)
        hl2.addWidget(btn_nhac)

        hl2.addStretch()
        lv.addLayout(hl2)
        return w

    def _lay_du_lieu_tt(self):
        try:
            conn = get_conn()
            rows = conn.execute("SELECT ma_don, ho_ten, ten_xe, so_tien_da_tt, gia_ban, trang_thai_tt FROM don_hang ORDER BY id DESC LIMIT 20").fetchall()
            conn.close()
            result = []
            for r in rows:
                result.append(str(r[0]) + ": " + str(r[1]) + " - " + str(r[2]) + " - Da TT: " + str(r[3]) + " / " + str(r[4]) + " - " + str(r[5]))
            return "\n".join(result)
        except Exception as e:
            return "Khong lay duoc du lieu: " + str(e)

    def _ai_ask(self):
        cau_hoi = self.ai_input.text().strip()
        if not cau_hoi:
            return
        self.ai_output.setText("⏳ Đang hỏi AI...")
        du_lieu = self._lay_du_lieu_tt()
        ket_qua = hoi_tro_ly(cau_hoi, du_lieu)
        self.ai_output.setText(ket_qua)
        self.ai_input.clear()


    def _ai_quick(self, cau_hoi):
        self.ai_input.setText(cau_hoi)
        self._ai_ask()

    def _tao_qr(self):
        row = self.tbl.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Chú ý", "Vui lòng chọn một đơn hàng trong tab Danh sách!")
            return
        ma_don = self.tbl.item(row, 0).text()
        ho_ten = self.tbl.item(row, 1).text()
        try:
            con_lai_text = self.tbl.item(row, 6).text().replace(",", "").replace(" đ", "").replace("đ", "").strip()
            so_tien = int(float(con_lai_text))
        except Exception:
            so_tien = 0
        if so_tien <= 0:
            QMessageBox.information(self, "Thông báo", "Đơn này đã thanh toán đủ rồi!")
            return
        try:
            qr_path = tao_ma_qr(ma_don, so_tien, ho_ten)
            QMessageBox.information(self, "QR Thanh Toán",
                "Đã tạo mã QR cho đơn " + ma_don + "\nKhách: " + ho_ten + "\nSố tiền: " + str(so_tien) + " đ\nFile: " + qr_path)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))

    def _soan_nhac_no(self):
        row = self.tbl.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Chú ý", "Vui lòng chọn một đơn hàng trong tab Danh sách!")
            return
        ma_don = self.tbl.item(row, 0).text()
        ho_ten = self.tbl.item(row, 1).text()
        trang_thai = self.tbl.item(row, 7).text()
        if "Đã thanh toán" in trang_thai:
            QMessageBox.information(self, "Thông báo", "Đơn này đã thanh toán đủ rồi!")
            return
        try:
            con_lai_text = self.tbl.item(row, 6).text().replace(",", "").replace(" đ", "").replace("đ", "").strip()
            so_tien = int(float(con_lai_text))
        except Exception:
            so_tien = 0
        self.ai_output.setText("⏳ AI đang soạn tin nhắn...")
        self.tabs.setCurrentIndex(3)
        tin_nhan = soan_nhac_no(ho_ten, ma_don, so_tien)
        self.ai_output.setText("📨 Tin nhắn nhắc nợ:\n\n" + tin_nhan)
