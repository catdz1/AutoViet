"""
views/xe_catalog_view.py — Giao diện xem xe như showroom
✅ CẬP NHẬT: Nền TRẮNG, sidebar GIỮA NGUYÊN xanh đen
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QGridLayout, QFrame, QLineEdit, QComboBox,
    QDialog, QMessageBox, QFileDialog, QApplication
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QFont, QColor
from database import get_conn

# ✅ CARD STYLE - Nền TRẮNG + border xanh dương
CARD_STYLE = """
QWidget#xe_card {
    background: #ffffff;
    border-radius: 12px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}
QWidget#xe_card:hover {
    border: 2px solid #2563eb;
    background: #f9fafb;
    box-shadow: 0 4px 12px rgba(37,99,235,0.15);
}
QLabel#car_name {
    font-size: 13px; font-weight: 700;
    color: #111827; background: transparent;
}
QLabel#car_price {
    font-size: 15px; font-weight: 800;
    color: #2563eb; background: transparent;
}
QLabel#car_info {
    font-size: 11px; color: #6b7280;
    background: transparent;
}
QLabel#car_status_ok {
    background: #dcfce7; color: #15803d;
    border-radius: 6px; padding: 4px 10px;
    font-size: 11px; font-weight: 700;
}
QLabel#car_status_no {
    background: #fee2e2; color: #991b1b;
    border-radius: 6px; padding: 4px 10px;
    font-size: 11px; font-weight: 700;
}
QLabel#car_status_dep {
    background: #fef3c7; color: #92400e;
    border-radius: 6px; padding: 4px 10px;
    font-size: 11px; font-weight: 700;
}
QPushButton#btn_detail {
    background: #f3f4f6; color: #2563eb;
    border: 1px solid #e5e7eb;
    border-radius: 8px; font-size: 12px; font-weight: 700;
    padding: 8px 12px;
}
QPushButton#btn_detail:hover {
    background: #e5e7eb; color: #1d4ed8;
    border: 1px solid #2563eb;
}
QPushButton#btn_buy {
    background: #2563eb; color: #ffffff; border: none;
    border-radius: 8px; font-size: 12px; font-weight: 700;
    padding: 8px 12px;
}
QPushButton#btn_buy:hover { 
    background: #1d4ed8; 
}
QPushButton#btn_buy:disabled {
    background: #d1d5db; color: #9ca3af;
}
"""


class XeCatalogView(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("page_catalog")
        self._all_rows = []
        self._active_tab = "all"
        self._build()
        self._load()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Toolbar ──────────────────────────────────────────────────────
        # ✅ Toolbar TRẮNG thay vì đen
        tb = QWidget()
        tb.setStyleSheet("background:#ffffff; border-bottom: 1px solid #e5e7eb;")
        tbh = QHBoxLayout(tb)
        tbh.setContentsMargins(16, 10, 16, 10)
        tbh.setSpacing(10)

        title = QLabel("🚗  Showroom — Danh sách xe hơi")
        title.setStyleSheet("font-size:16px; font-weight:700; color:#111827; background:transparent;")

        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍 Tìm xe theo tên, hãng, màu sắc...")
        self.search.setMinimumWidth(280)
        self.search.setStyleSheet("""
            QLineEdit {
                background: #f9fafb;
                border: 1px solid #e5e7eb;
                border-radius: 8px; padding: 8px 12px;
                color: #111827; font-size: 12px;
            }
            QLineEdit:focus { 
                border: 2px solid #2563eb;
                background: #ffffff;
            }
        """)
        self.search.textChanged.connect(self._filter)

        combo_style = """
            QComboBox {
                background: #f9fafb;
                border: 1px solid #e5e7eb;
                border-radius: 8px; padding: 8px 12px;
                color: #111827; font-size: 12px;
            }
            QComboBox::drop-down { border: none; width: 20px; }
            QComboBox QAbstractItemView {
                background: #ffffff; color: #111827;
                border: 1px solid #2563eb;
                selection-background-color: #dbeafe;
            }
        """

        self.filter_hang = QComboBox()
        self.filter_hang.setMinimumWidth(140)
        self.filter_hang.addItem("Tất cả hãng")
        self.filter_hang.setStyleSheet(combo_style)
        self.filter_hang.currentTextChanged.connect(self._filter)

        self.filter_tt = QComboBox()
        self.filter_tt.setMinimumWidth(130)
        self.filter_tt.addItems(["Tất cả trạng thái", "Còn hàng", "Đặt cọc", "Đã bán"])
        self.filter_tt.setStyleSheet(combo_style)
        self.filter_tt.currentTextChanged.connect(self._filter)

        tbh.addWidget(title)
        tbh.addStretch()
        tbh.addWidget(self.filter_hang)
        tbh.addWidget(self.filter_tt)
        tbh.addWidget(self.search)
        root.addWidget(tb)

        # ── Tab bar ──────────────────────────────────────────────────────
        # ✅ Tab bar TRẮNG
        tab_bar = QWidget()
        tab_bar.setStyleSheet("background:#ffffff; border-bottom:2px solid #e5e7eb;")
        tbh2 = QHBoxLayout(tab_bar)
        tbh2.setContentsMargins(16, 0, 16, 0)
        tbh2.setSpacing(0)

        # ✅ Tab active xanh dương #2563eb
        TAB_ON = (
            "QPushButton{background:transparent;color:#2563eb;"
            "border:none;border-bottom:3px solid #2563eb;"
            "font-size:13px;font-weight:700;padding:12px 24px;}"
        )
        TAB_OFF = (
            "QPushButton{background:transparent;color:#6b7280;"
            "border:none;border-bottom:3px solid transparent;"
            "font-size:13px;font-weight:600;padding:12px 24px;}"
            "QPushButton:hover{color:#111827;}"
        )

        self.tab_all  = QPushButton("🚗  Tất cả xe")
        self.tab_new  = QPushButton("🆕  Xe mới về")
        self.tab_hot  = QPushButton("⭐  Xe nổi bật")
        self.tab_sale = QPushButton("🏷️  Đang giảm giá")
        self._active_tab = "all"

        for btn in [self.tab_all, self.tab_new, self.tab_hot, self.tab_sale]:
            tbh2.addWidget(btn)
        tbh2.addStretch()

        self.tab_all.setStyleSheet(TAB_ON)
        self.tab_new.setStyleSheet(TAB_OFF)
        self.tab_hot.setStyleSheet(TAB_OFF)
        self.tab_sale.setStyleSheet(TAB_OFF)

        self.tab_all.clicked.connect(lambda: self._switch_tab("all"))
        self.tab_new.clicked.connect(lambda: self._switch_tab("new"))
        self.tab_hot.clicked.connect(lambda: self._switch_tab("hot"))
        self.tab_sale.clicked.connect(lambda: self._switch_tab("sale"))

        root.addWidget(tab_bar)

        # ── Grid scroll area ──────────────────────────────────────────────
        # ✅ Nền TRẮNG thay vì đen
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("background:#f9fafb;")

        self.grid_widget = QWidget()
        self.grid_widget.setStyleSheet(CARD_STYLE + "QWidget{background:#f9fafb;}")
        self.grid = QGridLayout(self.grid_widget)
        self.grid.setContentsMargins(16, 16, 16, 16)
        self.grid.setSpacing(14)

        scroll.setWidget(self.grid_widget)
        root.addWidget(scroll, 1)

        # ── Status bar ────────────────────────────────────────────────────
        # ✅ Status bar TRẮNG
        self.status_bar = QLabel()
        self.status_bar.setStyleSheet(
            "background:#ffffff; color:#6b7280; font-size:12px;"
            "padding:8px 16px; border-top:1px solid #e5e7eb;")
        root.addWidget(self.status_bar)

    def _load(self):
        conn = get_conn()
        self._all_rows = [dict(r) for r in conn.execute(
            "SELECT * FROM xe ORDER BY id DESC").fetchall()]
        hangs = sorted(set(r["hang_xe"] for r in self._all_rows))
        self.filter_hang.clear()
        self.filter_hang.addItem("Tất cả hãng")
        for h in hangs:
            self.filter_hang.addItem(h)
        conn.close()
        self._render(self._all_rows)

    def _switch_tab(self, tab):
        self._active_tab = tab
        TAB_ON = (
            "QPushButton{background:transparent;color:#2563eb;"
            "border:none;border-bottom:3px solid #2563eb;"
            "font-size:13px;font-weight:700;padding:12px 24px;}"
        )
        TAB_OFF = (
            "QPushButton{background:transparent;color:#6b7280;"
            "border:none;border-bottom:3px solid transparent;"
            "font-size:13px;font-weight:600;padding:12px 24px;}"
            "QPushButton:hover{color:#111827;}"
        )
        self.tab_all.setStyleSheet(TAB_ON  if tab == "all"  else TAB_OFF)
        self.tab_new.setStyleSheet(TAB_ON  if tab == "new"  else TAB_OFF)
        self.tab_hot.setStyleSheet(TAB_ON  if tab == "hot"  else TAB_OFF)
        self.tab_sale.setStyleSheet(TAB_ON if tab == "sale" else TAB_OFF)
        self._filter()

    def _filter(self):
        from datetime import datetime, timedelta
        q    = self.search.text().strip().lower()
        hang = self.filter_hang.currentText()
        tt   = self.filter_tt.currentText()
        rows = self._all_rows

        tab = getattr(self, '_active_tab', 'all')
        if tab == "new":
            cutoff = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            rows = [r for r in rows if (r.get("ngay_nhap") or "") >= cutoff]
        elif tab == "hot":
            rows = [r for r in rows if int(r.get("noi_bat") or 0) == 1]
        elif tab == "sale":
            rows = [r for r in rows if float(r.get("giam_gia") or 0) > 0]

        if q:
            rows = [r for r in rows if
                    q in r["hang_xe"].lower() or
                    q in r["dong_xe"].lower() or
                    q in (r.get("mau_sac", "") or "").lower()]
        if hang != "Tất cả hãng":
            rows = [r for r in rows if r["hang_xe"] == hang]
        if tt != "Tất cả trạng thái":
            rows = [r for r in rows if r["trang_thai"] == tt]
        self._render(rows)

    def _render(self, rows):
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        cols = 3
        self.status_bar.setText(
            f"  Hiển thị: {len(rows)} xe  |  "
            f"Còn hàng: {sum(1 for r in rows if r['trang_thai']=='Còn hàng')}  |  "
            f"Đặt cọc: {sum(1 for r in rows if r['trang_thai']=='Đặt cọc')}  |  "
            f"Đã bán: {sum(1 for r in rows if r['trang_thai']=='Đã bán')}  ")

        for idx, row in enumerate(rows):
            card = self._make_card(row)
            self.grid.addWidget(card, idx // cols, idx % cols)

        self.grid.setRowStretch(len(rows) // cols + 1, 1)

    def _make_card(self, row):
        card = QWidget()
        card.setObjectName("xe_card")
        card.setFixedWidth(360)
        card.setFixedHeight(300)
        lv = QVBoxLayout(card)
        lv.setContentsMargins(0, 0, 0, 12)
        lv.setSpacing(0)

        # ── Ảnh xe ──────────────────────────────────────────────────────
        img_w = QWidget()
        img_w.setStyleSheet("background:#f3f4f6; border-radius:12px 12px 0 0;")
        img_lv = QVBoxLayout(img_w)
        img_lv.setContentsMargins(0, 0, 0, 0)
        img_lv.setAlignment(Qt.AlignmentFlag.AlignCenter)

        img_lbl = QLabel()
        img_lbl.setFixedSize(360, 180)
        img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        img_lbl.setStyleSheet("background:#f3f4f6; border-radius:12px 12px 0 0;")

        img_path = row.get("anh_url", "") or ""
        if img_path:
            img_path = img_path.replace("/", "\\")
        if img_path and os.path.exists(img_path):
            pix = QPixmap(img_path).scaled(
                360, 180,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation)
            img_lbl.setPixmap(pix)
        else:
            img_lbl.setText(f"🚗\n{row['hang_xe']}\n{row['dong_xe']}")
            img_lbl.setStyleSheet(
                "background:qlineargradient(x1:0,y1:0,x2:1,y2:1,"
                "stop:0 #dbeafe,stop:1 #e0f2fe);"
                "color:#2563eb; font-size:16px; font-weight:700;"
                "border-radius:12px 12px 0 0;")
            img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        img_lv.addWidget(img_lbl)

        # ── Badge ────────────────────────────────────────────────────────
        from datetime import datetime, timedelta
        badge_row = QHBoxLayout()
        badge_row.setContentsMargins(8, 8, 8, 0)
        badge_row.setSpacing(4)
        badge_row.setAlignment(Qt.AlignmentFlag.AlignLeft)

        cutoff = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        if (row.get("ngay_nhap") or "") >= cutoff:
            b = QLabel("🆕 Mới về")
            b.setStyleSheet(
                "background:#dbeafe; color:#1e40af;"
                "border-radius:6px; padding:3px 8px;"
                "font-size:10px; font-weight:700;")
            badge_row.addWidget(b)

        if row.get("noi_bat", 0):
            b = QLabel("⭐ Nổi bật")
            b.setStyleSheet(
                "background:#fef3c7; color:#b45309;"
                "border-radius:6px; padding:3px 8px;"
                "font-size:10px; font-weight:700;")
            badge_row.addWidget(b)

        if (row.get("giam_gia") or 0) > 0:
            b = QLabel(f"🏷️ -{int(row['giam_gia'])}%")
            b.setStyleSheet(
                "background:#fee2e2; color:#991b1b;"
                "border-radius:6px; padding:3px 8px;"
                "font-size:10px; font-weight:700;")
            badge_row.addWidget(b)

        badge_row.addStretch()
        img_lv.addLayout(badge_row)
        lv.addWidget(img_w)

        # ── Thông tin ────────────────────────────────────────────────────
        info_w = QWidget()
        info_w.setStyleSheet("background:#ffffff;")
        info_lv = QVBoxLayout(info_w)
        info_lv.setContentsMargins(14, 8, 14, 0)
        info_lv.setSpacing(4)

        h_row = QHBoxLayout()
        name = QLabel(f"{row['hang_xe']} {row['dong_xe']}")
        name.setObjectName("car_name")
        name.setWordWrap(True)
        tt = row["trang_thai"]
        obj = ("car_status_ok" if tt == "Còn hàng"
               else "car_status_dep" if tt == "Đặt cọc"
               else "car_status_no")
        status_lbl = QLabel(tt)
        status_lbl.setObjectName(obj)
        h_row.addWidget(name, 1)
        h_row.addWidget(status_lbl)
        info_lv.addLayout(h_row)

        price_row = QHBoxLayout()
        price = QLabel(f"{row['gia_ban']/1e9:.2f} tỷ ₫")
        price.setObjectName("car_price")
        year = QLabel(f"📅 {row['nam_sx']}  |  🎨 {row.get('mau_sac','') or 'N/A'}")
        year.setObjectName("car_info")
        price_row.addWidget(price)
        price_row.addStretch()
        price_row.addWidget(year)
        info_lv.addLayout(price_row)

        lv.addWidget(info_w)
        lv.addStretch()

        # ── Nút ─────────────────────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(14, 0, 14, 0)
        btn_row.setSpacing(8)

        btn_detail = QPushButton("🔍 Chi tiết")
        btn_detail.setObjectName("btn_detail")
        btn_detail.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_detail.clicked.connect(lambda _, r=row: self._show_detail(r))

        btn_buy = QPushButton("🛒 Đặt mua")
        btn_buy.setObjectName("btn_buy")
        btn_buy.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_buy.setEnabled(tt == "Còn hàng")
        btn_buy.clicked.connect(lambda _, r=row: self._dat_mua(r))

        btn_row.addWidget(btn_detail, 1)
        btn_row.addWidget(btn_buy, 1)
        lv.addLayout(btn_row)

        return card

    def _show_detail(self, row):
        dlg = XeDetailDialog(self, row)
        dlg.exec()

    def _dat_mua(self, row):
        from views.don_hang_view import DonHangDialog
        dlg = DonHangDialog(self)
        for i in range(dlg.f_xe.count()):
            if dlg.f_xe.itemData(i) == row["id"]:
                dlg.f_xe.setCurrentIndex(i)
                break
        if dlg.exec():
            self._load()
            mw = self.window()
            if hasattr(mw, "_refresh_status"):
                mw._refresh_status()

    def refresh(self):
        self._load()


class XeDetailDialog(QDialog):
    def __init__(self, parent=None, row=None):
        super().__init__(parent)
        self.row = row
        self.setWindowTitle(f"Chi tiết xe — {row['hang_xe']} {row['dong_xe']}")
        self.setMinimumWidth(560)
        self.setStyleSheet("""
            QDialog { background:#ffffff; }
            QLabel  { background:transparent; color:#111827; font-size:13px; }
            QLabel#key {
                color:#6b7280; font-size:11px; font-weight:700;
                letter-spacing:1px;
            }
            QPushButton {
                background:#f3f4f6; color:#6b7280;
                border:1px solid #e5e7eb; border-radius:8px;
                padding:8px 16px; font-size:13px;
            }
            QPushButton:hover { background:#e5e7eb; }
            QPushButton#btn_img {
                background:#dbeafe; color:#2563eb;
                border:1px solid #2563eb;
            }
            QPushButton#btn_img:hover { background:#bfdbfe; color:#1d4ed8; }
            QPushButton#btn_buy {
                background:#2563eb; color:white; border:none;
                font-weight:700; font-size:14px; padding:12px;
            }
            QPushButton#btn_buy:hover { background:#1d4ed8; }
            QPushButton#btn_buy:disabled { background:#d1d5db; color:#9ca3af; }
        """)
        self._build()

    def _build(self):
        lv = QVBoxLayout(self)
        lv.setContentsMargins(0, 0, 0, 20)
        lv.setSpacing(0)
        row = self.row

        self.img_lbl = QLabel()
        self.img_lbl.setFixedHeight(240)
        self.img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._load_img()
        lv.addWidget(self.img_lbl)

        btn_img = QPushButton("📷  Thêm / Đổi ảnh xe")
        btn_img.setObjectName("btn_img")
        btn_img.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_img.clicked.connect(self._change_img)
        btn_img.setFixedHeight(36)
        lv.addWidget(btn_img)

        info_w = QWidget()
        info_lv = QVBoxLayout(info_w)
        info_lv.setContentsMargins(24, 16, 24, 0)
        info_lv.setSpacing(2)

        title = QLabel(f"{row['hang_xe']} {row['dong_xe']}")
        title.setStyleSheet("font-size:20px; font-weight:800; color:#111827;")
        price = QLabel(f"💰 {row['gia_ban']/1e9:.3f} tỷ ₫")
        price.setStyleSheet("font-size:18px; font-weight:700; color:#2563eb; margin:4px 0;")
        info_lv.addWidget(title)
        info_lv.addWidget(price)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background:#e5e7eb; max-height:1px; margin:8px 0;")
        info_lv.addWidget(sep)

        grid = QGridLayout()
        grid.setSpacing(8)
        fields = [
            ("Mã xe",      row.get("ma_xe", "")),
            ("Năm SX",     str(row.get("nam_sx", ""))),
            ("Màu sắc",    row.get("mau_sac", "") or "—"),
            ("Số khung",   row.get("so_khung", "") or "—"),
            ("Số máy",     row.get("so_may", "") or "—"),
            ("Tình trạng", row.get("tinh_trang", "") or "—"),
            ("Trạng thái", row.get("trang_thai", "")),
            ("Giá nhập",   f"{int(row.get('gia_nhap', 0)):,} ₫"),
        ]
        for i, (k, v) in enumerate(fields):
            lk = QLabel(k)
            lk.setObjectName("key")
            lv2 = QLabel(v)
            if k == "Trạng thái":
                col = {
                    "Còn hàng": "#15803d",
                    "Đặt cọc":  "#b45309",
                    "Đã bán":   "#991b1b"
                }.get(v, "#6b7280")
                lv2.setStyleSheet(f"color:{col}; font-weight:700;")
            grid.addWidget(lk,  i // 2, (i % 2) * 2)
            grid.addWidget(lv2, i // 2, (i % 2) * 2 + 1)
        info_lv.addLayout(grid)

        if row.get("mo_ta"):
            sep2 = QFrame()
            sep2.setFrameShape(QFrame.Shape.HLine)
            sep2.setStyleSheet("background:#e5e7eb; max-height:1px; margin:8px 0;")
            info_lv.addWidget(sep2)
            mo_ta = QLabel(f"📝 {row['mo_ta']}")
            mo_ta.setWordWrap(True)
            mo_ta.setStyleSheet("color:#6b7280; font-size:12px;")
            info_lv.addWidget(mo_ta)

        lv.addWidget(info_w)

        btn_w = QWidget()
        btn_lv = QHBoxLayout(btn_w)
        btn_lv.setContentsMargins(24, 12, 24, 0)
        btn_close = QPushButton("Đóng")
        btn_close.clicked.connect(self.reject)
        self.btn_buy = QPushButton("🛒  Đặt mua xe này")
        self.btn_buy.setObjectName("btn_buy")
        self.btn_buy.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_buy.setEnabled(row.get("trang_thai") == "Còn hàng")
        self.btn_buy.clicked.connect(self._dat_mua)
        btn_lv.addWidget(btn_close)
        btn_lv.addWidget(self.btn_buy, 1)
        lv.addWidget(btn_w)

    def _load_img(self):
        img_path = self.row.get("anh_url", "") or ""
        if img_path and os.path.exists(img_path):
            pix = QPixmap(img_path).scaled(
                560, 240,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation)
            self.img_lbl.setPixmap(pix)
            self.img_lbl.setStyleSheet("background:#f3f4f6;")
        else:
            self.img_lbl.setText(
                f"🚗\n{self.row['hang_xe']} {self.row['dong_xe']}\n(Chưa có ảnh)")
            self.img_lbl.setStyleSheet(
                "background:qlineargradient(x1:0,y1:0,x2:1,y2:1,"
                "stop:0 #dbeafe,stop:1 #e0f2fe);"
                "color:#2563eb; font-size:18px; font-weight:700;")

    def _change_img(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Chọn ảnh xe", "",
            "Images (*.png *.jpg *.jpeg *.webp *.bmp)")
        if not path:
            return
        conn = get_conn()
        conn.execute("UPDATE xe SET anh_url=? WHERE id=?", (path, self.row["id"]))
        conn.commit()
        conn.close()
        self.row["anh_url"] = path
        self._load_img()
        QMessageBox.information(self, "OK", "✅ Đã cập nhật ảnh xe!")

    def _dat_mua(self):
        from views.don_hang_view import DonHangDialog
        dlg = DonHangDialog(self)
        for i in range(dlg.f_xe.count()):
            if dlg.f_xe.itemData(i) == self.row["id"]:
                dlg.f_xe.setCurrentIndex(i)
                break
        if dlg.exec():
            self.reject()