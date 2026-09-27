"""
views/xe_view.py — Danh sách xe cải tiến
+ Filter theo hãng xe (button tabs)
+ Sắp xếp theo hãng
+ Chi tiết xe bên phải đẹp hơn
THAY THẾ views/xe_view.py cũ
"""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QLineEdit, QScrollArea, QDialog, QFormLayout, QComboBox,
    QDoubleSpinBox, QTextEdit, QMessageBox, QFileDialog,
    QGridLayout, QApplication, QSplitter, QSizePolicy
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor, QFont, QPixmap
from database import get_conn


STYLE = """
QWidget { font-family: 'Segoe UI', Arial; }
/* ComboBox lọc hãng xe */
QComboBox#brand_combo {
    background: #0F1F35;
    color: #e2e8f0;
    border: 1px solid #2c1f6e;
    border-radius: 8px;
    padding: 6px 12px;
    font-size: 12px;
    font-weight: 600;
    min-width: 180px;
    max-width: 220px;
}
QComboBox#brand_combo::drop-down {
    width: 20px;
    border: none;
    background: transparent;
}
QComboBox#brand_combo::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #a78bfa;
}
QComboBox#brand_combo:hover { border-color: #a78bfa; }
QComboBox#brand_combo::drop-down { border: none; }
QComboBox QAbstractItemView {
    background: #0F1F35;
    color: #e2e8f0;
    selection-background-color: #2c1f6e;
    border: 1px solid #2c1f6e;
}
/* Toolbar */
QWidget#toolbar_widget {
    background: #0F1F35:
    border-bottom: 1px solid #3d2d8a;
}

/* Hãng xe tabs */
QWidget#brand_bar {
    background: #0F1F35;
    border-bottom: 1px solid #1a3050;
    padding: 6px 14px;
}
QPushButton#brand_btn {
    background: #ffffff;
    color: #64748b;
    border: 1px solid #e2e8f0;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    padding: 6px 16px;
    min-width: 70px;
}
QPushButton#brand_btn:hover {
    background: #f1f5ff;
    color: #4338ca;
    border-color: #a5b4fc;
}
QPushButton#brand_btn_active {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #6d28d9, stop:1 #7c3aed);
    color: white;
    border: none;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
    padding: 6px 16px;
    min-width: 70px;
}

/* Buttons */
QPushButton#btn_add {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #6d28d9, stop:1 #7c3aed);
    color: white; border: none; border-radius: 9px;
    font-size: 13px; font-weight: 700; padding: 9px 18px;
}
QPushButton#btn_add:hover { background: #7c3aed; }
QPushButton#btn_ai {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #0e7490, stop:1 #0891b2);
    color: white; border: none; border-radius: 9px;
    font-size: 13px; font-weight: 700; padding: 9px 18px;
}
QPushButton#btn_ai:hover { background: #0891b2; }
QPushButton#btn_del {
    background: #450a0a; color: #fca5a5;
    border: 1px solid #7f1d1d; border-radius: 8px;
    font-size: 12px; padding: 8px 14px;
}
QPushButton#btn_del:hover { background: #7f1d1d; }
QPushButton#btn_print {
    background: #1e2236; color: #9ca3af;
    border: 1px solid #2c3050; border-radius: 8px;
    font-size: 12px; padding: 8px 14px;
}
QPushButton#btn_excel {
    background: #14532d; color: #86efac;
    border: 1px solid #166534; border-radius: 8px;
    font-size: 12px; padding: 8px 14px;
}

/* Search */
QLineEdit#search_box {
    background: #1e2236; color: #e2e8f0;
    border: 1px solid #2c3050; border-radius: 9px;
    padding: 8px 16px; font-size: 13px; min-width: 240px;
}
QLineEdit#search_box:focus { border-color: #7c3aed; }

/* Table — ĐỔI NỀN TRẮNG */
QTableWidget {
    background: #ffffff;
    alternate-background-color: #f8faff;
    gridline-color: #e9edf5;
    border: none;
    selection-background-color: #ede9fe;
}
QTableWidget::item { padding: 8px 12px; color: #1e293b; font-size: 13px; font-weight: 500; }
QTableWidget::item:selected { color: #6d28d9; background: #ede9fe; }
QHeaderView::section {
    background: #f1f3f7; color: #1e293b;
    font-size: 13px; font-weight: 800;
    letter-spacing: 1px; padding: 10px 12px;
    border: none; border-bottom: 1px solid #e2e8f0;
    text-transform: uppercase;
}

/* Detail panel — ĐỔI NỀN TRẮNG */
QWidget#detail_panel {
    background: #ffffff;
    border-left: 1px solid #e2e8f0;
}
QLabel#detail_title {
    font-size: 16px; font-weight: 800;
    color: #1e293b; background: transparent;
}
QLabel#detail_price {
    font-size: 22px; font-weight: 800;
    color: #059669; background: transparent;
}
QLabel#detail_key {
    font-size: 10px; font-weight: 700;
    color: #94a3b8; background: transparent;
    text-transform: uppercase; letter-spacing: 1px;
}
QLabel#detail_val {
    font-size: 13px; color: #334155;
    background: transparent; font-weight: 500;
}

/* Sort buttons — ĐỔI NỀN TRẮNG */
QPushButton#sort_btn {
    background: #ffffff; color: #64748b;
    border: 1px solid #e2e8f0; border-radius: 6px;
    font-size: 11px; padding: 4px 10px;
}
QPushButton#sort_btn:hover { background: #f1f5ff; color: #4338ca; }
QPushButton#sort_btn_active {
    background: #ede9fe; color: #6d28d9;
    border: 1px solid #a78bfa; border-radius: 6px;
    font-size: 11px; padding: 4px 10px; font-weight: 700;
}
"""

BRAND_ICONS = {
    "Toyota": "🚙", "Honda": "🚗", "Ford": "🚕",
    "Kia": "🚐", "Mazda": "🏎️", "Hyundai": "🚌",
    "Mitsubishi": "🚓", "Suzuki": "🛻", "Mercedes": "💎",
    "BMW": "⭐", "Audi": "🔷",
}


