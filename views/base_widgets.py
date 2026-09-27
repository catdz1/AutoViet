"""
views/base_widgets.py
Các class widget nền dùng chung cho nhiều màn hình (View/Dialog) trong toàn bộ app:
- BaseDialog: khung dialog chuẩn (tiêu đề + form + nút Lưu/Huỷ)
- BaseView: khung view chuẩn (toolbar + bảng dữ liệu + tìm kiếm)

Được tách ra từ views/other_views.py (bản trước gộp chung base + 4 màn hình
Khách hàng/Nhân viên/Đơn hàng/Dịch vụ trong 1 file 2300+ dòng, rất khó bảo trì).
"""
import os                  # ← THÊM DÒNG NÀY
import pandas as pd
import calendar, random
from datetime import datetime, date
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QDialog, QFormLayout, QComboBox,
    QMessageBox, QHeaderView, QLabel, QDoubleSpinBox, QTextEdit,
    QFrame, QApplication, QTabWidget, QScrollArea, QGridLayout, QInputDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QPixmap   # ← thêm QPixmap vào đây luôn
from database import get_conn


class BaseDialog(QDialog):
    def __init__(self, parent=None, title="", width=500):
        super().__init__(parent)
        self.setWindowTitle(title); self.setMinimumWidth(width)
        self.setStyleSheet("""
            QDialog{background:#f0f4f8;color:#00274c;}
            QLabel{color:#1e40af;font-size:13px;font-weight:600;background:transparent;letter-spacing:0.3px;}
            QLineEdit,QTextEdit,QDoubleSpinBox,QComboBox{
                background:#ffffff;color:#00274c;border:0.5px solid #dbeafe;
                border-radius:8px;padding:8px 12px;font-size:13px;}
            QLineEdit:focus,QTextEdit:focus,QDoubleSpinBox:focus,QComboBox:focus{border-color:#2563eb;}
            QComboBox QAbstractItemView{background:#ffffff;color:#00274c;
                border:0.5px solid #dbeafe;selection-background-color:#eff6ff;}
            QPushButton{background:#ffffff;color:#00274c;border:0.5px solid #dbeafe;
                border-radius:8px;padding:8px 18px;font-size:13px;}
            QPushButton:hover{background:#eff6ff;color:#1e40af;}
            QPushButton#btn_save{background:#2563eb;color:white;border:none;font-weight:700;min-width:100px;}
            QPushButton#btn_save:hover{background:#1d4ed8;}
            QPushButton#btn_pdf{background:#eff6ff;color:#1e40af;border:0.5px solid #bfdbfe;font-weight:600;}
            QPushButton#btn_pdf:hover{background:#2563eb;color:white;}
            QTabWidget::pane{border:0.5px solid #dbeafe;border-radius:8px;}
            QTabBar::tab{padding:6px 16px;font-size:12px;font-weight:600;
                color:#64748b;background:#f8fafc;border:none;
                border-bottom:2px solid transparent;}
            QTabBar::tab:selected{color:#2563eb;border-bottom:2px solid #2563eb;}
        """)
        self._main_lv = QVBoxLayout(self)
        self._main_lv.setContentsMargins(24,20,24,20); self._main_lv.setSpacing(14)

        # Giới hạn chiều cao dialog theo màn hình thực tế — tránh tràn màn hình laptop nhỏ
        screen = QApplication.primaryScreen().availableGeometry()
        self.setMaximumHeight(int(screen.height() * 0.92))

    def _add_title(self, text):
        lbl = QLabel(text);
        lbl.setStyleSheet("font-size:15px;font-weight:700;color:#00274c;background:transparent;padding-bottom:4px;")
        sep = QFrame();
        sep.setFrameShape(QFrame.Shape.HLine);
        sep.setStyleSheet("background:#dbeafe;max-height:1px;")
        self._main_lv.addWidget(lbl); self._main_lv.addWidget(sep)

    def _add_form(self):
        form=QFormLayout(); form.setSpacing(10); form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        # Bọc form trong vùng cuộn — nếu form quá dài, người dùng cuộn được thay vì bị tràn/mất nút
        form_wrap = QWidget()
        form_wrap.setLayout(form)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea{background:transparent;border:none;}")
        scroll.setWidget(form_wrap)
        self._main_lv.addWidget(scroll, 1)
        return form

    def _add_buttons(self, save_text="💾  Lưu"):
        sep=QFrame(); sep.setFrameShape(QFrame.Shape.HLine); sep.setStyleSheet("background:#dbeafe;max-height:1px;")
        self._main_lv.addWidget(sep)
        bh=QHBoxLayout(); bh.addStretch()
        bc=QPushButton("  Huỷ bỏ"); bc.clicked.connect(self.reject)
        bs=QPushButton(save_text); bs.setObjectName("btn_save"); bs.clicked.connect(self._save); bs.setDefault(True)
        bh.addWidget(bc); bh.addWidget(bs); self._main_lv.addLayout(bh)

    def _f_line(self,ph=""): w=QLineEdit(); w.setPlaceholderText(ph); return w
    def _f_combo(self,items): w=QComboBox(); w.addItems(items); return w
    def _f_spin(self,max_v=1e11,step=1e6,suffix=" ₫"):
        w=QDoubleSpinBox(); w.setRange(0,max_v); w.setSingleStep(step); w.setDecimals(0); w.setSuffix(suffix); return w
    def _save(self): pass


