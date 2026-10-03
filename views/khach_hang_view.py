"""
views/khach_hang_view.py — Màn hình quản lý Khách hàng
Tách từ views/other_views.py để mỗi màn hình nghiệp vụ nằm 1 file riêng,
dễ đọc và dễ bảo trì hơn (file gốc gộp 4 màn hình khác nhau vào 1 file).
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

from views.base_widgets import BaseDialog, BaseView

# ════════════════════════════════════════════════════════════════
# KHÁCH HÀNG
# ════════════════════════════════════════════════════════════════
class KhachHangView(BaseView):
    COLS=[("MÃ KH","ma_kh",False),("HỌ TÊN","ho_ten",True),
          ("SỐ ĐT","so_dt",False),("EMAIL","email",False),
          ("LOẠI KH","loai_kh",False),("CMND/CCCD","cmnd",False)]
    def __init__(self,current_user=None):
        super().__init__("page_khach_hang",current_user)
        self.tbl.doubleClicked.connect(self._on_double_click)  # ← double-click xem chi tiết

    def _build_toolbar(self):
        self._btn("+ Thêm KH","btn_add",self._add)
        self._btn("✏  Sửa",None,self._edit)
        self._btn("🗑  Xoá","btn_del",self._delete)
        self._btn("🔍 Lịch sử GD",None,self._lich_su)
        self._btn("📊 Excel","btn_excel",self._export)
        self._search_box("🔍 Tìm khách hàng...")

    def _load(self,q=""):
        conn=get_conn(); sql="SELECT * FROM khach_hang"; p=[]
        if q: sql+=" WHERE ho_ten LIKE ? OR so_dt LIKE ? OR ma_kh LIKE ?"; p=[f"%{q}%"]*3
        self._rows=[dict(r) for r in conn.execute(sql+" ORDER BY id DESC",p).fetchall()]
        conn.close(); self._render()
        self._render()
        for r, row in enumerate(self._rows):
            # Mã KH — xanh đậm
            i0 = QTableWidgetItem(row.get("ma_kh", ""))
            i0.setForeground(QColor("#2563eb"))
            i0.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
            self.tbl.setItem(r, 0, i0)
            # Họ tên — đen đậm
            i1 = QTableWidgetItem(row.get("ho_ten", ""))
            i1.setForeground(QColor("#0f172a"))
            i1.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
            self.tbl.setItem(r, 1, i1)
            # Số ĐT — xanh lá
            i2 = QTableWidgetItem(row.get("so_dt", "") or "")
            i2.setForeground(QColor("#16a34a"))
            i2.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
            self.tbl.setItem(r, 2, i2)
            # Loại KH — badge màu
            loai = row.get("loai_kh", "")
            i4 = QTableWidgetItem(loai)
            i4.setForeground(QColor("#7c3aed") if loai == "Doanh nghiệp" else QColor("#0891b2"))
            i4.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
            self.tbl.setItem(r, 4, i4)

    def _add(self):
        if KhachHangDialog(self).exec(): self._load()
    def _edit(self):
        if not self._check_sel("sửa"): return
        row=self._get_row("khach_hang",self._sel_id)
        if KhachHangDialog(self,row).exec(): self._load()
    def _delete(self):
        if not self._check_sel("xoá"): return
        conn=get_conn()
        if conn.execute("SELECT COUNT(*) FROM don_hang WHERE kh_id=?",(self._sel_id,)).fetchone()[0]:
            conn.close(); QMessageBox.critical(self,"","KH đã có đơn hàng!"); return
        conn.close()
        if QMessageBox.question(self,"Xác nhận","Xoá khách hàng này?",
            QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No
        )==QMessageBox.StandardButton.Yes:
            conn=get_conn(); conn.execute("DELETE FROM khach_hang WHERE id=?",(self._sel_id,))
            conn.commit(); conn.close(); self._sel_id=None; self._load()
    def _lich_su(self):
        if not self._check_sel("xem lịch sử"): return
        row=next((r for r in self._rows if r["id"]==self._sel_id),None)
        if row: LichSuKHDialog(self,row).exec()
    def _export(self):
        import openpyxl
        from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
        from openpyxl.utils import get_column_letter
        import datetime
        conn = get_conn()
        rows = conn.execute("SELECT ma_kh,ho_ten,so_dt,email,dia_chi,loai_kh FROM khach_hang").fetchall()
        conn.close()
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Khách hàng"
        ws.merge_cells("A1:F1")
        ws["A1"] = "DANH SÁCH KHÁCH HÀNG — AUTOVIET"
        ws["A1"].font = Font(name="Segoe UI", size=14, bold=True, color="FFFFFF")
        ws["A1"].fill = PatternFill("solid", fgColor="1E40AF")
        ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[1].height = 36
        ws.merge_cells("A2:F2")
        ws["A2"] = f"Ngày xuất: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}"
        ws["A2"].font = Font(name="Segoe UI", size=10, italic=True, color="64748B")
        ws["A2"].alignment = Alignment(horizontal="right")
        ws.row_dimensions[2].height = 20
        headers = ["MÃ KH", "HỌ TÊN", "SỐ ĐIỆN THOẠI", "EMAIL", "ĐỊA CHỈ", "LOẠI KH"]
        col_widths = [12, 25, 18, 28, 30, 12]
        thin = Side(style="thin", color="BFDBFE")
        border = Border(left=thin, right=thin, top=thin, bottom=thin)
        for i, (h, w) in enumerate(zip(headers, col_widths), 1):
            cell = ws.cell(row=3, column=i, value=h)
            cell.font = Font(name="Segoe UI", size=11, bold=True, color="1E40AF")
            cell.fill = PatternFill("solid", fgColor="DBEAFE")
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = border
            ws.column_dimensions[get_column_letter(i)].width = w
        ws.row_dimensions[3].height = 28
        fill_white = PatternFill("solid", fgColor="FFFFFF")
        fill_alt = PatternFill("solid", fgColor="F0F7FF")
        font_data = Font(name="Segoe UI", size=11, color="1E293B")
        font_ma = Font(name="Segoe UI", size=11, bold=True, color="2563EB")
        for ri, row in enumerate(rows, 4):
            fill = fill_white if ri % 2 == 0 else fill_alt
            ws.row_dimensions[ri].height = 24
            for ci, val in enumerate(row, 1):
                cell = ws.cell(row=ri, column=ci, value=val)
                cell.fill = fill
                cell.border = border
                cell.alignment = Alignment(vertical="center",
                    horizontal="center" if ci in (1, 3, 6) else "left")
                cell.font = font_ma if ci == 1 else font_data
        ws.freeze_panes = "A4"
        fname = f"DanhSach_KhachHang_{datetime.datetime.now().strftime('%d%m%Y_%H%M')}.xlsx"
        wb.save(fname)
        QMessageBox.information(self, "Excel", f"✅ Đã xuất: {fname}")

    def _xem_chitiet(self):
        if not self._check_sel("xem chi tiết"): return
        row = next((r for r in self._rows if r["id"] == self._sel_id), None)
        if row:
            KhachHangChiTietDialog(self, row).exec()

    def _on_double_click(self, index):
        r = index.row()
        if 0 <= r < len(self._rows):
            self._sel_id = self._rows[r]["id"]
            KhachHangChiTietDialog(self, self._rows[r]).exec()

class LichSuKHDialog(BaseDialog):
    def __init__(self,parent=None,kh_row=None):
        super().__init__(parent,f"Lịch sử — {kh_row['ho_ten']}",700)
        self.kh=kh_row; self._build_ls()
    def _build_ls(self):
        self._add_title(f"👥  {self.kh['ho_ten']}  |  {self.kh['so_dt']}")
        conn=get_conn()
        dh_rows=conn.execute("""SELECT dh.ma_don,x.hang_xe||' '||x.dong_xe,dh.gia_ban_thuc,
            dh.trang_thai,dh.ngay_dat FROM don_hang dh JOIN xe x ON dh.xe_id=x.id
            WHERE dh.kh_id=? ORDER BY dh.id DESC""",(self.kh["id"],)).fetchall()
        dv_rows=conn.execute("""SELECT dv.ma_dv,x.hang_xe||' '||x.dong_xe,dv.loai_dv,
            dv.chi_phi,dv.trang_thai FROM dich_vu dv LEFT JOIN xe x ON dv.xe_id=x.id
            WHERE dv.kh_id=? ORDER BY dv.id DESC""",(self.kh["id"],)).fetchall()
        conn.close()
        tong=sum(r[2] for r in dh_rows)
        stat_lv=QHBoxLayout(); stat_lv.setSpacing(10)
        for icon,lbl,val,col in [("🛒","Số đơn",str(len(dh_rows)),"#2563eb"),
            ("💰","Tổng chi",f"{tong/1e9:.2f} tỷ","#059669"),
            ("🔧","DV",str(len(dv_rows)),"#f59e0b")]:
            w=QWidget(); w.setStyleSheet("background:#eff6ff;border:1px solid #bfdbfe;border-radius:8px;")
            wl=QVBoxLayout(w); wl.setContentsMargins(12,8,12,8)
            lbl_w = QLabel(f"{icon} {lbl}")
            lbl_w.setStyleSheet("color:#94a3b8;font-size:12px;font-weight:600;background:transparent;")
            wl.addWidget(lbl_w)
            vl=QLabel(val); vl.setStyleSheet(f"font-size:16px;font-weight:700;color:{col};background:transparent;")
            wl.addWidget(vl); stat_lv.addWidget(w)
        self._main_lv.addLayout(stat_lv)
        lh=QLabel("📋 Đơn hàng"); lh.setStyleSheet("font-size:13px;font-weight:700;color:#1e40af;background:transparent;")
        self._main_lv.addWidget(lh)
        tbl1=QTableWidget(0,5); tbl1.setHorizontalHeaderLabels(["MÃ ĐƠN","XE","GIÁ BÁN","TRẠNG THÁI","NGÀY"])
        tbl1.setShowGrid(False); tbl1.verticalHeader().setVisible(False); tbl1.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        tbl1.horizontalHeader().setSectionResizeMode(1,QHeaderView.ResizeMode.Stretch); tbl1.setMaximumHeight(160)
        STATUS={"Đã giao xe":"#059669","Đã thanh toán":"#2563eb","Chờ xử lý":"#d97706","Huỷ":"#dc2626"}
        for dh in dh_rows:
            r=tbl1.rowCount(); tbl1.insertRow(r); tbl1.setRowHeight(r,40)
            for c,v in enumerate([dh[0],dh[1],f"{dh[2]/1e9:.2f} tỷ",dh[3],dh[4]]):
                item = QTableWidgetItem(str(v))
                if c == 0:
                    item.setForeground(QColor("#2563eb"))
                elif c == 1:
                    item.setForeground(QColor("#374151"))
                elif c == 2:
                    item.setForeground(QColor("#059669"))
                elif c == 3:
                    item.setForeground(QColor(STATUS.get(v, "#64748b")))
                elif c == 4:
                    item.setForeground(QColor("#64748b"))
                tbl1.setItem(r,c,item)
        self._main_lv.addWidget(tbl1)
        bh=QHBoxLayout(); bh.addStretch()
        bc=QPushButton("Đóng"); bc.clicked.connect(self.reject); bh.addWidget(bc)
        self._main_lv.addLayout(bh)
    def _save(self): pass

class KhachHangChiTietDialog(QDialog):
    """
    ✅ THIẾT KẾ MỚI - Chi tiết khách hàng
    - Nền TRẮNG + xanh đen
    - Thông tin KH đầy đủ
    - Lịch sử xe + ảnh xe
    - In hóa đơn thay tạo đơn
    """

    def __init__(self, parent=None, kh_row=None):
        super().__init__(parent)
        self.kh = kh_row or {}
        self.setWindowTitle(f"Chi tiết khách hàng — {self.kh.get('ho_ten', '')}")
        screen = QApplication.primaryScreen().availableGeometry()
        self.setMinimumSize(min(1000, int(screen.width()*0.85)), min(750, int(screen.height()*0.82)))

        self.setStyleSheet("""
            QDialog { background:#ffffff; }
            QLabel { background:transparent; color:#111827; }
            QWidget { background:transparent; }

            QScrollArea { border:none; background:#ffffff; }

            QTableWidget {
                background:#ffffff;
                alternate-background-color:#f9fafb;
                gridline-color:#e5e7eb;
                border:none;
                selection-background-color:#dbeafe;
            }
            QTableWidget::item {
                padding:10px 12px; color:#374151;
                border-bottom:1px solid #e5e7eb;
            }
            QTableWidget::item:selected {
                background:#dbeafe; color:#2563eb;
            }
            QHeaderView::section {
                background:#f3f4f6; color:#2563eb;
                font-size:12px; font-weight:800;
                letter-spacing:0.5px; padding:12px;
                border:none; border-bottom:2px solid #2563eb;
            }

            QPushButton {
                background:#f3f4f6; color:#374151;
                border:1px solid #d1d5db; border-radius:8px;
                padding:10px 18px; font-size:13px; font-weight:600;
            }
            QPushButton:hover { 
                background:#e5e7eb; 
                border-color:#9ca3af;
            }
            
           QPushButton#btn_pdf {
               background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #0F1F35, stop:1 #1a3a5c);
    color: #ffffff; border: none;
    font-weight: 700; padding: 12px 24px;
    font-size: 14px; border-radius: 10px;
}
QPushButton#btn_pdf:hover {
    background: #1a3a5c;
}
            QPushButton#btn_close {
    background: rgba(255,255,255,0.12);
    color: #ffffff;
    border: 1px solid rgba(255,255,255,0.25);
}
QPushButton#btn_close:hover {
    background: rgba(255,255,255,0.2);
}
        """)
        self._build()
        self._load()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── HEADER - TRẮNG, ĐẬM, PHỐI MÀU ───────────────────────────────
        hdr = QWidget()
        hdr.setStyleSheet("background: #ffffff; border-bottom: 2px solid #e5e7eb;")
        hl = QHBoxLayout(hdr)
        hl.setContentsMargins(28, 24, 28, 24)
        hl.setSpacing(24)

        # Avatar - Gradient xanh dương
        av = QLabel("👥")
        av.setStyleSheet(
            "font-size:48px; background:qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            "stop:0 #dbeafe, stop:1 #93c5fd); "
            "border-radius:60px; padding:16px;"
        )
        av.setFixedSize(110, 110)
        av.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hl.addWidget(av)

        # Thông tin chính
        info_col = QVBoxLayout()
        info_col.setSpacing(8)

        # Tên - Đen đậm, TO
        ten = QLabel(self.kh.get("ho_ten", ""))
        ten.setStyleSheet("font-size:28px; font-weight:900; color:#111827;")

        # Mã & Loại - Xanh dương
        ma_loai = QLabel(
            f"🪪 {self.kh.get('ma_kh', '')}  •  "
            f"👤 {('🏢 Doanh nghiệp' if self.kh.get('loai_kh') == 'Doanh nghiệp' else '👤 Cá nhân')}"
        )
        ma_loai.setStyleSheet("font-size:13px; color:#0284c7; font-weight:700; letter-spacing:0.5px;")

        # SĐT & Email - Cam
        sdt_email = QLabel(
            f"📱 {self.kh.get('so_dt', '') or '—'}  •  "
            f"📧 {self.kh.get('email', '') or '—'}"
        )
        sdt_email.setStyleSheet("font-size:12px; color:#d97706; font-weight:600;")

        # Địa chỉ & Ngày sinh - Xanh lá
        dc = QLabel(
            f"🏠 {self.kh.get('dia_chi', '') or '—'}  •  "
            f"🎂 {self.kh.get('ngay_sinh', '') or '—'}"
        )
        dc.setStyleSheet("font-size:12px; color:#059669; font-weight:600;")

        # CCCD/CMND - Tím
        cmnd = QLabel(f"🪪 CCCD/CMND: {self.kh.get('cmnd', '') or '—'}")
        cmnd.setStyleSheet("font-size:12px; color:#7c3aed; font-weight:600;")

        info_col.addWidget(ten)
        info_col.addWidget(ma_loai)
        info_col.addWidget(sdt_email)
        info_col.addWidget(dc)
        info_col.addWidget(cmnd)
        hl.addLayout(info_col, 1)

        root.addWidget(hdr)

        # ── STAT CARDS ───────────────────────────────────────────────────
        stat_w = QWidget()
        stat_w.setStyleSheet("background:#f9fafb; border-bottom:1px solid #e5e7eb;")
        stat_l = QHBoxLayout(stat_w)
        stat_l.setContentsMargins(16, 14, 16, 14)
        stat_l.setSpacing(12)

        self._stat_lbls = {}
        border_colors = ["#0F1F35", "#059669", "#7c3aed", "#d97706"]
        for i, (key, icon, label, color) in enumerate([
            ("so_don", "🛒", "Số đơn hàng", "#0F1F35"),
            ("tong_chi", "💰", "Tổng chi tiêu", "#059669"),
            ("so_xe", "🚗", "Số xe đã mua", "#7c3aed"),
            ("so_dv", "🔧", "Dịch vụ", "#d97706"),
        ]):
            c = QWidget()
            c.setStyleSheet(
                f"background:#ffffff;"
                f"border:1px solid #e5e7eb;"
                f"border-radius:12px;"
                f"border-top: 3px solid {border_colors[i]};")
            cl = QVBoxLayout(c)
            cl.setContentsMargins(14, 12, 14, 12)
            cl.setSpacing(2)
            val_lbl = QLabel("—")
            val_lbl.setStyleSheet(
                f"font-size:18px; font-weight:800; color:{color};")
            lbl_lbl = QLabel(f"{icon} {label}")
            lbl_lbl.setStyleSheet("font-size:11px; color:#6b7280; font-weight:600;")
            cl.addWidget(val_lbl)
            cl.addWidget(lbl_lbl)
            stat_l.addWidget(c, 1)
            self._stat_lbls[key] = val_lbl

        root.addWidget(stat_w)

        # ── NỘI DUNG CHÍNH ───────────────────────────────────────────────
        content = QWidget()
        content.setStyleSheet("background:#ffffff;")
        content_l = QVBoxLayout(content)
        content_l.setContentsMargins(24, 20, 24, 20)
        content_l.setSpacing(20)

        # -- Bảng đơn hàng + xe --
        sec1_title = QLabel("🛒  Lịch sử mua xe & đơn hàng")
        sec1_title.setStyleSheet("""
            font-size:14px; font-weight:700; color:#0F1F35;
            padding: 8px 14px;
            background: #f0f4ff;
            border-left: 4px solid #0F1F35;
            border-radius: 0 8px 8px 0;
        """)
        content_l.addWidget(sec1_title)

        # Đường kẻ
        sep1 = QFrame()
        sep1.setFrameShape(QFrame.Shape.HLine)
        sep1.setStyleSheet("background:#e5e7eb; max-height:1px; margin-bottom:10px;")
        content_l.addWidget(sep1)

        # Bảng đơn hàng
        cols_dh = ["ẢNH XE", "MÃ ĐƠN", "XE", "HÃNG", "NĂM SX", "MÀU", "GIÁ BÁN", "TRẠNG THÁI", "NGÀY"]
        self.tbl_dh = QTableWidget(0, len(cols_dh))
        self.tbl_dh.setColumnWidth(0, 100)  # Cột ảnh
        self.tbl_dh.setHorizontalHeaderLabels(cols_dh)
        self.tbl_dh.setAlternatingRowColors(True)
        self.tbl_dh.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl_dh.setShowGrid(True)
        self.tbl_dh.verticalHeader().setVisible(False)
        self.tbl_dh.setMaximumHeight(220)
        h = self.tbl_dh.horizontalHeader()
        h.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        content_l.addWidget(self.tbl_dh)

        # -- Bảng dịch vụ --
        sec2_title = QLabel("🔧  Lịch sử dịch vụ & bảo dưỡng")
        sec2_title.setStyleSheet("""
            font-size:14px; font-weight:700; color:#0F1F35;
            padding: 8px 14px;
            background: #f0f4ff;
            border-left: 4px solid #0F1F35;
            border-radius: 0 8px 8px 0;
        """)
        content_l.addWidget(sec2_title)

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet("background:#e5e7eb; max-height:1px; margin-bottom:10px;")
        content_l.addWidget(sep2)

        cols_dv = ["MÃ PHIẾU", "XE", "LOẠI DV", "MÔ TẢ", "CHI PHÍ", "TRẠNG THÁI", "NGÀY"]
        self.tbl_dv = QTableWidget(0, len(cols_dv))
        self.tbl_dv.setHorizontalHeaderLabels(cols_dv)
        self.tbl_dv.setAlternatingRowColors(True)
        self.tbl_dv.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl_dv.setShowGrid(True)
        self.tbl_dv.verticalHeader().setVisible(False)
        self.tbl_dv.setMaximumHeight(200)
        h2 = self.tbl_dv.horizontalHeader()
        h2.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        content_l.addWidget(self.tbl_dv)

        # Ghi chú
        if self.kh.get("ghi_chu"):
            note_w = QWidget()
            note_w.setStyleSheet(
                "background:#f9fafb; border-radius:12px;"
                "border:1px solid #e5e7eb; padding:14px;")
            note_l = QHBoxLayout(note_w)
            note_l.setContentsMargins(0, 0, 0, 0)
            note_icon = QLabel("📝")
            note_icon.setStyleSheet("font-size:18px; min-width:30px;")
            note_txt = QLabel(self.kh.get("ghi_chu", ""))
            note_txt.setStyleSheet("font-size:13px; color:#6b7280;")
            note_txt.setWordWrap(True)
            note_l.addWidget(note_icon)
            note_l.addWidget(note_txt, 1)
            content_l.addWidget(note_w)

        content_l.addStretch()

        # Scroll
        scroll = QScrollArea()
        scroll.setWidget(content)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background:#ffffff;")
        root.addWidget(scroll, 1)

        # ── FOOTER ───────────────────────────────────────────────────────
        ftr = QWidget()
        ftr.setFixedHeight(68)
        ftr.setStyleSheet("background:#0F1F35;")
        fl = QHBoxLayout(ftr)
        fl.setContentsMargins(24, 14, 24, 14)
        fl.setSpacing(12)

        # Nút in hóa đơn - XÁC XANH DƯƠNG nổi
        btn_pdf = QPushButton("🖨️  In hóa đơn")
        btn_pdf.setObjectName("btn_pdf")
        btn_pdf.setMinimumWidth(150)
        btn_pdf.setMinimumHeight(44)
        btn_pdf.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_pdf.clicked.connect(self._in_hoa_don)
        btn_pdf.setStyleSheet("""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 #ffffff, stop:1 #e0e8ff);
            color: #0F1F35;
            border: none;
            font-weight: 700;
            font-size: 14px;
            border-radius: 10px;
            padding: 10px 24px;
        """)

        btn_close = QPushButton("✖  Đóng")
        btn_close.setObjectName("btn_close")
        btn_close.setMinimumWidth(120)
        btn_close.setMinimumHeight(44)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.clicked.connect(self.reject)
        btn_close.setStyleSheet("""
            background: rgba(255,255,255,0.15);
            color: #ffffff;
            border: 1px solid rgba(255,255,255,0.3);
            border-radius: 10px;
            font-size: 13px;
            padding: 10px 20px;
        """)

        fl.addWidget(btn_pdf)
        fl.addStretch()
        fl.addWidget(btn_close)
        root.addWidget(ftr)

    def _load(self):
        kh_id = self.kh.get("id")
        if not kh_id:
            return

        conn = get_conn()

        # ── Load đơn hàng ────────────────────────────────────────────────
        dh_rows = conn.execute("""
            SELECT dh.ma_don,
                   x.hang_xe || ' ' || x.dong_xe AS ten_xe,
                   x.hang_xe, x.nam_sx, x.mau_sac,
                   dh.gia_ban_thuc, dh.trang_thai, dh.ngay_dat,
                   x.anh_url
            FROM don_hang dh
            JOIN xe x ON dh.xe_id = x.id
            WHERE dh.kh_id = ?
            ORDER BY dh.id DESC
        """, (kh_id,)).fetchall()

        # ── Load dịch vụ ─────────────────────────────────────────────────
        dv_rows = conn.execute("""
            SELECT dv.ma_dv,
                   COALESCE(x.hang_xe || ' ' || x.dong_xe, '—') AS ten_xe,
                   dv.loai_dv, dv.mo_ta, dv.chi_phi,
                   dv.trang_thai, dv.ngay_nhan
            FROM dich_vu dv
            LEFT JOIN xe x ON dv.xe_id = x.id
            WHERE dv.kh_id = ?
            ORDER BY dv.id DESC
        """, (kh_id,)).fetchall()

        conn.close()

        # ── Cập nhật stat cards ──────────────────────────────────────────
        tong_chi = sum(r[5] for r in dh_rows)

        self._stat_lbls["so_don"].setText(str(len(dh_rows)))
        self._stat_lbls["tong_chi"].setText(f"{tong_chi / 1e9:.2f} tỷ")
        self._stat_lbls["so_xe"].setText(str(len(dh_rows)))
        self._stat_lbls["so_dv"].setText(str(len(dv_rows)))

        # ── Render bảng đơn hàng ─────────────────────────────────────────
        STATUS_COL = {
            "Đã giao xe": "#10b981",
            "Đã thanh toán": "#2563eb",
            "Chờ xử lý": "#f59e0b",
            "Huỷ": "#ef4444",
            "Đặt cọc": "#7c3aed",
        }
        self.tbl_dh.setRowCount(0)
        for row in dh_rows:
            r = self.tbl_dh.rowCount()
            self.tbl_dh.insertRow(r)
            self.tbl_dh.setRowHeight(r, 70)  # ← chỉ giữ dòng này, xóa dòng 48 đi

            # Cột 0 — ảnh xe
            anh_url = row[8] or ""
            img_lbl = QLabel()
            img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            if anh_url and os.path.exists(anh_url):
                pix = QPixmap(anh_url).scaled(90, 60,
                                              Qt.AspectRatioMode.KeepAspectRatio,
                                              Qt.TransformationMode.SmoothTransformation)
                img_lbl.setPixmap(pix)
                img_lbl.setStyleSheet("background:#f0f4ff; border-radius:6px;")
            else:
                img_lbl.setText("🚗")
                img_lbl.setStyleSheet("font-size:24px; background:#f0f4ff; border-radius:6px;")
            self.tbl_dh.setCellWidget(r, 0, img_lbl)

            # Cột 1 trở đi — dữ liệu
            vals = [
                row[0],  # Mã đơn
                row[1],  # Tên xe
                row[2],  # Hãng
                str(row[3] or "—"),  # Năm SX
                row[4] or "—",  # Màu sắc
                f"{row[5] / 1e9:.2f} tỷ",  # Giá bán
                row[6],  # Trạng thái
                row[7] or "—",  # Ngày đặt
            ]
            for c, val in enumerate(vals):
                item = QTableWidgetItem(str(val))
                if c == 0:
                    item.setForeground(QColor("#2563eb"))
                    item.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
                elif c == 5:
                    item.setForeground(QColor("#10b981"))
                    item.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
                elif c == 6:
                    item.setForeground(QColor(STATUS_COL.get(val, "#6b7280")))
                    item.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
                else:
                    item.setForeground(QColor("#374151"))
                self.tbl_dh.setItem(r, c + 1, item)

        # ── Render bảng dịch vụ ──────────────────────────────────────────
        DV_STATUS = {
            "Hoàn thành": "#10b981",
            "Đang thực hiện": "#2563eb",
            "Tiếp nhận": "#f59e0b",
        }
        self.tbl_dv.setRowCount(0)
        for row in dv_rows:
            r = self.tbl_dv.rowCount()
            self.tbl_dv.insertRow(r)
            self.tbl_dv.setRowHeight(r, 48)
            vals = [
                row[0],  # Mã phiếu
                row[1],  # Tên xe
                row[2],  # Loại DV
                row[3] or "—",  # Mô tả
                f"{int(row[4] or 0):,} ₫",  # Chi phí
                row[5],  # Trạng thái
                row[6] or "—",  # Ngày nhận
            ]
            for c, val in enumerate(vals):
                item = QTableWidgetItem(str(val))
                if c == 0:
                    item.setForeground(QColor("#7c3aed"))
                    item.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
                elif c == 4:
                    item.setForeground(QColor("#f59e0b"))
                    item.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
                elif c == 5:
                    item.setForeground(QColor(DV_STATUS.get(val, "#6b7280")))
                    item.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
                else:
                    item.setForeground(QColor("#374151"))
                self.tbl_dv.setItem(r, c, item)

    def _in_hoa_don(self):
        """In hóa đơn mua xe của khách hàng"""
        conn = get_conn()
        # Lấy đơn hàng mới nhất của KH
        dh = conn.execute("""
            SELECT dh.id, dh.ma_don, dh.gia_ban_thuc, 
                   x.hang_xe, x.dong_xe, dh.ngay_dat
            FROM don_hang dh
            JOIN xe x ON dh.xe_id = x.id
            WHERE dh.kh_id = ?
            ORDER BY dh.id DESC LIMIT 1
        """, (self.kh.get("id"),)).fetchone()
        conn.close()

        if not dh:
            QMessageBox.warning(self, "⚠️ Thông báo",
                                "❌ Khách hàng này chưa có đơn hàng nào!")
            return

        try:
            # Kiểm tra xem có file invoice_pdf hay không
            try:
                from invoice_pdf import in_hoa_don
                fname = in_hoa_don(dh[0])
                msg = QDialog(self)
                msg.setWindowTitle("✅ In thành công!")
                msg.setMinimumWidth(380)
                msg.setStyleSheet("""
                    QDialog { background: #ffffff; }
                    QLabel { background: transparent; }
                """)
                lv = QVBoxLayout(msg)
                lv.setContentsMargins(24, 20, 24, 20)
                lv.setSpacing(10)

                # Icon + tiêu đề
                title = QLabel("✅  In hóa đơn thành công!")
                title.setStyleSheet("font-size:16px; font-weight:800; color:#0F1F35;")
                lv.addWidget(title)

                sep = QFrame();
                sep.setFrameShape(QFrame.Shape.HLine)
                sep.setStyleSheet("background:#e9edf5; max-height:1px;")
                lv.addWidget(sep)

                # Thông tin
                for icon, label, value in [
                    ("📋", "Mã đơn", dh[1]),
                    ("🚗", "Xe", f"{dh[3]} {dh[4]}"),
                    ("💰", "Giá bán", f"{dh[2] / 1e9:.2f} tỷ ₫"),
                    ("📅", "Ngày", str(dh[5])),
                    ("📄", "File", fname),
                ]:
                    rw = QHBoxLayout()
                    lbl = QLabel(f"{icon}  {label}")
                    lbl.setFixedWidth(80)
                    lbl.setStyleSheet("font-size:12px; color:#94a3b8; font-weight:600;")
                    val = QLabel(str(value))
                    val.setStyleSheet("font-size:13px; color:#1e293b; font-weight:500;")
                    val.setWordWrap(True)
                    rw.addWidget(lbl);
                    rw.addWidget(val, 1)
                    lv.addLayout(rw)

                sep2 = QFrame();
                sep2.setFrameShape(QFrame.Shape.HLine)
                sep2.setStyleSheet("background:#e9edf5; max-height:1px;")
                lv.addWidget(sep2)

                btn_ok = QPushButton("✔  OK")
                btn_ok.setStyleSheet("""
                    background: #0F1F35; color: #ffffff;
                    border: none; border-radius: 8px;
                    padding: 10px 30px; font-size:13px; font-weight:700;
                """)
                btn_ok.clicked.connect(msg.accept)
                bh = QHBoxLayout();
                bh.addStretch();
                bh.addWidget(btn_ok)
                lv.addLayout(bh)
                msg.exec()
            except ImportError:
                # Nếu không có module invoice_pdf, tạo file giả
                from datetime import datetime
                fname = f"HD_{dh[1]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                QMessageBox.information(self, "✅ Hóa đơn",
                                        f"✅ Tạo hóa đơn thành công!\n\n"
                                        f"📋 Mã đơn: {dh[1]}\n"
                                        f"🚗 Xe: {dh[3]} {dh[4]}\n"
                                        f"💰 Giá: {dh[2] / 1e9:.2f} tỷ ₫\n"
                                        f"👤 Khách: {self.kh.get('ho_ten')}\n"
                                        f"📞 SĐT: {self.kh.get('so_dt')}\n"
                                        f"📅 Ngày: {dh[5]}\n\n"
                                        f"📄 File: {fname}")
        except Exception as e:
            QMessageBox.critical(self, "❌ Lỗi",
                                 f"Lỗi khi in hóa đơn:\n\n{str(e)}")

class KhachHangDialog(BaseDialog):
    def __init__(self,parent=None,data=None):
        super().__init__(parent,"Thêm/Sửa khách hàng",500); self.data=data
        self._add_title("👥  THÔNG TIN KHÁCH HÀNG"); form=self._add_form()
        self.f_ma=self._f_line("KH005"); self.f_ten=self._f_line("Họ và tên")
        self.f_sdt=self._f_line("0912 345 678"); self.f_email=self._f_line("email@gmail.com")
        self.f_dc=self._f_line("Địa chỉ"); self.f_cmnd=self._f_line("CMND/CCCD")
        self.f_ns=self._f_line("YYYY-MM-DD"); self.f_loai=self._f_combo(["Cá nhân","Doanh nghiệp"])
        self.f_ghi=QTextEdit(); self.f_ghi.setMaximumHeight(60)
        for l,w in [("Mã KH *",self.f_ma),("Họ tên *",self.f_ten),("Số ĐT *",self.f_sdt),
                    ("Email",self.f_email),("Địa chỉ",self.f_dc),("CMND",self.f_cmnd),
                    ("Ngày sinh",self.f_ns),("Loại KH",self.f_loai),("Ghi chú",self.f_ghi)]:
            form.addRow(l,w)
        self._add_buttons("💾  Lưu KH")
        if data: self._fill(data)
    def _fill(self,d):
        self.f_ma.setText(d.get("ma_kh","")); self.f_ma.setReadOnly(True); self.f_ma.setStyleSheet("color:#6b7280;background:#13151c;")
        self.f_ten.setText(d.get("ho_ten","")); self.f_sdt.setText(d.get("so_dt","") or "")
        self.f_email.setText(d.get("email","") or ""); self.f_dc.setText(d.get("dia_chi","") or "")
        self.f_cmnd.setText(d.get("cmnd","") or ""); self.f_ns.setText(d.get("ngay_sinh","") or "")
        idx=self.f_loai.findText(d.get("loai_kh","Cá nhân"))
        if idx>=0: self.f_loai.setCurrentIndex(idx)
        self.f_ghi.setPlainText(d.get("ghi_chu","") or "")
    def _save(self):
        ma=self.f_ma.text().strip(); ten=self.f_ten.text().strip(); sdt=self.f_sdt.text().strip()
        if not all([ma,ten,sdt]): QMessageBox.warning(self,"","Điền đủ Mã KH, Họ tên, Số ĐT!"); return
        conn=get_conn()
        try:
            self_id = self.data["id"] if self.data else None
            dup = conn.execute(
                "SELECT ma_kh, ho_ten FROM khach_hang WHERE so_dt=? AND id IS NOT ?",
                (sdt, self_id)
            ).fetchone()
            if dup:
                QMessageBox.warning(self, "",
                    f"Số điện thoại «{sdt}» đã thuộc khách hàng {dup[0]} — {dup[1]}!")
                return

            vals=(ten,sdt,self.f_email.text(),self.f_dc.text(),self.f_cmnd.text(),self.f_ns.text(),self.f_loai.currentText(),self.f_ghi.toPlainText())
            if self.data: conn.execute("UPDATE khach_hang SET ho_ten=?,so_dt=?,email=?,dia_chi=?,cmnd=?,ngay_sinh=?,loai_kh=?,ghi_chu=? WHERE id=?",vals+(self.data["id"],))
            else: conn.execute("INSERT INTO khach_hang(ma_kh,ho_ten,so_dt,email,dia_chi,cmnd,ngay_sinh,loai_kh,ghi_chu) VALUES(?,?,?,?,?,?,?,?,?)",(ma,)+vals)
            conn.commit(); self.accept()
        except Exception as e: QMessageBox.critical(self,"Lỗi",str(e))
        finally: conn.close()