class XeView(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("page_xe")
        self.setStyleSheet(STYLE)
        self._rows = []
        self._sel_id = None
        self._cur_brand = "Tất cả"
        self._sort_col = "hang_xe"
        self._sort_asc = True
        self._brand_btns = {}
        self._build()
        self._load()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Toolbar ──────────────────────────────────────────────────────
        tb = QWidget(); tb.setObjectName("toolbar_widget")
        tbh = QHBoxLayout(tb)
        tbh.setContentsMargins(14, 9, 14, 9); tbh.setSpacing(6)

        btn_add = QPushButton("➕  Thêm xe");
        btn_add.setObjectName("btn_add")
        btn_ai = QPushButton("🤖  AI nhận diện xe");
        btn_ai.setObjectName("btn_ai")
        btn_ai.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_edit = QPushButton("✏  Sửa");
        btn_edit.setObjectName("btn_edit")
        btn_del = QPushButton("🗑  Xoá");
        btn_del.setObjectName("btn_del")
        btn_in = QPushButton("🖨  In PDF");
        btn_in.setObjectName("btn_print")
        btn_xl = QPushButton("📊 Excel");
        btn_xl.setObjectName("btn_excel")

        for b in [btn_add,btn_edit,btn_del,btn_in,btn_xl]:
            b.setCursor(Qt.CursorShape.PointingHandCursor)

        self.search = QLineEdit(); self.search.setObjectName("search_box")
        self.search.setPlaceholderText("🔍  Tìm xe theo tên, mã, màu sắc...")
        self.search.textChanged.connect(lambda t: self._load(t.strip()))

        tbh.addWidget(btn_add);
        tbh.addWidget(btn_ai);
        tbh.addWidget(btn_edit)
        tbh.addWidget(btn_del);
        tbh.addWidget(btn_in)
        tbh.addWidget(btn_xl);
        tbh.addStretch()
        tbh.addWidget(self.search)
        root.addWidget(tb)

        # ── Brand filter bar ─────────────────────────────────────────────
        self.brand_w = QWidget()
        self.brand_w.setObjectName("brand_bar")
        self.brand_h = QHBoxLayout(self.brand_w)
        self.brand_h.setContentsMargins(14, 6, 14, 6)
        self.brand_h.setSpacing(6)
        lbl = QLabel("🏷️  Lọc theo hãng:")
        lbl.setStyleSheet("color:#a78bfa;font-size:12px;font-weight:600;background:transparent;")
        self.brand_combo = QComboBox()
        self.brand_combo.setObjectName("brand_combo")
        self.brand_combo.setFixedWidth(220)
        self.brand_combo.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.brand_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.brand_combo.currentTextChanged.connect(self._on_brand_combo)
        self.brand_h.addWidget(lbl)
        self.brand_h.addWidget(self.brand_combo)
        self.brand_h.addStretch()
        root.addWidget(self.brand_w)

        # ── Main: Table + Detail panel ───────────────────────────────────
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet("QSplitter::handle{background:#e2e8f0;width:1px;}")

        # Table
        table_w = QWidget()
        table_lv = QVBoxLayout(table_w)
        table_lv.setContentsMargins(0,0,0,0); table_lv.setSpacing(0)

        # Sort bar — NỀN TRẮNG
        sort_w = QWidget()
        sort_w.setStyleSheet("background:#f5f7fa;border-bottom:1px solid #e2e8f0;padding:4px 14px;")
        sort_h = QHBoxLayout(sort_w); sort_h.setContentsMargins(0,4,0,4); sort_h.setSpacing(6)
        sort_lbl = QLabel("Sắp xếp theo:")
        sort_lbl.setStyleSheet("color:#94a3b8;font-size:11px;background:transparent;")
        sort_h.addWidget(sort_lbl)

        self._sort_btns = {}
        for key, label in [("hang_xe","Hãng xe"),("gia_ban","Giá bán"),
                            ("nam_sx","Năm SX"),("trang_thai","Trạng thái")]:
            b = QPushButton(label); b.setObjectName("sort_btn")
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.clicked.connect(lambda _,k=key: self._sort_by(k))
            sort_h.addWidget(b); self._sort_btns[key] = b
        sort_h.addStretch()
        # Stat labels
        self.lbl_total = QLabel()
        self.lbl_total.setStyleSheet("color:#94a3b8;font-size:11px;background:transparent;")
        sort_h.addWidget(self.lbl_total)
        table_lv.addWidget(sort_w)

        cols = ["MÃ XE","TÊN XE","NĂM","GIÁ BÁN","MÀU SẮC","TRẠNG THÁI"]
        self.tbl = QTableWidget(0, len(cols))
        self.tbl.setHorizontalHeaderLabels(cols)
        self.tbl.setAlternatingRowColors(True)
        self.tbl.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tbl.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl.setShowGrid(True)
        self.tbl.verticalHeader().setVisible(False)
        h = self.tbl.horizontalHeader()
        h.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tbl.selectionModel().selectionChanged.connect(self._on_sel)
        self.tbl.doubleClicked.connect(self._edit)
        table_lv.addWidget(self.tbl)
        splitter.addWidget(table_w)

        # Detail panel
        self.detail_w = QWidget(); self.detail_w.setObjectName("detail_panel")
        self.detail_w.setFixedWidth(280)
        self._build_detail_panel()
        splitter.addWidget(self.detail_w)
        splitter.setSizes([900, 280])
        root.addWidget(splitter, 1)

        # Connect buttons
        btn_add.clicked.connect(self._add)
        btn_ai.clicked.connect(self._add_ai)
        btn_edit.clicked.connect(self._edit)
        btn_del.clicked.connect(self._delete)
        btn_in.clicked.connect(self._print_pdf)
        btn_xl.clicked.connect(self._export)

        # Init sort button
        self._sort_btns["hang_xe"].setObjectName("sort_btn_active")

    def _build_detail_panel(self):
        outer_lv = QVBoxLayout(self.detail_w)
        outer_lv.setContentsMargins(0, 0, 0, 0)
        outer_lv.setSpacing(0)

        # Bọc toàn bộ nội dung chi tiết trong vùng cuộn — nếu thông tin xe
        # (đặc biệt phần "Mô tả") quá dài thì cuộn chuột lên/xuống để xem hết,
        # không bị tràn/che mất phần dưới panel.
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea{background:#ffffff;border:none;}")
        scroll.verticalScrollBar().setSingleStep(14)

        content = QWidget()
        content.setStyleSheet("background:#ffffff;")
        lv = QVBoxLayout(content)
        lv.setContentsMargins(14, 8, 14, 14); lv.setSpacing(8)

        self.detail_img = QLabel()
        self.detail_img.setFixedSize(252, 160)
        self.detail_img.setScaledContents(False)
        self.detail_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.detail_img.setStyleSheet(
            "background:#f8faff;border-radius:10px;color:#94a3b8;"
            "font-size:13px;border:1px solid #e2e8f0;")
        self.detail_img.setText("🚗\nChọn xe để xem chi tiết")
        lv.addWidget(self.detail_img)

        sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background:#e2e8f0;max-height:1px;")
        lv.addWidget(sep)

        self.detail_name = QLabel("—"); self.detail_name.setObjectName("detail_title")
        self.detail_name.setWordWrap(True)
        self.detail_price = QLabel("—"); self.detail_price.setObjectName("detail_price")
        lv.addWidget(self.detail_name); lv.addWidget(self.detail_price)

        sep2 = QFrame(); sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet("background:#e2e8f0;max-height:1px;")
        lv.addWidget(sep2)

        self.detail_fields = {}
        fields = ["Mã xe","Năm SX","Màu sắc","Số khung","Số máy",
                  "Tình trạng","Trạng thái","Giá nhập","Mô tả"]
        for f in fields:
            lk = QLabel(f.upper())
            lk.setObjectName("detail_key")
            lv2 = QLabel("—"); lv2.setObjectName("detail_val")
            lv2.setWordWrap(True)
            lv.addWidget(lk); lv.addWidget(lv2)
            self.detail_fields[f] = lv2

        lv.addStretch()
        scroll.setWidget(content)
        outer_lv.addWidget(scroll)

    def _update_brand_bar(self):
        conn = get_conn()
        brands = [r[0] for r in conn.execute(
            "SELECT DISTINCT hang_xe FROM xe ORDER BY hang_xe").fetchall()]
        counts = {r[0]: r[1] for r in conn.execute(
            "SELECT hang_xe,COUNT(*) FROM xe GROUP BY hang_xe").fetchall()}
        total = conn.execute("SELECT COUNT(*) FROM xe").fetchone()[0]
        conn.close()

        self.brand_combo.blockSignals(True)
        self.brand_combo.clear()
        self.brand_combo.addItem(f"🚗 Tất cả ({total})")
        for brand in brands:
            icon = BRAND_ICONS.get(brand, "🚗")
            self.brand_combo.addItem(f"{icon} {brand} ({counts.get(brand, 0)})")
        for i in range(self.brand_combo.count()):
            if self._cur_brand in self.brand_combo.itemText(i):
                self.brand_combo.setCurrentIndex(i)
                break
        self.brand_combo.blockSignals(False)
        self.brand_h.addStretch()

    def _filter_brand(self, brand):
        self._cur_brand = brand
        for key, btn in self._brand_btns.items():
            btn.setObjectName("brand_btn_active" if key==brand else "brand_btn")
            btn.setStyleSheet("")
        self._load(self.search.text().strip())

    def _on_brand_combo(self, text):
        if "Tất cả" in text:
            self._cur_brand = "Tất cả"
        else:
            self._cur_brand = text.split("(")[0].strip()
            for icon in BRAND_ICONS.values():
                self._cur_brand = self._cur_brand.replace(icon, "").strip()
        self._load(self.search.text().strip())

    def _sort_by(self, col):
        if self._sort_col == col:
            self._sort_asc = not self._sort_asc
        else:
            self._sort_col = col; self._sort_asc = True
        for key, btn in self._sort_btns.items():
            btn.setObjectName("sort_btn_active" if key==col else "sort_btn")
            btn.setStyleSheet("")
        self._load(self.search.text().strip())

    def _load(self, q=""):
        conn = get_conn()
        sql = "SELECT * FROM xe"
        p = []
        conds = []
        if self._cur_brand != "Tất cả":
            conds.append("hang_xe=?"); p.append(self._cur_brand)
        if q:
            conds.append("(hang_xe LIKE ? OR dong_xe LIKE ? OR ma_xe LIKE ? OR mau_sac LIKE ?)")
            p += [f"%{q}%"]*4
        if conds: sql += " WHERE " + " AND ".join(conds)

        sort_map = {"hang_xe":"hang_xe,dong_xe","gia_ban":"gia_ban",
                    "nam_sx":"nam_sx DESC","trang_thai":"trang_thai"}
        sql += f" ORDER BY {sort_map.get(self._sort_col,'hang_xe')}"
        if self._sort_col in ["hang_xe","gia_ban"] and not self._sort_asc:
            sql = sql.replace("ORDER BY","ORDER BY") + " DESC" if "DESC" not in sql else sql

        self._rows = [dict(r) for r in conn.execute(sql, p).fetchall()]
        conn.close()

        self._update_brand_bar()
        self._render()

    def _render(self):
        STATUS_COL = {
            "Còn hàng":"#059669","Đặt cọc":"#d97706",
            "Đã bán":"#dc2626","Bảo dưỡng":"#7c3aed"
        }
        STATUS_BG = {
            "Còn hàng":"rgba(5,150,105,.10)","Đặt cọc":"rgba(217,119,6,.10)",
            "Đã bán":"rgba(220,38,38,.10)","Bảo dưỡng":"rgba(124,58,237,.10)"
        }

        self.tbl.setRowCount(0)
        for row in self._rows:
            r = self.tbl.rowCount(); self.tbl.insertRow(r)
            self.tbl.setRowHeight(r, 52)

            vals = [
                row.get("ma_xe",""),
                f"{row['hang_xe']}  {row['dong_xe']}",
                str(row.get("nam_sx","")),
                f"{row['gia_ban']/1e9:.2f} tỷ",
                row.get("mau_sac","") or "—",
                row.get("trang_thai",""),
            ]
            for c, val in enumerate(vals):
                item = QTableWidgetItem(val)
                item.setData(Qt.ItemDataRole.UserRole, row.get("id"))
                if c == 0:
                    item.setForeground(QColor("#2563eb"))
                    item.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
                elif c == 1:
                    item.setForeground(QColor("#1e293b"))
                    item.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
                elif c == 3:
                    item.setForeground(QColor("#16a34a"))
                    item.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
                elif c == 5:
                    tt = val
                    item.setForeground(QColor(STATUS_COL.get(tt,"#64748b")))
                    item.setFont(QFont("Segoe UI",13,QFont.Weight.Bold))
                    item.setBackground(QColor(STATUS_BG.get(tt,"transparent")))
                self.tbl.setItem(r, c, item)
                if c == 2:
                    item.setForeground(QColor("#475569"))
                    item.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
                elif c == 4:
                    item.setForeground(QColor("#334155"))
                    item.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))

        con = sum(1 for r in self._rows if r["trang_thai"]=="Còn hàng")
        ban = sum(1 for r in self._rows if r["trang_thai"]=="Đã bán")
        self.lbl_total.setText(
            f"Hiển thị: {len(self._rows)} xe  |  Còn hàng: {con}  |  Đã bán: {ban}")

    def _on_sel(self):
        r = self.tbl.currentRow()
        if 0 <= r < len(self._rows):
            row = self._rows[r]
            self._sel_id = row["id"]
            self._show_detail(row)

    def _show_detail(self, row):
        img_path = row.get("anh_url","") or ""
        if img_path and os.path.exists(img_path):
            pix = QPixmap(img_path.replace("/","\\")).scaled(
                self.detail_img.width(), self.detail_img.height(), Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation)
            self.detail_img.setPixmap(pix)
        else:
            icon = BRAND_ICONS.get(row.get("hang_xe",""),"🚗")
            self.detail_img.setText(f"{icon}\n{row['hang_xe']}\n(Chưa có ảnh)")
            self.detail_img.setPixmap(QPixmap())

        self.detail_name.setText(f"{row['hang_xe']} {row['dong_xe']}")
        self.detail_price.setText(f"{row['gia_ban']/1e9:.3f} tỷ ₫")

        STATUS_COL={"Còn hàng":"#059669","Đặt cọc":"#d97706",
                    "Đã bán":"#dc2626","Bảo dưỡng":"#7c3aed"}
        vals = {
            "Mã xe":      row.get("ma_xe",""),
            "Năm SX":     str(row.get("nam_sx","")),
            "Màu sắc":    row.get("mau_sac","") or "—",
            "Số khung":   row.get("so_khung","") or "—",
            "Số máy":     row.get("so_may","") or "—",
            "Tình trạng": row.get("tinh_trang","") or "—",
            "Trạng thái": row.get("trang_thai",""),
            "Giá nhập":   f"{int(row.get('gia_nhap',0) or 0):,} ₫",
            "Mô tả":      row.get("mo_ta","") or "—",
        }
        for key, val in vals.items():
            lbl = self.detail_fields.get(key)
            if lbl:
                lbl.setText(val)
                if key == "Trạng thái":
                    lbl.setStyleSheet(
                        f"font-size:13px;font-weight:700;background:transparent;"
                        f"color:{STATUS_COL.get(val,'#64748b')};")

        # Ép vẽ lại toàn bộ panel — tránh hiện tượng ảnh/chữ cũ còn sót lại (ghosting) khi đổi xe
        self.detail_img.repaint()
        self.detail_name.repaint()
        self.detail_price.repaint()
        self.detail_w.repaint()

    def _change_img(self):
        if not self._sel_id: return
        path, _ = QFileDialog.getOpenFileName(
            self, "Chọn ảnh xe", "",
            "Images (*.png *.jpg *.jpeg *.webp *.bmp)")
        if not path: return
        conn = get_conn()
        conn.execute("UPDATE xe SET anh_url=? WHERE id=?", (path, self._sel_id))
        conn.commit(); conn.close()
        self._load(self.search.text())
        QMessageBox.information(self,"✅ OK","Đã cập nhật ảnh xe!")

    def _add(self):
        if XeDialog(self).exec(): self._load(self.search.text())

    def _add_ai(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Chọn ảnh xe", "", "Images (*.png *.jpg *.jpeg *.webp)")
        if not path: return
        if XeDialogAI(self, path).exec(): self._load(self.search.text())

    def _edit(self):
        if not self._sel_id:
            QMessageBox.warning(self, "", "Chọn xe cần sửa!")
            return
        row = next((r for r in self._rows if r["id"] == self._sel_id), None)
        if row and XeDialog(self, row).exec(): self._load(self.search.text())

    def _delete(self):
        if not self._sel_id:
            QMessageBox.warning(self, "", "Chọn xe cần xoá!")
            return
        conn = get_conn()
        if conn.execute("SELECT COUNT(*) FROM don_hang WHERE xe_id=?", (self._sel_id,)).fetchone()[0]:
            conn.close()
            QMessageBox.critical(self, "", "Xe đã có đơn hàng, không thể xoá!")
            return
        conn.close()
        if QMessageBox.question(self, "Xác nhận", "Xoá xe này?",
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                                ) == QMessageBox.StandardButton.Yes:
            conn = get_conn()
            conn.execute("DELETE FROM xe WHERE id=?", (self._sel_id,))
            conn.commit(); conn.close(); self._sel_id = None
            self.detail_img.setText("🚗\nChọn xe để xem chi tiết")
            
            self._load(self.search.text())

    def _print_pdf(self):
        if not self._sel_id:
            QMessageBox.warning(self, "", "Chọn xe cần in!")
            return
        row = next((r for r in self._rows if r["id"] == self._sel_id), None)
        if not row: return
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib import colors
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import cm
            import os

            fname = f"xe_{row['ma_xe']}.pdf"
            doc = SimpleDocTemplate(fname, pagesize=A4,
                                    topMargin=2*cm, bottomMargin=2*cm,
                                    leftMargin=2*cm, rightMargin=2*cm)
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle('title', fontSize=16, fontName='Helvetica-Bold',
                                         alignment=1, spaceAfter=20)
            story = []
            story.append(Paragraph("THONG TIN XE", title_style))
            story.append(Spacer(1, 0.3*cm))

            anh_url = row.get("anh_url","") or ""
            if anh_url: anh_url = anh_url.replace("/","\\")
            if anh_url and os.path.exists(anh_url):
                try:
                    img = Image(anh_url)
                    max_w, max_h = 12*cm, 7*cm
                    ratio = min(max_w/img.imageWidth, max_h/img.imageHeight)
                    img.drawWidth = img.imageWidth * ratio
                    img.drawHeight = img.imageHeight * ratio
                    img.hAlign = 'CENTER'
                    story.append(img)
                    story.append(Spacer(1, 0.4*cm))
                except Exception: pass

            data = [
                ["Ma xe", row.get("ma_xe","")],
                ["Hang xe", row.get("hang_xe","")],
                ["Dong xe", row.get("dong_xe","")],
                ["Nam san xuat", str(row.get("nam_sx",""))],
                ["Mau sac", row.get("mau_sac","") or "—"],
                ["Gia ban", f"{int(row.get('gia_ban',0) or 0):,} VND"],
                ["Gia nhap", f"{int(row.get('gia_nhap',0) or 0):,} VND"],
                ["So khung", row.get("so_khung","") or "—"],
                ["So may", row.get("so_may","") or "—"],
                ["Tinh trang", row.get("tinh_trang","") or "—"],
                ["Trang thai", row.get("trang_thai","")],
                ["Mo ta", row.get("mo_ta","") or "—"],
            ]
            tbl = Table(data, colWidths=[5*cm, 12*cm])
            tbl.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#0f1f35')),
                ('TEXTCOLOR', (0,0), (0,-1), colors.white),
                ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 11),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('PADDING', (0,0), (-1,-1), 8),
                ('ROWBACKGROUNDS', (1,0), (1,-1),
                 [colors.HexColor('#f8fafc'), colors.white]),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
            ]))
            story.append(tbl)
            doc.build(story)
            QMessageBox.information(self, "✅ In PDF", f"Da xuat: {fname}")
            os.startfile(fname)
        except Exception as e:
            QMessageBox.critical(self, "Loi", str(e))

    # ══════════════════════════════════════════════════════════
    # HÀM XUẤT EXCEL ĐẸP — THAY THẾ HÀM CŨ
    # ══════════════════════════════════════════════════════════
    def _export(self):
        import openpyxl
        from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
        from openpyxl.utils import get_column_letter
        from datetime import datetime

        # ── Lấy dữ liệu ──────────────────────────────────────
        conn = get_conn()
        rows = conn.execute("""
            SELECT ma_xe, hang_xe, dong_xe, nam_sx, mau_sac,
                   tinh_trang, gia_nhap, gia_ban, trang_thai
            FROM xe ORDER BY hang_xe, dong_xe
        """).fetchall()
        stats = conn.execute("""
            SELECT
                COUNT(*) as tong,
                SUM(CASE WHEN trang_thai='Còn hàng' THEN 1 ELSE 0 END),
                SUM(CASE WHEN trang_thai='Đã bán'   THEN 1 ELSE 0 END),
                SUM(CASE WHEN trang_thai='Đặt cọc'  THEN 1 ELSE 0 END),
                SUM(gia_ban),
                SUM(CASE WHEN trang_thai='Đã bán' THEN gia_ban ELSE 0 END)
            FROM xe
        """).fetchone()
        by_brand = conn.execute("""
            SELECT hang_xe, COUNT(*) as so_xe,
                   SUM(CASE WHEN trang_thai='Còn hàng' THEN 1 ELSE 0 END),
                   SUM(CASE WHEN trang_thai='Đã bán'   THEN 1 ELSE 0 END),
                   SUM(gia_ban)
            FROM xe GROUP BY hang_xe ORDER BY so_xe DESC
        """).fetchall()
        conn.close()

        # ── Hộp thoại chọn nơi lưu ───────────────────────────
        fname, _ = QFileDialog.getSaveFileName(
            self, "Lưu file Excel",
            f"BaoCao_Xe_{datetime.now().strftime('%d%m%Y_%H%M')}.xlsx",
            "Excel Files (*.xlsx)"
        )
        if not fname:
            return

        # ── Helpers ───────────────────────────────────────────
        def fill(c):
            return PatternFill("solid", fgColor=c)
        def fnt(bold=False, color="000000", size=11):
            return Font(bold=bold, color=color, size=size, name="Segoe UI")
        def aln(h="left", v="center", wrap=False):
            return Alignment(horizontal=h, vertical=v, wrap_text=wrap)
        def bdr(c="CBD5E1"):
            s = Side(style="thin", color=c)
            return Border(left=s, right=s, top=s, bottom=s)

        wb = openpyxl.Workbook()

        # ════════════════════════════════════════════════════
        # SHEET 1: DANH SÁCH XE
        # ════════════════════════════════════════════════════
        ws = wb.active
        ws.title = "Danh sách xe"

        # Dòng 1 — Tiêu đề
        ws.merge_cells("A1:I1")
        c = ws["A1"]
        c.value = "DANH SÁCH XE  —  HỆ THỐNG AUTOVIET"
        c.font = Font(bold=True, color="FFFFFF", size=16, name="Segoe UI")
        c.fill = fill("6D28D9")
        c.alignment = aln("center")
        ws.row_dimensions[1].height = 42

        # Dòng 2 — Thông tin xuất
        ws.merge_cells("A2:E2")
        ws["A2"].value = f"Ngày xuất: {datetime.now().strftime('%d/%m/%Y  %H:%M')}"
        ws["A2"].font = fnt(color="64748B", size=10)
        ws["A2"].fill = fill("F1F5F9")
        ws["A2"].alignment = aln("left")

        ws.merge_cells("F2:I2")
        ws["F2"].value = (
            f"Tổng: {stats[0]} xe    |    "
            f"Còn hàng: {stats[1]}    |    "
            f"Đã bán: {stats[2]}    |    "
            f"Đặt cọc: {stats[3]}"
        )
        ws["F2"].font = fnt(bold=True, color="1E293B", size=10)
        ws["F2"].fill = fill("F1F5F9")
        ws["F2"].alignment = aln("right")
        ws.row_dimensions[2].height = 22

        # Dòng 3 — Header cột
        cols_cfg = [
            ("STT",           "A",  5),
            ("MÃ XE",         "B",  11),
            ("HÃNG XE",       "C",  15),
            ("DÒNG XE",       "D",  24),
            ("NĂM SX",        "E",   9),
            ("MÀU SẮC",       "F",  15),
            ("TÌNH TRẠNG",    "G",  14),
            ("GIÁ BÁN (VNĐ)", "H",  22),
            ("TRẠNG THÁI",    "I",  15),
        ]
        for label, col, width in cols_cfg:
            c = ws[f"{col}3"]
            c.value = label
            c.font = Font(bold=True, color="FFFFFF", size=11, name="Segoe UI")
            c.fill = fill("0F1F35")
            c.alignment = aln("center")
            c.border = bdr("1E40AF")
            ws.column_dimensions[col].width = width
        ws.row_dimensions[3].height = 32

        # Màu trạng thái
        ST_CFG = {
            "Còn hàng":  ("D1FAE5", "065F46", "✅ Còn hàng"),
            "Đã bán":    ("FEE2E2", "991B1B", "🔴 Đã bán"),
            "Đặt cọc":   ("FEF3C7", "92400E", "🟡 Đặt cọc"),
            "Bảo dưỡng": ("EDE9FE", "5B21B6", "🔧 Bảo dưỡng"),
        }

        for i, row in enumerate(rows, 1):
            r = i + 3
            bg = "F8FAFF" if i % 2 == 1 else "FFFFFF"
            ws.row_dimensions[r].height = 21
            ma, hang, dong, nam, mau, tinh, g_nhap, g_ban, tt = row
            tt = tt or "Còn hàng"
            st_bg, st_fg, st_lbl = ST_CFG.get(tt, ("F1F5F9", "374151", tt))

            data_cells = [
                (1, i,                 "94A3B8", False, "center"),
                (2, ma or "",          "2563EB", True,  "center"),
                (3, hang or "",        "1E293B", True,  "left"),
                (4, dong or "",        "334155", False, "left"),
                (5, nam or "",         "475569", False, "center"),
                (6, mau or "—",        "334155", False, "center"),
                (7, tinh or "—",       "334155", False, "center"),
                (8, int(g_ban or 0),   "059669", True,  "right"),
                (9, st_lbl,            st_fg,    True,  "center"),
            ]
            for col_idx, val, color, bold, align_h in data_cells:
                c = ws.cell(r, col_idx, val)
                c.font = fnt(bold=bold, color=color)
                c.fill = fill(st_bg if col_idx == 9 else bg)
                c.alignment = aln(align_h)
                c.border = bdr()
                if col_idx == 8:
                    c.number_format = '#,##0 "₫"'

        # Dòng tổng
        last = len(rows) + 4
        ws.row_dimensions[last].height = 28
        ws.merge_cells(f"A{last}:G{last}")
        c = ws[f"A{last}"]
        c.value = f"TỔNG CỘNG  ({len(rows)} xe)"
        c.font = Font(bold=True, color="FFFFFF", size=12, name="Segoe UI")
        c.fill = fill("0F1F35"); c.alignment = aln("center"); c.border = bdr("0F1F35")

        c = ws[f"H{last}"]
        c.value = sum(int(r[7] or 0) for r in rows)
        c.font = Font(bold=True, color="FBBF24", size=13, name="Segoe UI")
        c.fill = fill("0F1F35"); c.number_format = '#,##0 "₫"'
        c.alignment = aln("right"); c.border = bdr("0F1F35")

        c = ws[f"I{last}"]
        c.value = f"DT bán: {int(stats[5] or 0):,} ₫"
        c.font = Font(bold=True, color="4ADE80", size=10, name="Segoe UI")
        c.fill = fill("0F1F35"); c.alignment = aln("center"); c.border = bdr("0F1F35")

        ws.freeze_panes = "A4"
        ws.auto_filter.ref = f"A3:I{last - 1}"

        # ════════════════════════════════════════════════════
        # SHEET 2: THỐNG KÊ
        # ════════════════════════════════════════════════════
        ws2 = wb.create_sheet("Thống kê")

        ws2.merge_cells("A1:D1")
        ws2["A1"].value = "THỐNG KÊ KHO XE — AUTOVIET"
        ws2["A1"].font = Font(bold=True, color="FFFFFF", size=14, name="Segoe UI")
        ws2["A1"].fill = fill("6D28D9")
        ws2["A1"].alignment = aln("center")
        ws2.row_dimensions[1].height = 36

        for j, h in enumerate(["CHỈ SỐ", "GIÁ TRỊ"], 1):
            c = ws2.cell(2, j, h)
            c.font = fnt(bold=True, color="FFFFFF", size=11)
            c.fill = fill("0F1F35"); c.alignment = aln("center"); c.border = bdr()
        ws2.column_dimensions["A"].width = 30
        ws2.column_dimensions["B"].width = 26

        kpi = [
            ("Tổng số xe trong kho",      stats[0], "1E293B"),
            ("Xe còn hàng",               stats[1], "059669"),
            ("Xe đã bán",                 stats[2], "DC2626"),
            ("Xe đặt cọc",                stats[3], "D97706"),
            ("Tổng giá trị kho (VNĐ)",    int(stats[4] or 0), "2563EB"),
            ("Doanh thu đã bán (VNĐ)",    int(stats[5] or 0), "7C3AED"),
        ]
        for i, (lbl_txt, val, color) in enumerate(kpi, 3):
            bg3 = "F8FAFF" if i % 2 == 1 else "FFFFFF"
            c = ws2.cell(i, 1, lbl_txt)
            c.font = fnt(bold=True, color="1E293B")
            c.fill = fill(bg3); c.border = bdr(); c.alignment = aln("left")

            c = ws2.cell(i, 2, val)
            c.font = fnt(bold=True, color=color, size=12)
            c.fill = fill(bg3); c.border = bdr(); c.alignment = aln("right")
            if isinstance(val, int) and val > 9999:
                c.number_format = '#,##0 "₫"'
            ws2.row_dimensions[i].height = 26

        # Thống kê theo hãng
        sr = len(kpi) + 4
        ws2.merge_cells(f"A{sr}:E{sr}")
        c = ws2[f"A{sr}"]
        c.value = "THỐNG KÊ THEO HÃNG XE"
        c.font = Font(bold=True, color="FFFFFF", size=12, name="Segoe UI")
        c.fill = fill("1E40AF"); c.alignment = aln("center")
        ws2.row_dimensions[sr].height = 28

        b_headers = ["HÃNG XE", "TỔNG XE", "CÒN HÀNG", "ĐÃ BÁN", "TỔNG GIÁ TRỊ"]
        for j, h in enumerate(b_headers, 1):
            c = ws2.cell(sr+1, j, h)
            c.font = fnt(bold=True, color="FFFFFF", size=10)
            c.fill = fill("0F1F35"); c.alignment = aln("center"); c.border = bdr()
            ws2.column_dimensions[get_column_letter(j)].width = 17
        ws2.column_dimensions["E"].width = 26

        for i, (hang, so_xe, con_hang, da_ban, tong_gia) in enumerate(by_brand):
            r2 = sr + 2 + i
            bg4 = "F0F4FF" if i % 2 == 0 else "FFFFFF"
            for j, (val, color, bold, align_h) in enumerate([
                (hang,           "1E293B", True,  "left"),
                (so_xe,          "334155", False, "center"),
                (con_hang or 0,  "059669", True,  "center"),
                (da_ban or 0,    "DC2626", True,  "center"),
                (int(tong_gia or 0), "059669", True, "right"),
            ], 1):
                c = ws2.cell(r2, j, val)
                c.font = fnt(bold=bold, color=color)
                c.fill = fill(bg4); c.border = bdr(); c.alignment = aln(align_h)
                if j == 5: c.number_format = '#,##0 "₫"'
            ws2.row_dimensions[r2].height = 22

        # ── Lưu ──────────────────────────────────────────────
        try:
            wb.save(fname)
            import os
            QMessageBox.information(
                self, "✅ Xuất Excel thành công!",
                f"Đã lưu tại:\n{fname}\n\n"
                f"• Sheet 1 — Danh sách: {len(rows)} xe\n"
                f"• Sheet 2 — Thống kê tổng hợp & theo hãng"
            )
            os.startfile(fname)
        except PermissionError:
            QMessageBox.critical(self, "❌ Lỗi",
                "Không thể lưu!\nVui lòng đóng file Excel đang mở rồi thử lại.")
        except Exception as e:
            QMessageBox.critical(self, "❌ Lỗi", str(e))

    def refresh(self): self._load(self.search.text())