class BaseView(QWidget):
    COLS=[]
    def __init__(self,page_name,current_user=None):
        super().__init__(); self.setObjectName(page_name)
        self.current_user=current_user or {"role":"nhanvien","id":None}
        self._sel_id=None; self._rows=[]
        self._build_base(); self._build_toolbar(); self._load()

    def _build_base(self):
        self._root=QVBoxLayout(self); self._root.setContentsMargins(0,0,0,0); self._root.setSpacing(0)
        self._tb=QWidget(); self._tb.setObjectName("toolbar_widget")
        self._tbh=QHBoxLayout(self._tb); self._tbh.setContentsMargins(12,8,12,8); self._tbh.setSpacing(6)
        self._root.addWidget(self._tb)
        self.tbl = QTableWidget(0, len(self.COLS))
        self.tbl.setHorizontalHeaderLabels([c[0] for c in self.COLS])
        self.tbl.setAlternatingRowColors(True)
        self.tbl.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tbl.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl.setShowGrid(False);
        self.tbl.verticalHeader().setVisible(False)
        h = self.tbl.horizontalHeader()
        # ✅ Căn chỉnh tự động fit nội dung
        for i, (_, __, stretch) in enumerate(self.COLS):
            if stretch:
                h.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
            else:
                h.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        self.tbl.setStyleSheet("""
            QTableWidget{background:#ffffff;alternate-background-color:#f8fafc;
                gridline-color:#f1f5f9;border:none;font-size:13px;}
            QTableWidget::item{padding:8px 12px;color:#1e293b;border-bottom:1px solid #f1f5f9;}
            QTableWidget::item:selected{background:#eff6ff;color:#2563eb;}
            QHeaderView::section{background:#f8fafc;color:#2563eb;
                font-size:12px;font-weight:800;letter-spacing:1px;
                padding:12px;border:none;border-bottom:2px solid #2563eb;}
        """)
        self._root.addWidget(self.tbl)
        self.tbl.selectionModel().selectionChanged.connect(self._on_sel)

    def _btn(self,txt,obj=None,slot=None):
        b=QPushButton(txt)
        if obj: b.setObjectName(obj)
        if slot: b.clicked.connect(slot)
        b.setCursor(Qt.CursorShape.PointingHandCursor); self._tbh.addWidget(b); return b

    def _search_box(self,ph="🔍 Tìm kiếm..."):
        self._tbh.addStretch()
        self.search=QLineEdit(); self.search.setObjectName("search_box"); self.search.setPlaceholderText(ph)
        self.search.textChanged.connect(lambda t: self._load(t.strip()))
        self._tbh.addWidget(self.search)

    def _build_toolbar(self): pass
    def _load(self,q=""): pass

    def _render(self):
        self.tbl.setRowCount(0)
        for row in self._rows:
            r = self.tbl.rowCount();
            self.tbl.insertRow(r);
            self.tbl.setRowHeight(r, 50)
            for c, (_, key, __) in enumerate(self.COLS):
                val = str(row.get(key, "") or "")
                item = QTableWidgetItem(val);
                item.setData(Qt.ItemDataRole.UserRole, row.get("id"))
                item.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
                if c == 0:
                    item.setForeground(QColor("#2563eb"))
                    item.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
                else:
                    item.setForeground(QColor("#334155"))
                    item.setFont(QFont("Segoe UI", 12))
                self.tbl.setItem(r, c, item)

    def _on_sel(self):
        r=self.tbl.currentRow()
        if 0<=r<len(self._rows): self._sel_id=self._rows[r]["id"]

    def refresh(self):
        q=getattr(self,"search",None); self._load(q.text().strip() if q else "")

    def _check_sel(self,action="thao tác"):
        if not self._sel_id:
            QMessageBox.warning(self,"Chưa chọn",f"Vui lòng chọn dòng cần {action}!"); return False
        return True

    def _get_row(self,table,id_val):
        conn=get_conn(); row=conn.execute(f"SELECT * FROM {table} WHERE id=?",(id_val,)).fetchone()
        conn.close(); return dict(row) if row else None
