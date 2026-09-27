"""
views/dich_vu_view_new.py — Giao diện Dịch vụ thiết kế lại hoàn toàn
THAY THẾ phần DichVuView trong other_views.py
Copy file này vào views/ với tên: dich_vu_view.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QDialog, QFormLayout, QComboBox, QMessageBox,
    QHeaderView, QFrame, QScrollArea, QGridLayout, QDoubleSpinBox,
    QTextEdit, QTableWidget, QTableWidgetItem, QTabWidget,
    QApplication, QProgressBar, QSplitter
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QColor, QFont, QLinearGradient, QPainter, QBrush
import pandas as pd
from database import get_conn
from datetime import datetime

STYLE = """
QWidget { font-family: 'Segoe UI', Arial; }

QWidget#dv_toolbar {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #0f1f35, stop:1 #1e3a5f);
    border-bottom: 1px solid #1e3a5f;
}

QWidget#stat_card {
    background: #ffffff;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
}

QPushButton#btn_lap {
    background: #2563eb;
    color: white; border: none; border-radius: 10px;
    font-size: 13px; font-weight: 700; padding: 10px 18px;
}
QPushButton#btn_lap:hover { background: #1d4ed8; }

QPushButton#btn_pdf {
    background: #eff6ff; color: #2563eb;
    border: 1px solid #bfdbfe; border-radius: 8px;
    font-size: 12px; font-weight: 600; padding: 8px 14px;
}
QPushButton#btn_pdf:hover { background: #dbeafe; }

QPushButton#btn_update {
    background: #f0fdf4; color: #16a34a;
    border: 1px solid #86efac; border-radius: 8px;
    font-size: 12px; font-weight: 600; padding: 8px 14px;
}
QPushButton#btn_update:hover { background: #dcfce7; }

QPushButton#btn_excel {
    background: #f0fdf4; color: #16a34a;
    border: 1px solid #86efac; border-radius: 8px;
    font-size: 12px; font-weight: 600; padding: 8px 14px;
}
QPushButton#btn_excel:hover { background: #dcfce7; }

QPushButton#btn_del {
    background: #fff1f2; color: #dc2626;
    border: 1px solid #fecaca; border-radius: 8px;
    font-size: 12px; padding: 8px 14px;
}
QPushButton#btn_del:hover { background: #fee2e2; }

QPushButton#btn_view_all, QPushButton#btn_view_card {
    background: #f8fafc; color: #64748b;
    border: 1px solid #e2e8f0; border-radius: 8px;
    font-size: 12px; padding: 8px 14px;
}
QPushButton#btn_view_all:checked, QPushButton#btn_view_card:checked {
    background: #eff6ff; color: #2563eb; border-color: #2563eb;
}

QLineEdit#dv_search {
    background: #ffffff; color: #1e293b;
    border: 1px solid #e2e8f0; border-radius: 10px;
    padding: 9px 16px; font-size: 13px; min-width: 260px;
}
QLineEdit#dv_search:focus { border-color: #2563eb; background: #eff6ff; }

QComboBox#dv_filter {
    background: #ffffff; color: #334155;
    border: 1px solid #e2e8f0; border-radius: 8px;
    padding: 8px 12px; font-size: 12px; min-width: 130px;
}
QComboBox#dv_filter::drop-down { border: none; }
QComboBox#dv_filter QAbstractItemView {
    background: #ffffff; color: #1e293b;
    selection-background-color: #eff6ff;
}