class XeDialog(QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.data = data
        self.setWindowTitle("Thêm xe mới" if not data else f"Sửa — {data.get('hang_xe','')} {data.get('dong_xe','')}")
        self.setMinimumWidth(520)
        self.setStyleSheet("""
            QDialog{background:#1a1d28;}
            QLabel{color:#64748b;font-size:11px;font-weight:700;background:transparent;letter-spacing:.8px;}
            QLineEdit,QDoubleSpinBox,QComboBox,QTextEdit{
                background:#13151c;color:#e2e8f0;border:1px solid #2c3050;
                border-radius:8px;padding:8px 12px;font-size:13px;}
            QLineEdit:focus,QDoubleSpinBox:focus,QComboBox:focus{border-color:#7c3aed;}
            QPushButton#save{background:#6d28d9;color:white;border:none;border-radius:9px;
                font-size:14px;font-weight:700;padding:11px 24px;}
            QPushButton#save:hover{background:#7c3aed;}
            QPushButton#cancel{background:#1e2236;color:#9ca3af;border:1px solid #2c3050;
                border-radius:9px;font-size:13px;padding:10px 20px;}
        """)
        self._build()

    def _build(self):
        from PyQt6.QtWidgets import QScrollArea, QApplication
        outer = QVBoxLayout(self); outer.setContentsMargins(24,20,24,20); outer.setSpacing(14)
        title = QLabel("🚗  THÔNG TIN XE" if not self.data else "✏️  SỬA THÔNG TIN XE")
        title.setStyleSheet("font-size:15px;font-weight:700;color:#e2e8f0;background:transparent;")
        sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background:#252840;max-height:1px;")
        outer.addWidget(title); outer.addWidget(sep)

        form = QFormLayout(); form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        def lbl(t):
            l = QLabel(t)
            l.setStyleSheet("color:#4a5568;font-size:11px;font-weight:700;background:transparent;letter-spacing:.8px;")
            return l

        self.f_ma    = QLineEdit(); self.f_ma.setPlaceholderText("VD: XE012")
        self.f_hang  = QLineEdit(); self.f_hang.setPlaceholderText("VD: Toyota, Honda, Ford, Kia...")
        self.f_dong  = QLineEdit(); self.f_dong.setPlaceholderText("VD: Camry 2.5Q")
        self.f_nam   = QLineEdit(); self.f_nam.setPlaceholderText("VD: 2024")
        self.f_mau   = QLineEdit(); self.f_mau.setPlaceholderText("VD: Trắng Ngọc Trai")
        self.f_gian  = QDoubleSpinBox(); self.f_gian.setRange(0,10e9); self.f_gian.setSingleStep(50e6); self.f_gian.setDecimals(0); self.f_gian.setSuffix(" ₫")
        self.f_gban  = QDoubleSpinBox(); self.f_gban.setRange(0,10e9); self.f_gban.setSingleStep(50e6); self.f_gban.setDecimals(0); self.f_gban.setSuffix(" ₫")
        self.f_skhung= QLineEdit(); self.f_skhung.setPlaceholderText("Số khung VIN")
        self.f_smay  = QLineEdit(); self.f_smay.setPlaceholderText("Số máy")
        self.f_ttinh = QComboBox(); self.f_ttinh.addItems(["Mới","Đã qua sử dụng"])
        self.f_tt    = QComboBox(); self.f_tt.addItems(["Còn hàng","Đặt cọc","Đã bán","Bảo dưỡng"])
        self.f_mota  = QTextEdit(); self.f_mota.setMaximumHeight(70); self.f_mota.setPlaceholderText("Mô tả thêm...")

        for l,w in [("MÃ XE *",self.f_ma),("HÃNG XE *",self.f_hang),
                    ("DÒNG XE *",self.f_dong),("NĂM SX *",self.f_nam),
                    ("MÀU SẮC",self.f_mau),("GIÁ NHẬP",self.f_gian),
                    ("GIÁ BÁN *",self.f_gban),("SỐ KHUNG",self.f_skhung),
                    ("SỐ MÁY",self.f_smay),("TÌNH TRẠNG",self.f_ttinh),
                    ("TRẠNG THÁI",self.f_tt),("MÔ TẢ",self.f_mota)]:
            form.addRow(lbl(l), w)

        # Bọc form trong vùng cuộn để không bị tràn màn hình laptop nhỏ
        form_wrap = QWidget()
        form_wrap.setStyleSheet("background:#1a1d28;")
        form_wrap.setLayout(form)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea{background:#1a1d28;border:none;}")
        scroll.setWidget(form_wrap)
        scroll.viewport().setStyleSheet("background:#1a1d28;")
        outer.addWidget(scroll, 1)

        bh = QHBoxLayout(); bh.addStretch()
        bc = QPushButton("Huỷ bỏ"); bc.setObjectName("cancel"); bc.clicked.connect(self.reject)
        bs = QPushButton("💾  Lưu xe"); bs.setObjectName("save")
        bs.clicked.connect(self._save); bs.setDefault(True)
        bh.addWidget(bc); bh.addWidget(bs); outer.addLayout(bh)

        if self.data: self._fill()

        # Giới hạn kích thước dialog theo màn hình thực tế (luôn thấy được nút Lưu/Huỷ)
        screen = QApplication.primaryScreen().availableGeometry()
        self.resize(560, min(700, int(screen.height()*0.85)))
        self.setMaximumHeight(int(screen.height()*0.92))

    def _fill(self):
        d = self.data
        self.f_ma.setText(d.get("ma_xe","")); self.f_ma.setReadOnly(True)
        self.f_ma.setStyleSheet("color:#6b7280;background:#13151c;")
        self.f_hang.setText(d.get("hang_xe",""))
        self.f_dong.setText(d.get("dong_xe",""))
        self.f_nam.setText(str(d.get("nam_sx","")))
        self.f_mau.setText(d.get("mau_sac","") or "")
        self.f_gian.setValue(float(d.get("gia_nhap",0) or 0))
        self.f_gban.setValue(float(d.get("gia_ban",0) or 0))
        self.f_skhung.setText(d.get("so_khung","") or "")
        self.f_smay.setText(d.get("so_may","") or "")
        idx2 = self.f_ttinh.findText(d.get("tinh_trang","Mới"))
        if idx2>=0: self.f_ttinh.setCurrentIndex(idx2)
        idx3 = self.f_tt.findText(d.get("trang_thai","Còn hàng"))
        if idx3>=0: self.f_tt.setCurrentIndex(idx3)
        self.f_mota.setPlainText(d.get("mo_ta","") or "")

    def _save(self):
        ma   = self.f_ma.text().strip()
        hang = self.f_hang.text().strip()
        dong = self.f_dong.text().strip()
        nam  = self.f_nam.text().strip()
        if not all([ma, hang, dong, nam]):
            QMessageBox.warning(self,"","Điền đủ Mã xe, Hãng, Dòng xe, Năm!"); return
        conn = get_conn()
        try:
            vals = (hang, dong, int(nam), self.f_mau.text(),
                    self.f_gian.value(), self.f_gban.value(),
                    self.f_skhung.text() or None, self.f_smay.text() or None,
                    self.f_ttinh.currentText(), self.f_tt.currentText(),
                    self.f_mota.toPlainText())
            if self.data:
                conn.execute("""UPDATE xe SET hang_xe=?,dong_xe=?,nam_sx=?,mau_sac=?,
                    gia_nhap=?,gia_ban=?,so_khung=?,so_may=?,tinh_trang=?,
                    trang_thai=?,mo_ta=? WHERE id=?""", vals+(self.data["id"],))
            else:
                conn.execute("""INSERT INTO xe(ma_xe,hang_xe,dong_xe,nam_sx,mau_sac,
                    gia_nhap,gia_ban,so_khung,so_may,tinh_trang,trang_thai,mo_ta)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""", (ma,)+vals)
            conn.commit()
            QMessageBox.information(self,"✅ OK","Lưu xe thành công!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self,"Lỗi",
                "Mã xe đã tồn tại!" if "UNIQUE" in str(e) else str(e))
        finally: conn.close()


class XeDialogAI(QDialog):
    def __init__(self, parent=None, image_path=None):
        super().__init__(parent)
        self.image_path = image_path
        self.setWindowTitle("🤖 Thêm xe bằng AI")
        self.setMinimumWidth(560)
        self.setStyleSheet("""
            QDialog{background:#1a1d28;}
            QLabel{color:#64748b;font-size:11px;font-weight:700;background:transparent;letter-spacing:.8px;}
            QLineEdit,QDoubleSpinBox,QComboBox,QTextEdit{
                background:#13151c;color:#e2e8f0;border:1px solid #2c3050;
                border-radius:8px;padding:8px 12px;font-size:13px;}
            QLineEdit:focus,QDoubleSpinBox:focus,QComboBox:focus{border-color:#7c3aed;}
            QPushButton#save{background:#6d28d9;color:white;border:none;border-radius:9px;
                font-size:14px;font-weight:700;padding:11px 24px;}
            QPushButton#save:hover{background:#7c3aed;}
            QPushButton#cancel{background:#1e2236;color:#9ca3af;border:1px solid #2c3050;
                border-radius:9px;font-size:13px;padding:10px 20px;}
            QPushButton#btn_reanalyze{background:#0e7490;color:white;border:none;border-radius:8px;
                font-size:12px;font-weight:600;padding:8px 16px;}
        """)
        self._build()
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(300, self._analyze)

    def _build(self):
        from PyQt6.QtWidgets import QScrollArea, QApplication
        outer = QVBoxLayout(self); outer.setContentsMargins(24,20,24,20); outer.setSpacing(14)
        title = QLabel("🤖  NHẬN DIỆN XE BẰNG AI")
        title.setStyleSheet("font-size:15px;font-weight:700;color:#e2e8f0;background:transparent;")
        sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background:#252840;max-height:1px;")
        outer.addWidget(title); outer.addWidget(sep)

        img_row = QHBoxLayout()
        self.img_lbl = QLabel(); self.img_lbl.setFixedSize(160,110)
        self.img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.img_lbl.setStyleSheet("border:1px solid #2c3050;border-radius:8px;background:#13151c;")
        px = QPixmap(self.image_path)
        if not px.isNull():
            self.img_lbl.setPixmap(px.scaled(160,110,Qt.AspectRatioMode.KeepAspectRatio,
                                              Qt.TransformationMode.SmoothTransformation))
        self.status_lbl = QLabel("🔍 Đang phân tích ảnh bằng AI...")
        self.status_lbl.setStyleSheet("color:#a78bfa;font-size:13px;font-weight:600;background:transparent;")
        self.status_lbl.setWordWrap(True)
        btn_re = QPushButton("🔄 Phân tích lại"); btn_re.setObjectName("btn_reanalyze")
        btn_re.clicked.connect(self._analyze)
        vbox = QVBoxLayout(); vbox.addWidget(self.status_lbl); vbox.addWidget(btn_re); vbox.addStretch()
        img_row.addWidget(self.img_lbl); img_row.addSpacing(12); img_row.addLayout(vbox,1)
        outer.addLayout(img_row)

        sep2 = QFrame(); sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet("background:#252840;max-height:1px;")
        outer.addWidget(sep2)

        def lbl(t):
            l = QLabel(t)
            l.setStyleSheet("color:#4a5568;font-size:11px;font-weight:700;background:transparent;letter-spacing:.8px;")
            return l

        form = QFormLayout(); form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.f_ma    = QLineEdit(); self.f_ma.setPlaceholderText("VD: XE012")
        self.f_hang  = QLineEdit(); self.f_hang.setPlaceholderText("VD: Toyota")
        self.f_dong  = QLineEdit(); self.f_dong.setPlaceholderText("VD: Camry 2.5Q")
        self.f_nam   = QLineEdit(); self.f_nam.setPlaceholderText("VD: 2024")
        self.f_mau   = QLineEdit(); self.f_mau.setPlaceholderText("VD: Trắng Ngọc Trai")
        self.f_gian  = QDoubleSpinBox(); self.f_gian.setRange(0,10e9); self.f_gian.setSingleStep(50e6); self.f_gian.setDecimals(0); self.f_gian.setSuffix(" ₫")
        self.f_gban  = QDoubleSpinBox(); self.f_gban.setRange(0,10e9); self.f_gban.setSingleStep(50e6); self.f_gban.setDecimals(0); self.f_gban.setSuffix(" ₫")
        self.f_skhung= QLineEdit(); self.f_skhung.setPlaceholderText("Số khung VIN")
        self.f_smay  = QLineEdit(); self.f_smay.setPlaceholderText("Số máy")
        self.f_ttinh = QComboBox(); self.f_ttinh.addItems(["Mới","Đã qua sử dụng"])
        self.f_tt    = QComboBox(); self.f_tt.addItems(["Còn hàng","Đặt cọc","Đã bán","Bảo dưỡng"])
        self.f_mota  = QTextEdit(); self.f_mota.setMaximumHeight(70); self.f_mota.setPlaceholderText("Mô tả thêm...")

        for l,w in [("MÃ XE *",self.f_ma),("HÃNG XE *",self.f_hang),
                    ("DÒNG XE *",self.f_dong),("NĂM SX *",self.f_nam),
                    ("MÀU SẮC",self.f_mau),("GIÁ NHẬP",self.f_gian),
                    ("GIÁ BÁN *",self.f_gban),("SỐ KHUNG",self.f_skhung),
                    ("SỐ MÁY",self.f_smay),("TÌNH TRẠNG",self.f_ttinh),
                    ("TRẠNG THÁI",self.f_tt),("MÔ TẢ",self.f_mota)]:
            form.addRow(lbl(l), w)

        # Bọc form trong vùng cuộn để không bị tràn màn hình laptop nhỏ
        form_wrap = QWidget()
        form_wrap.setStyleSheet("background:#1a1d28;")
        form_wrap.setLayout(form)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea{background:#1a1d28;border:none;}")
        scroll.setWidget(form_wrap)
        scroll.viewport().setStyleSheet("background:#1a1d28;")
        outer.addWidget(scroll, 1)

        bh = QHBoxLayout(); bh.addStretch()
        bc = QPushButton("Huỷ bỏ"); bc.setObjectName("cancel"); bc.clicked.connect(self.reject)
        bs = QPushButton("💾  Lưu xe"); bs.setObjectName("save"); bs.clicked.connect(self._save)
        bh.addWidget(bc); bh.addWidget(bs); outer.addLayout(bh)

        # Giới hạn kích thước dialog theo màn hình thực tế (luôn thấy được nút Lưu/Huỷ)
        screen = QApplication.primaryScreen().availableGeometry()
        self.resize(600, min(750, int(screen.height()*0.88)))
        self.setMaximumHeight(int(screen.height()*0.92))

    def _analyze(self):
        import base64, json, urllib.request, threading
        self.status_lbl.setText("🔍 Đang phân tích ảnh bằng AI...")
        self.status_lbl.setStyleSheet("color:#a78bfa;font-size:13px;font-weight:600;background:transparent;")

        def run():
            try:
                with open(self.image_path, "rb") as f:
                    img_b64 = base64.b64encode(f.read()).decode()
                ext = self.image_path.lower().split(".")[-1]
                mime = {"jpg":"image/jpeg","jpeg":"image/jpeg",
                        "png":"image/png","webp":"image/webp"}.get(ext,"image/jpeg")
                api_key = "ViiLvjUT7Qnub1ySiDy6pW0tPmCFBHzJ4Rf8aOX9"
                prompt = """Phân tích ảnh xe này và trả về JSON (không có markdown, chỉ JSON thuần):
{
  "hang_xe": "tên hãng xe",
  "dong_xe": "dòng xe và phiên bản",
  "nam_sx": "năm sản xuất ước tính",
  "mau_sac": "màu sắc xe",
  "gia_ban": giá bán tại Việt Nam hiện tại tính bằng đồng (số nguyên),
  "gia_nhap": giá nhập ước tính tính bằng đồng (số nguyên),
  "tinh_trang": "Mới hoặc Đã qua sử dụng",
  "mo_ta": "mô tả ngắn về xe bằng tiếng Việt"
}"""
                body = json.dumps({
                    "model": "command-a-vision-07-2025",
                    "messages": [{"role":"user","content":[
                        {"type":"text","text":prompt},
                        {"type":"image_url","image_url":{"url":f"data:{mime};base64,{img_b64}"}}
                    ]}]
                }).encode()
                req = urllib.request.Request(
                    "https://api.cohere.com/v2/chat", data=body,
                    headers={"Content-Type":"application/json",
                             "Authorization":f"Bearer {api_key}","Accept":"application/json"})
                with urllib.request.urlopen(req, timeout=60) as resp:
                    result = json.loads(resp.read())
                    text = result["message"]["content"][0]["text"].strip()
                    if "```" in text:
                        text = text.split("```")[1].replace("json","").strip()
                    data = json.loads(text)
                    self._fill_form(data)
            except urllib.error.HTTPError as e:
                # Đọc nội dung lỗi CHI TIẾT từ Cohere (thay vì chỉ hiện "HTTP Error 422")
                try:
                    err_body = e.read().decode("utf-8", errors="ignore")
                except Exception:
                    err_body = "(không đọc được nội dung lỗi)"
                print(f"[AI nhận diện xe] HTTP {e.code} - Chi tiết lỗi từ Cohere:\n{err_body}")
                self.status_lbl.setText(f"❌ Lỗi HTTP {e.code}: {err_body[:150]}")
                self.status_lbl.setStyleSheet("color:#f87171;font-size:12px;background:transparent;")
            except Exception as e:
                self.status_lbl.setText(f"❌ Lỗi: {str(e)[:80]}")
                self.status_lbl.setStyleSheet("color:#f87171;font-size:12px;background:transparent;")

        threading.Thread(target=run, daemon=True).start()

    def _fill_form(self, data):
        self._ai_data = data
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(0, self._apply_form)

    @staticmethod
    def _parse_so(val):
        if val is None:
         return 0.0
        if isinstance(val, (int, float)):
         return float(val)
        s = str(val).lower().replace(",", "")
        m = re.search(r"[\d]+(\.\d+)?", s)
        if not m:
         return 0.0
        num = float(m.group(0))
        if "tỷ" in s or "ty" in s:
         num *= 1_000_000_000
        elif "triệu" in s or "trieu" in s:
         num *= 1_000_000
        elif "nghìn" in s or "ngàn" in s or "nghin" in s or "ngan" in s:
         num *= 1_000
        return num

    def _apply_form(self):
        data = getattr(self, "_ai_data", {})
        conn = get_conn()
        rows = conn.execute("SELECT ma_xe FROM xe ORDER BY ma_xe").fetchall()
        conn.close()
        nums = []
        for r in rows:
            try: nums.append(int(r[0].replace("XE","")))
            except Exception: pass
        next_num = max(nums)+1 if nums else 1
        self.f_ma.setText(f"XE{next_num:03d}")
        self.f_hang.setText(data.get("hang_xe",""))
        self.f_dong.setText(data.get("dong_xe",""))
        self.f_nam.setText(str(data.get("nam_sx","")))
        self.f_mau.setText(data.get("mau_sac",""))
        self.f_gian.setValue(self._parse_so(data.get("gia_nhap",0)))
        self.f_gban.setValue(self._parse_so(data.get("gia_ban",0)))
        self.f_mota.setPlainText(data.get("mo_ta",""))
        try:
            nam = int(data.get("nam_sx",0))
            tinh_trang = "Mới" if nam >= 2020 else "Đã qua sử dụng"
        except Exception:
            tinh_trang = data.get("tinh_trang","Mới")
        idx = self.f_ttinh.findText(tinh_trang)
        if idx >= 0: self.f_ttinh.setCurrentIndex(idx)
        self.status_lbl.setText("✅ AI đã nhận diện xong! Kiểm tra và chỉnh sửa nếu cần.")
        self.status_lbl.setStyleSheet("color:#4ade80;font-size:12px;font-weight:600;background:transparent;")
        try:
            gia = float(data.get("gia_ban",0) or 0)
            nam = int(data.get("nam_sx",0) or 0)
            self._ai_noi_bat = 1 if gia >= 3_000_000_000 else 0
            self._ai_giam_gia = 10 if nam < 2020 else 0
        except Exception:
            self._ai_noi_bat = 0; self._ai_giam_gia = 0

    def _save(self):
        ma = self.f_ma.text().strip(); hang = self.f_hang.text().strip()
        dong = self.f_dong.text().strip(); nam = self.f_nam.text().strip()
        if not all([ma, hang, dong, nam]):
            QMessageBox.warning(self,"","Vui lòng điền đầy đủ các trường bắt buộc (*)!"); return
        conn = get_conn()
        try:
            if conn.execute("SELECT id FROM xe WHERE ma_xe=?",(ma,)).fetchone():
                QMessageBox.warning(self,"","Mã xe đã tồn tại!"); return
            conn.execute("""INSERT INTO xe(ma_xe,hang_xe,dong_xe,nam_sx,mau_sac,gia_nhap,gia_ban,
                                           so_khung,so_may,tinh_trang,trang_thai,mo_ta)
                            VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
                         (ma,hang,dong,nam,self.f_mau.text(),int(self.f_gian.value()),
                          int(self.f_gban.value()),self.f_skhung.text() or None,
                          self.f_smay.text() or None,self.f_ttinh.currentText(),
                          self.f_tt.currentText(),self.f_mota.toPlainText()))
            xe_id = conn.execute("SELECT id FROM xe WHERE ma_xe=?",(ma,)).fetchone()
            if xe_id:
                conn.execute("UPDATE xe SET noi_bat=?,giam_gia=?,ngay_nhap=date('now') WHERE id=?",
                             (getattr(self,'_ai_noi_bat',0),getattr(self,'_ai_giam_gia',0),xe_id[0]))
                conn.execute("UPDATE xe SET anh_url=? WHERE id=?", (self.image_path, xe_id[0]))
            conn.commit()
            QMessageBox.information(self,"✅ OK","Lưu xe thành công!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self,"Lỗi",str(e))
        finally: conn.close()