QTableWidget {
    background: #ffffff; alternate-background-color: #f8fafc;
    gridline-color: #f1f5f9; border: none;
    selection-background-color: #eff6ff;
    font-size: 13px;
}
QTableWidget::item { padding: 8px 12px; color: #1e293b; border-bottom: 1px solid #f1f5f9; }
QTableWidget::item:selected { background: #eff6ff; color: #2563eb; }
QHeaderView::section {
    background: #f8fafc; color: #2563eb;
    font-size: 12px; font-weight: 800; letter-spacing: 1px;
    padding: 12px; border: none; border-bottom: 2px solid #2563eb;
}

QDialog { background: #f0f4f8; }
QWidget#dlg_card {
    background: #ffffff;
    border-radius: 14px;
    border: 1px solid #e2e8f0;
}
QLabel#dlg_title {
    font-size: 16px; font-weight: 800;
    color: #0f1f35; background: transparent;
}
QLabel#dlg_field {
    font-size: 11px; font-weight: 700; color: #64748b;
    background: transparent; letter-spacing: 1px;
}
QLineEdit, QTextEdit, QDoubleSpinBox, QComboBox#dlg_combo {
    background: #f8fafc; color: #1e293b;
    border: 1.5px solid #e2e8f0; border-radius: 8px;
    padding: 9px 12px; font-size: 13px;
}
QLineEdit:focus, QTextEdit:focus,
QDoubleSpinBox:focus, QComboBox#dlg_combo:focus {
    border-color: #2563eb; background: #eff6ff;
}
QPushButton#dlg_save {
    background: #2563eb; color: white; border: none;
    border-radius: 9px; font-size: 14px; font-weight: 700;
    padding: 12px 24px;
}
QPushButton#dlg_save:hover { background: #1d4ed8; }
QPushButton#dlg_cancel {
    background: #f8fafc; color: #64748b;
    border: 1px solid #e2e8f0; border-radius: 9px;
    font-size: 13px; padding: 10px 20px;
}
QPushButton#dlg_cancel:hover { background: #f1f5f9; }
"""

LOAI_DV_LIST = [
    "🔧 Bảo dưỡng định kỳ",
    "🔩 Thay dầu & lọc",
    "🛞 Thay lốp xe",
    "🔋 Thay ắc quy",
    "❄️ Bảo dưỡng điều hòa",
    "🚿 Rửa xe & đánh bóng",
    "🔬 Kiểm tra tổng quát",
    "📋 Đăng kiểm xe",
    "⚙️ Sửa chữa động cơ",
    "🎨 Sơn & đồng phục",
    "🔌 Sửa điện - điện tử",
    "💨 Bơm lốp & cân bằng",
    "🧰 Sửa chữa khác",
]

STATUS_CONFIG = {
    "Tiếp nhận":       ("#fbbf24", "#1c1500", "⏳"),
    "Đang thực hiện":  ("#60a5fa", "#0c1a2e", "⚙️"),
    "Hoàn thành":      ("#4ade80", "#052e16", "✅"),
    "Chờ phụ tùng":    ("#f97316", "#1c0d00", "📦"),
    "Huỷ":             ("#f87171", "#1c0505", "❌"),
}


class DichVuView(QWidget):
    def __init__(self, current_user=None):
        super().__init__()
        self.setObjectName("page_dich_vu")
        self.setStyleSheet(STYLE)
        self.current_user = current_user or {"role": "admin"}
        self._rows = []
        self._sel_id = None
        self._view_mode = "table"  # table | card
        self._build()
        self._load()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── TOOLBAR ──────────────────────────────────────────────────────
        tb = QWidget();
        tb.setObjectName("dv_toolbar")
        tbh = QHBoxLayout(tb)
        tbh.setContentsMargins(12, 8, 12, 8)
        tbh.setSpacing(5)

        self.btn_lap = QPushButton("➕ Lập phiếu");
        self.btn_lap.setObjectName("btn_lap")
        self.btn_pdf = QPushButton("🖨️ In PDF");
        self.btn_pdf.setObjectName("btn_pdf")
        self.btn_update = QPushButton("🔄 Cập nhật");
        self.btn_update.setObjectName("btn_update")
        self.btn_excel = QPushButton("📊 Excel");
        self.btn_excel.setObjectName("btn_excel")
        self.btn_del = QPushButton("🗑 Xoá");
        self.btn_del.setObjectName("btn_del")

        sep = QFrame();
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setStyleSheet("background:#1e2236; max-width:1px; margin:4px 2px;")

        self.btn_card = QPushButton("⊞ Card");
        self.btn_card.setObjectName("btn_view_card")
        self.btn_table = QPushButton("☰ Bảng");
        self.btn_table.setObjectName("btn_view_all")
        self.btn_card.setCheckable(True);
        self.btn_table.setCheckable(True)
        self.btn_table.setChecked(True)

        self.filter_loai = QComboBox();
        self.filter_loai.setObjectName("dv_filter")
        self.filter_loai.setFixedWidth(120)
        self.filter_loai.addItem("Tất cả loại DV")
        for l in LOAI_DV_LIST: self.filter_loai.addItem(l)

        self.filter_tt = QComboBox();
        self.filter_tt.setObjectName("dv_filter")
        self.filter_tt.setFixedWidth(110)
        self.filter_tt.addItems(["Tất cả TT", "Tiếp nhận", "Đang thực hiện", "Hoàn thành", "Chờ phụ tùng", "Huỷ"])

        self.search = QLineEdit();
        self.search.setObjectName("dv_search")
        self.search.setPlaceholderText("🔍 Tìm mã phiếu, xe, KH...")
        self.search.setFixedWidth(200)

        for b in [self.btn_lap, self.btn_pdf, self.btn_update, self.btn_excel, self.btn_del]:
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setFixedHeight(34)
            tbh.addWidget(b)
        tbh.addWidget(sep)
        for b in [self.btn_card, self.btn_table]:
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setFixedHeight(34)
            tbh.addWidget(b)
        tbh.addStretch(1)
        tbh.addWidget(self.filter_loai)
        tbh.addWidget(self.filter_tt)
        tbh.addWidget(self.search)
        root.addWidget(tb)

        # ── STAT CARDS ───────────────────────────────────────────────────
        stat_w = QWidget()
        stat_w.setStyleSheet("background:#f0f4f8; padding:12px 16px 8px;")
        stat_h = QHBoxLayout(stat_w); stat_h.setSpacing(10)

        self.sc_tiep    = self._stat("⏳","Tiếp nhận","0","#fbbf24","stat_tiepnhan")
        self.sc_dang    = self._stat("⚙️","Đang thực hiện","0","#60a5fa","stat_dangthuc")
        self.sc_hoan    = self._stat("✅","Hoàn thành","0","#4ade80","stat_hoanhanh")
        self.sc_dt      = self._stat("💰","Doanh thu DV","0 ₫","#a78bfa","stat_doanhthu")
        for sc in [self.sc_tiep,self.sc_dang,self.sc_hoan,self.sc_dt]:
            stat_h.addWidget(sc)
        root.addWidget(stat_w)

        # ── CONTENT AREA ─────────────────────────────────────────────────
        self.content = QWidget()
        self.content_lv = QVBoxLayout(self.content)
        self.content_lv.setContentsMargins(0,0,0,0)
        self.content_lv.setSpacing(0)
        root.addWidget(self.content, 1)

        # Table view
        self._build_table()
        # Card view
        self._build_card_view()

        self._show_table()

        # Connects
        self.btn_lap.clicked.connect(self._lap_phieu)
        self.btn_pdf.clicked.connect(self._in_pdf)
        self.btn_update.clicked.connect(self._cap_nhat_tt)
        self.btn_excel.clicked.connect(self._export)
        self.btn_del.clicked.connect(self._delete)
        self.btn_table.clicked.connect(self._show_table)
        self.btn_card.clicked.connect(self._show_card)
        self.search.textChanged.connect(lambda t: self._load(t.strip()))
        self.filter_tt.currentTextChanged.connect(lambda _: self._load(self.search.text()))
        self.filter_loai.currentTextChanged.connect(lambda _: self._load(self.search.text()))

    def _stat(self, icon, label, val, color, obj):
        w = QWidget(); w.setObjectName("stat_card")
        lv = QVBoxLayout(w); lv.setContentsMargins(14,10,14,10); lv.setSpacing(3)
        w2 = QWidget(); w2.setObjectName(obj)
        lv2 = QVBoxLayout(w2); lv2.setContentsMargins(14,10,14,10); lv2.setSpacing(3)
        li = QLabel(f"{icon}  {label}")
        li.setStyleSheet("font-size:11px;color:#64748b;font-weight:700;background:transparent;letter-spacing:.8px;")
        lv2 = QLabel(val)
        lv2.setStyleSheet(f"font-size:20px;font-weight:800;color:{color};background:transparent;")
        lv.addWidget(li); lv.addWidget(lv2)
        w._val = lv2
        w.setStyleSheet(f"QWidget#stat_card{{background:#ffffff;border-radius:12px;border:1px solid #e2e8f0;border-left:4px solid {color};}}")
        return w

    def _build_table(self):
        cols = ["MÃ PHIẾU", "XE", "KHÁCH HÀNG", "NHÂN VIÊN KTV",
                "LOẠI DỊCH VỤ", "MÔ TẢ", "CHI PHÍ", "TRẠNG THÁI", "NGÀY NHẬN"]
        self.tbl = QTableWidget(0, len(cols))
        self.tbl.setHorizontalHeaderLabels(cols)
        self.tbl.setAlternatingRowColors(True)
        self.tbl.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tbl.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl.setShowGrid(False)
        self.tbl.verticalHeader().setVisible(False)

        # ✅ Căn chỉnh cột tự động fit nội dung
        h = self.tbl.horizontalHeader()
        h.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # MÃ PHIẾU
        h.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # XE - rộng
        h.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # KHÁCH HÀNG - rộng
        h.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # NHÂN VIÊN KTV
        h.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # LOẠI DỊCH VỤ
        h.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)  # MÔ TẢ - rộng
        h.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # CHI PHÍ
        h.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)  # TRẠNG THÁI
        h.setSectionResizeMode(8, QHeaderView.ResizeMode.ResizeToContents)  # NGÀY NHẬN

        self.tbl.selectionModel().selectionChanged.connect(self._on_sel)
        self.tbl.doubleClicked.connect(self._xem_chitiet)

    def _build_card_view(self):
        self.scroll_card = QScrollArea()
        self.scroll_card.setWidgetResizable(True)
        self.scroll_card.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_card.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.card_container = QWidget()
        self.card_grid = QGridLayout(self.card_container)
        self.card_grid.setContentsMargins(14,14,14,14)
        self.card_grid.setSpacing(12)
        self.scroll_card.setWidget(self.card_container)

    def _show_table(self):
        self.btn_table.setChecked(True); self.btn_card.setChecked(False)
        self._view_mode = "table"
        # Clear content
        while self.content_lv.count():
            item = self.content_lv.takeAt(0)
            if item.widget(): item.widget().setParent(None)
        self.content_lv.addWidget(self.tbl)
        self._render()

    def _show_card(self):
        self.btn_card.setChecked(True); self.btn_table.setChecked(False)
        self._view_mode = "card"
        while self.content_lv.count():
            item = self.content_lv.takeAt(0)
            if item.widget(): item.widget().setParent(None)
        self.content_lv.addWidget(self.scroll_card)
        self._render_cards()

    def _load(self, q=""):
        conn = get_conn()
        sql = """SELECT dv.*,
                 x.hang_xe||' '||x.dong_xe as ten_xe, x.ma_xe,
                 kh.ho_ten as ten_kh, kh.so_dt as sdt_kh,
                 nv.ho_ten as ten_nv
                 FROM dich_vu dv
                 LEFT JOIN xe x ON dv.xe_id=x.id
                 LEFT JOIN khach_hang kh ON dv.kh_id=kh.id
                 LEFT JOIN nhan_vien nv ON dv.nv_id=nv.id"""
        p = []
        conds = []
        if q:
            conds.append("(dv.ma_dv LIKE ? OR x.hang_xe LIKE ? OR x.dong_xe LIKE ? OR kh.ho_ten LIKE ?)")
            p += [f"%{q}%"]*4
        tt = self.filter_tt.currentText()
        if tt != "Tất cả TT":
            conds.append("dv.trang_thai=?"); p.append(tt)
        loai = self.filter_loai.currentText()
        if loai != "Tất cả loại DV":
            # Remove emoji prefix
            loai_clean = loai.split(" ",1)[1] if " " in loai else loai
            conds.append("dv.loai_dv LIKE ?"); p.append(f"%{loai_clean}%")
        if conds:
            sql += " WHERE " + " AND ".join(conds)
        sql += " ORDER BY dv.id DESC"
        self._rows = [dict(r) for r in conn.execute(sql, p).fetchall()]

        # Stats
        all_rows = [dict(r) for r in conn.execute(
            "SELECT trang_thai, chi_phi FROM dich_vu").fetchall()]
        conn.close()

        cnt_tiep = sum(1 for r in all_rows if r["trang_thai"]=="Tiếp nhận")
        cnt_dang = sum(1 for r in all_rows if r["trang_thai"]=="Đang thực hiện")
        cnt_hoan = sum(1 for r in all_rows if r["trang_thai"]=="Hoàn thành")
        dt = sum(r["chi_phi"] or 0 for r in all_rows if r["trang_thai"]=="Hoàn thành")

        self.sc_tiep._val.setText(str(cnt_tiep))
        self.sc_dang._val.setText(str(cnt_dang))
        self.sc_hoan._val.setText(str(cnt_hoan))
        self.sc_dt._val.setText(f"{dt/1e6:.1f} triệu")

        if self._view_mode == "table":
            self._render()
        else:
            self._render_cards()

    def _render(self):
        self.tbl.setRowCount(0)
        STATUS_COL = {
            "Tiếp nhận":"#fbbf24","Đang thực hiện":"#60a5fa",
            "Hoàn thành":"#4ade80","Chờ phụ tùng":"#f97316","Huỷ":"#f87171"
        }
        for row in self._rows:
            r = self.tbl.rowCount(); self.tbl.insertRow(r)
            self.tbl.setRowHeight(r, 50)
            vals = [
                row.get("ma_dv",""),
                row.get("ten_xe","") or "—",
                row.get("ten_kh","") or "—",
                row.get("ten_nv","") or "—",
                row.get("loai_dv","") or "—",
                row.get("mo_ta","") or "—",
                f"{int(row.get('chi_phi',0) or 0):,} ₫",
                row.get("trang_thai",""),
                row.get("ngay_nhan","") or "—",
            ]
            for c, val in enumerate(vals):
                item = QTableWidgetItem(val)
                # ✅ Font chung: to hơn, đậm hơn
                item.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
                item.setForeground(QColor("#1e293b"))

                if c == 0:  # MÃ PHIẾU
                    item.setForeground(QColor("#2563eb"))
                    item.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
                elif c == 4:  # CHI PHÍ
                    item.setForeground(QColor("#16a34a"))
                    item.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
                elif c == 5:  # TRẠNG THÁI
                    status_color = {"Hoàn thành": "#16a34a", "Đang thực hiện": "#2563eb", "Tiếp nhận": "#d97706"}.get(
                        val, "#64748b")
                    item.setForeground(QColor(status_color))
                    item.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))

                self.tbl.setItem(r, c, item)

    def _render_cards(self):
        # Clear
        while self.card_grid.count():
            item = self.card_grid.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        cols = 3
        for idx, row in enumerate(self._rows):
            card = self._make_card(row)
            self.card_grid.addWidget(card, idx//cols, idx%cols)
        self.card_grid.setRowStretch(len(self._rows)//cols+1, 1)

    def _make_card(self, row):
        tt = row.get("trang_thai","Tiếp nhận")
        cfg = STATUS_CONFIG.get(tt, ("#94a3b8","#1a1d28","❓"))
        color, bg, icon = cfg

        card = QWidget()
        card.setStyleSheet(f"""
            QWidget {{
                background:{bg};
                border-radius:14px;
                border:1px solid rgba{QColor(color).getRgb()[:3]+(60,)};
            }}
        """)
        card.setFixedHeight(220)
        lv = QVBoxLayout(card); lv.setContentsMargins(16,14,16,14); lv.setSpacing(6)

        # Header
        hr = QHBoxLayout()
        ma = QLabel(row.get("ma_dv",""))
        ma.setStyleSheet("font-size:13px;font-weight:800;color:#a78bfa;background:transparent;")
        status_lbl = QLabel(f"{icon} {tt}")
        status_lbl.setStyleSheet(
            f"background:rgba{QColor(color).getRgb()[:3]+(30,)};color:{color};"
            f"border-radius:8px;padding:3px 10px;font-size:11px;font-weight:700;")
        hr.addWidget(ma); hr.addStretch(); hr.addWidget(status_lbl)
        lv.addLayout(hr)

        # Xe
        xe = QLabel(f"🚗  {row.get('ten_xe','N/A')}")
        xe.setStyleSheet("font-size:13px;font-weight:700;color:#e2e8f0;background:transparent;")
        xe.setWordWrap(True)
        lv.addWidget(xe)

        # Separator
        sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background:rgba{QColor(color).getRgb()[:3]+(40,)};max-height:1px;")
        lv.addWidget(sep)

        # Info grid
        def info_row(icon2, val):
            rw = QHBoxLayout()
            li = QLabel(icon2); li.setStyleSheet("font-size:12px;background:transparent;min-width:20px;")
            lv2 = QLabel(str(val)); lv2.setStyleSheet("font-size:12px;color:#9ca3af;background:transparent;")
            lv2.setWordWrap(True)
            rw.addWidget(li); rw.addWidget(lv2,1); return rw

        lv.addLayout(info_row("👤", row.get("ten_kh","—")))
        lv.addLayout(info_row("🔧", row.get("loai_dv","—")))

        # Footer
        fr = QHBoxLayout()
        chi_phi = QLabel(f"💰 {int(row.get('chi_phi',0) or 0):,} ₫")
        chi_phi.setStyleSheet(f"font-size:13px;font-weight:700;color:{color};background:transparent;")
        ngay = QLabel(f"📅 {row.get('ngay_nhan','')}")
        ngay.setStyleSheet("font-size:11px;color:#4a5568;background:transparent;")
        fr.addWidget(chi_phi); fr.addStretch(); fr.addWidget(ngay)
        lv.addLayout(fr)
        lv.addStretch()

        # Nút
        br = QHBoxLayout(); br.setSpacing(6)
        btn_ct = QPushButton("Chi tiết"); btn_ct.setObjectName("btn_pdf")
        btn_ct.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ct.clicked.connect(lambda _, r=row: self._xem_chitiet_row(r))
        btn_up = QPushButton("Cập nhật"); btn_up.setObjectName("btn_update")
        btn_up.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_up.clicked.connect(lambda _, r=row: self._cap_nhat_tt_row(r["id"]))
        br.addWidget(btn_ct,1); br.addWidget(btn_up,1)
        lv.addLayout(br)

        return card

    def _on_sel(self):
        r = self.tbl.currentRow()
        if 0 <= r < len(self._rows):
            self._sel_id = self._rows[r]["id"]

    def _check(self, action="thao tác"):
        if not self._sel_id:
            QMessageBox.warning(self,"","Chọn phiếu cần " + action + "!")
            return False
        return True

    def _lap_phieu(self):
        if DichVuDialog(self).exec(): self._load(self.search.text())

    def _in_pdf(self):
        if self._view_mode=="table" and not self._check("in PDF"): return
        try:
            from invoice_pdf import in_phieu_dich_vu
            fname = in_phieu_dich_vu(self._sel_id)
            QMessageBox.information(self,"✅ In phiếu thành công!",
                f"File: {fname}\n\nMở file để in hoặc gửi cho khách!")
            os.startfile(fname)
        except Exception as e:
            QMessageBox.critical(self,"Lỗi",str(e))

    def _cap_nhat_tt(self):
        if not self._check("cập nhật"): return
        self._cap_nhat_tt_row(self._sel_id)

    def _cap_nhat_tt_row(self, dv_id):
        from PyQt6.QtWidgets import QInputDialog
        status, ok = QInputDialog.getItem(self,"🔄 Cập nhật trạng thái","Chọn trạng thái mới:",
            ["Tiếp nhận","Chờ phụ tùng","Đang thực hiện","Hoàn thành","Huỷ"],0,False)
        if ok:
            conn = get_conn()
            conn.execute("UPDATE dich_vu SET trang_thai=? WHERE id=?",(status,dv_id))
            conn.commit(); conn.close()
            self._load(self.search.text())

    def _delete(self):
        if not self._check("xoá"): return
        if QMessageBox.question(self,"Xác nhận","Xoá phiếu dịch vụ này?",
            QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No
        )==QMessageBox.StandardButton.Yes:
            conn=get_conn(); conn.execute("DELETE FROM dich_vu WHERE id=?",(self._sel_id,))
            conn.commit(); conn.close(); self._sel_id=None
            self._load(self.search.text())

    def _export(self):
        import openpyxl
        from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
        from openpyxl.utils import get_column_letter
        import datetime

        conn = get_conn()
        rows = conn.execute("""
            SELECT dv.ma_dv, x.hang_xe||' '||x.dong_xe, kh.ho_ten,
                   dv.loai_dv, dv.mo_ta, dv.chi_phi, dv.trang_thai, dv.ngay_nhan
            FROM dich_vu dv
            LEFT JOIN xe x ON dv.xe_id=x.id
            LEFT JOIN khach_hang kh ON dv.kh_id=kh.id
            ORDER BY dv.id DESC
        """).fetchall()
        conn.close()

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Dịch vụ"

        ws.merge_cells("A1:H1")
        ws["A1"] = "BÁO CÁO DỊCH VỤ BẢO DƯỠNG — AUTOVIET"
        ws["A1"].font = Font(name="Segoe UI", size=14, bold=True, color="FFFFFF")
        ws["A1"].fill = PatternFill("solid", fgColor="006064")
        ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[1].height = 36

        ws.merge_cells("A2:H2")
        ws["A2"] = f"Ngày xuất: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}"
        ws["A2"].font = Font(name="Segoe UI", size=10, italic=True, color="64748B")
        ws["A2"].alignment = Alignment(horizontal="right")
        ws.row_dimensions[2].height = 20

        headers = ["MÃ PHIẾU", "XE", "KHÁCH HÀNG", "LOẠI DV", "MÔ TẢ", "CHI PHÍ", "TRẠNG THÁI", "NGÀY NHẬN"]
        col_widths = [12, 28, 22, 22, 30, 16, 16, 14]
        thin = Side(style="thin", color="B2DFDB")
        border = Border(left=thin, right=thin, top=thin, bottom=thin)

        for i, (h, w) in enumerate(zip(headers, col_widths), 1):
            cell = ws.cell(row=3, column=i, value=h)
            cell.font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor="00838F")
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = border
            ws.column_dimensions[get_column_letter(i)].width = w
        ws.row_dimensions[3].height = 28

        fill_white = PatternFill("solid", fgColor="FFFFFF")
        fill_alt   = PatternFill("solid", fgColor="E0F7FA")
        font_data  = Font(name="Segoe UI", size=11, color="1E293B")
        font_ma    = Font(name="Segoe UI", size=11, bold=True, color="006064")

        STATUS_COLOR = {
            "Hoàn thành":      "059669",
            "Đang thực hiện":  "2563EB",
            "Tiếp nhận":       "D97706",
            "Chờ phụ tùng":    "EA580C",
            "Huỷ":             "DC2626",
        }

        for ri, row in enumerate(rows, 4):
            fill = fill_white if ri % 2 == 0 else fill_alt
            ws.row_dimensions[ri].height = 24
            for ci, val in enumerate(row, 1):
                cell = ws.cell(row=ri, column=ci, value=val)
                cell.fill = fill
                cell.border = border
                cell.alignment = Alignment(vertical="center",
                    horizontal="center" if ci in (1, 6, 7, 8) else "left")
                if ci == 1:
                    cell.font = font_ma
                elif ci == 6:
                    cell.font = Font(name="Segoe UI", size=11, bold=True, color="059669")
                    # Format số tiền
                    if val:
                        cell.value = int(val)
                        cell.number_format = '#,##0 "₫"'
                elif ci == 7:
                    color = STATUS_COLOR.get(str(val), "64748B")
                    cell.font = Font(name="Segoe UI", size=11, bold=True, color=color)
                else:
                    cell.font = font_data

        ws.freeze_panes = "A4"
        fname = f"BaoCao_DichVu_{datetime.datetime.now().strftime('%d%m%Y_%H%M')}.xlsx"
        wb.save(fname)
        QMessageBox.information(self, "Excel", f"✅ Đã xuất: {fname}")

    def _xem_chitiet(self):
        r = self.tbl.currentRow()
        if 0 <= r < len(self._rows):
            self._xem_chitiet_row(self._rows[r])

    def _xem_chitiet_row(self, row):
        ChiTietDVDialog(self, row).exec()

    def refresh(self): self._load(self.search.text())


class DichVuDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Lập phiếu dịch vụ")
        self.setMinimumWidth(540)
        self.setStyleSheet(STYLE)
        self._build()

    def _build(self):
        outer = QVBoxLayout(self); outer.setContentsMargins(20,20,20,20)
        card = QWidget(); card.setObjectName("dlg_card")
        cl = QVBoxLayout(card); cl.setContentsMargins(24,20,24,20); cl.setSpacing(14)

        # Title
        title = QLabel("🔧  LẬP PHIẾU DỊCH VỤ"); title.setObjectName("dlg_title")
        sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background:#e2e8f0;max-height:1px;")
        cl.addWidget(title); cl.addWidget(sep)

        conn = get_conn()
        xe_rows = conn.execute("SELECT id,ma_xe,hang_xe,dong_xe FROM xe").fetchall()
        kh_rows = conn.execute("SELECT id,ma_kh,ho_ten FROM khach_hang").fetchall()
        nv_rows = conn.execute("SELECT id,ma_nv,ho_ten FROM nhan_vien WHERE trang_thai='Đang làm'").fetchall()
        cnt = conn.execute("SELECT COUNT(*) FROM dich_vu").fetchone()[0]
        # Dò tìm mã chưa tồn tại để tránh trùng (UNIQUE constraint), giống lỗi đã gặp ở Đơn hàng
        so_dv = cnt + 1
        ma_dv_moi = f"DV{so_dv:03d}"
        while conn.execute("SELECT id FROM dich_vu WHERE ma_dv=?", (ma_dv_moi,)).fetchone():
            so_dv += 1
            ma_dv_moi = f"DV{so_dv:03d}"
        conn.close()

        form = QFormLayout(); form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        def lbl(t):
            l=QLabel(t); l.setObjectName("dlg_field"); return l

        self.f_ma = QLineEdit(ma_dv_moi)
        self.f_xe = QComboBox(); self.f_xe.setObjectName("dlg_combo")
        for r in xe_rows: self.f_xe.addItem(f"{r[1]} — {r[2]} {r[3]}",r[0])
        self.f_kh = QComboBox(); self.f_kh.setObjectName("dlg_combo")
        for r in kh_rows: self.f_kh.addItem(f"{r[1]} — {r[2]}",r[0])
        self.f_nv = QComboBox(); self.f_nv.setObjectName("dlg_combo")
        for r in nv_rows: self.f_nv.addItem(f"{r[1]} — {r[2]}",r[0])
        self.f_loai = QComboBox(); self.f_loai.setObjectName("dlg_combo")
        for l in LOAI_DV_LIST: self.f_loai.addItem(l)
        self.f_mota = QTextEdit(); self.f_mota.setPlaceholderText("Mô tả chi tiết công việc cần làm...")
        self.f_mota.setMaximumHeight(80)
        self.f_cp = QDoubleSpinBox()
        self.f_cp.setRange(0,100e6); self.f_cp.setSingleStep(50000)
        self.f_cp.setDecimals(0); self.f_cp.setSuffix(" ₫")
        self.f_tt = QComboBox(); self.f_tt.setObjectName("dlg_combo")
        self.f_tt.addItems(["Tiếp nhận","Đang thực hiện","Hoàn thành"])

        for l,w in [("Mã phiếu *",self.f_ma),("Xe *",self.f_xe),
                    ("Khách hàng",self.f_kh),("Kỹ thuật viên",self.f_nv),
                    ("Loại dịch vụ *",self.f_loai),("Mô tả công việc",self.f_mota),
                    ("Chi phí (₫)",self.f_cp),("Trạng thái",self.f_tt)]:
            form.addRow(lbl(l), w)
        cl.addLayout(form)

        bh = QHBoxLayout(); bh.addStretch()
        btn_c = QPushButton("Huỷ bỏ"); btn_c.setObjectName("dlg_cancel")
        btn_c.clicked.connect(self.reject)
        btn_s = QPushButton("🔧  Lập phiếu"); btn_s.setObjectName("dlg_save")
        btn_s.clicked.connect(self._save); btn_s.setDefault(True)
        bh.addWidget(btn_c); bh.addWidget(btn_s)
        cl.addLayout(bh)
        outer.addWidget(card)

    def _save(self):
        ma = self.f_ma.text().strip()
        if not ma: QMessageBox.warning(self,"","Nhập mã phiếu!"); return
        # Clean emoji from loai_dv
        loai = self.f_loai.currentText()
        if " " in loai: loai = loai.split(" ",1)[1]
        conn = get_conn()
        try:
            conn.execute(
                "INSERT INTO dich_vu(ma_dv,xe_id,kh_id,nv_id,loai_dv,mo_ta,chi_phi,trang_thai) VALUES(?,?,?,?,?,?,?,?)",
                (ma,self.f_xe.currentData(),self.f_kh.currentData(),
                 self.f_nv.currentData(),loai,self.f_mota.toPlainText(),
                 self.f_cp.value(),self.f_tt.currentText()))
            conn.commit()
            QMessageBox.information(self,"✅ Thành công!","Lập phiếu dịch vụ thành công!")
            self.accept()
        except Exception as e: QMessageBox.critical(self,"Lỗi",str(e))
        finally: conn.close()


class ChiTietDVDialog(QDialog):
    def __init__(self, parent=None, row=None):
        super().__init__(parent)
        self.row = row
        self.setWindowTitle(f"Chi tiết — {row.get('ma_dv','')}")
        self.setMinimumWidth(500)
        self.setStyleSheet("""
                    QDialog { background: #f8fafc; }
                    QWidget#dlg_card { background: #ffffff; border-radius: 14px; border: 1px solid #e2e8f0; }
                    QLabel#dlg_title { font-size:16px; font-weight:800; color:#0f172a; background:transparent; }
                    QLabel#dlg_field { font-size:11px; font-weight:700; color:#64748b; background:transparent; letter-spacing:1px; }
                    QPushButton#btn_pdf { background:#eff6ff; color:#2563eb; border:1px solid #bfdbfe; border-radius:8px; font-size:13px; font-weight:700; padding:10px 20px; }
                    QPushButton#btn_pdf:hover { background:#2563eb; color:#ffffff; }
                    QPushButton#dlg_cancel { background:#f1f5f9; color:#64748b; border:1px solid #e2e8f0; border-radius:8px; font-size:13px; padding:10px 20px; }
                    QPushButton#dlg_cancel:hover { background:#e2e8f0; }
                """)
        self._build()

    def _build(self):
        tt = self.row.get("trang_thai","")
        cfg = STATUS_CONFIG.get(tt,("#94a3b8","#1a1d28","❓"))
        color, bg, icon = cfg

        outer = QVBoxLayout(self); outer.setContentsMargins(20,20,20,20)
        card = QWidget(); card.setObjectName("dlg_card")
        cl = QVBoxLayout(card); cl.setContentsMargins(24,20,24,20); cl.setSpacing(10)

        # Header
        hr = QHBoxLayout()
        ma = QLabel(f"🔧  {self.row.get('ma_dv','')}"); ma.setObjectName("dlg_title")
        st = QLabel(f"{icon} {tt}")
        st.setStyleSheet(f"background:rgba{QColor(color).getRgb()[:3]+(30,)};color:{color};"
                         f"border-radius:8px;padding:4px 12px;font-size:12px;font-weight:700;")
        hr.addWidget(ma); hr.addStretch(); hr.addWidget(st)
        cl.addLayout(hr)

        sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background:#e2e8f0;max-height:1px;")
        cl.addWidget(sep)

        def row_info(key, val, vc="#1e293b"):
            rw = QHBoxLayout()
            lk = QLabel(key);
            lk.setFixedWidth(140)
            lk.setStyleSheet(
                "font-size:11px;font-weight:700;color:#64748b;background:transparent;letter-spacing:0.5px;")
            lv = QLabel(str(val))
            lv.setStyleSheet(f"color:{vc};font-size:13px;background:transparent;font-weight:600;")
            lv.setWordWrap(True)
            rw.addWidget(lk);
            rw.addWidget(lv, 1);
            return rw

        for k, v, c in [
            ("Mã phiếu", self.row.get("ma_dv", ""), "#7c3aed"),
            ("Xe", self.row.get("ten_xe", "N/A"), "#0f172a"),
            ("Mã xe", self.row.get("ma_xe", "N/A"), "#475569"),
            ("Khách hàng", self.row.get("ten_kh", "N/A"), "#0f172a"),
            ("SĐT khách", self.row.get("sdt_kh", "N/A"), "#059669"),
            ("Kỹ thuật viên", self.row.get("ten_nv", "N/A"), "#0f172a"),
            ("Loại DV", self.row.get("loai_dv", "N/A"), "#2563eb"),
            ("Mô tả", self.row.get("mo_ta", "") or "—", "#475569"),
            ("Ngày nhận", self.row.get("ngay_nhan", ""), "#0f172a"),
            ("Chi phí", f"{int(self.row.get('chi_phi', 0) or 0):,} ₫", "#059669"),
        ]: cl.addLayout(row_info(k, v, c))

        sep2 = QFrame(); sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet("background:#252840;max-height:1px;")
        cl.addWidget(sep2)

        bh = QHBoxLayout(); bh.addStretch()
        btn_pdf = QPushButton("🖨️  In phiếu PDF"); btn_pdf.setObjectName("btn_pdf")
        btn_pdf.clicked.connect(self._in_pdf)
        btn_c = QPushButton("Đóng"); btn_c.setObjectName("dlg_cancel")
        btn_c.clicked.connect(self.reject)
        bh.addWidget(btn_pdf); bh.addWidget(btn_c)
        cl.addLayout(bh)
        outer.addWidget(card)

    def _in_pdf(self):
        try:
            from invoice_pdf import in_phieu_dich_vu
            fname = in_phieu_dich_vu(self.row["id"])
            QMessageBox.information(self,"✅ OK",f"Đã xuất: {fname}")
            os.startfile(fname)
        except Exception as e: QMessageBox.critical(self,"Lỗi",str(e))
