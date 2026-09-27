"""
views/bao_cao_view.py — Màn hình Báo cáo riêng
File MỚI — thêm vào views/
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QComboBox, QMessageBox, QTabWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
import matplotlib
matplotlib.use("QtAgg")
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import pandas as pd
from database import get_conn
from datetime import datetime


class BaoCaoView(QWidget):
    def __init__(self, current_user=None):
        super().__init__()
        self.setObjectName("page_bao_cao")
        self.current_user = current_user or {"role":"admin","id":None}
        self._build()
        self._load()
    def _build(self):
        root = QVBoxLayout(self); root.setContentsMargins(0,0,0,0); root.setSpacing(0)
        # Title bar
        tb = QWidget(); tb.setObjectName("toolbar_widget")
        tb.setStyleSheet("background:#ffffff;border-bottom:2px solid #e2e8f0;")
        tbh = QHBoxLayout(tb); tbh.setContentsMargins(18,12,18,12)
        title = QLabel("📊  Báo cáo & Thống kê")
        title.setStyleSheet("font-size:17px;font-weight:700;color:#0f172a;background:transparent;")
        self.cmb_year = QComboBox()
        cur_year = datetime.now().year
        for y in range(cur_year, cur_year-5, -1):
            self.cmb_year.addItem(str(y), y)
        self.cmb_year.currentIndexChanged.connect(self._load)
        btn_excel = QPushButton("📊 Xuất Excel tổng hợp")
        btn_excel.setObjectName("btn_excel")
        btn_excel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_excel.clicked.connect(self._export_excel)
        btn_pdf = QPushButton("📄 Xuất PDF báo cáo")
        btn_pdf.setObjectName("btn_print")
        btn_pdf.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_pdf.clicked.connect(self._export_pdf)
        tbh.addWidget(title); tbh.addStretch()
        tbh.addWidget(QLabel("Năm:"))
        tbh.addWidget(self.cmb_year)

        btn_refresh = QPushButton("🔄 Làm mới")
        btn_refresh.setObjectName("btn_refresh")
        btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_refresh.setStyleSheet("""
            QPushButton {
                background:#10b981;color:white;border:none;
                border-radius:8px;padding:8px 16px;
                font-size:13px;font-weight:600;
            }
            QPushButton:hover { background:#059669; }
            QPushButton:pressed { background:#047857; }
        """)
        btn_refresh.clicked.connect(self._load)
        tbh.addWidget(btn_refresh)

        tbh.addWidget(btn_excel); tbh.addWidget(btn_pdf)
        root.addWidget(tb)
        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabBar::tab{padding:10px 20px;font-size:13px;font-weight:600;
                color:#64748b;background:#f1f5f9;border:none;
                border-bottom:2px solid transparent;}
            QTabBar::tab:selected{color:#7c3aed;border-bottom:2px solid #7c3aed;background:#ffffff;}
            QTabBar::tab:hover{color:#1e40af;background:#e0e7ff;}
            QTabWidget::pane{border:none;background:#ffffff;}
        """)
        # Tab 1: Doanh thu
        self.tab_dt = self._build_tab_doanhthu()
        # Tab 2: Xe tồn kho
        self.tab_xe = self._build_tab_xe()
        # Tab 3: Đơn hàng
        self.tab_dh = self._build_tab_donhang()
        # Tab 4: Khách hàng
        self.tab_kh = self._build_tab_kh()

        self.tabs.addTab(self.tab_dt, "💰  Doanh thu")
        self.tabs.addTab(self.tab_xe, "🚗  Tồn kho xe")
        self.tabs.addTab(self.tab_dh, "📋  Đơn hàng")
        self.tabs.addTab(self.tab_kh, "👥  Khách hàng")
        root.addWidget(self.tabs, 1)

    def _build_tab_doanhthu(self):
        w = QWidget(); lv = QVBoxLayout(w)
        lv.setContentsMargins(16,16,16,16); lv.setSpacing(12)

        # Stat cards
        self.sc_row = QHBoxLayout(); self.sc_row.setSpacing(10)
        self.lbl_tong_dt    = self._stat_card("💰","TỔNG DOANH THU","0 ₫","#4ade80")
        self.lbl_so_don     = self._stat_card("📋","SỐ ĐƠN HÀNG","0","#60a5fa")
        self.lbl_dt_thang   = self._stat_card("📅","THÁNG NÀY","0 ₫","#f59e0b")
        self.lbl_tb_don     = self._stat_card("📊","TB MỖI ĐƠN","0 ₫","#a78bfa")
        for c in [self.lbl_tong_dt, self.lbl_so_don, self.lbl_dt_thang, self.lbl_tb_don]:
            self.sc_row.addWidget(c)
        lv.addLayout(self.sc_row)

        # Biểu đồ doanh thu theo tháng
        self.fig_dt = Figure(facecolor="#ffffff", figsize=(10,3.5))
        self.canvas_dt = FigureCanvasQTAgg(self.fig_dt)
        self.canvas_dt.setStyleSheet("border-radius:12px;border:1px solid #e2e8f0;")
        self.canvas_dt.setMinimumHeight(300)
        lv.addWidget(self.canvas_dt)

        # Bảng chi tiết theo tháng
        lbl = QLabel("Chi tiết doanh thu theo tháng")
        lbl.setStyleSheet("font-size:13px;font-weight:600;color:#0f172a;background:transparent;")
        lv.addWidget(lbl)
        self.tbl_dt = self._make_table(
            ["THÁNG","SỐ ĐƠN","DOANH THU","GIÁ TB","CHIẾT KHẤU","THỰC THU"])
        self.tbl_dt.setMaximumHeight(200)
        lv.addWidget(self.tbl_dt)
        return w

    def _build_tab_xe(self):
        w = QWidget(); lv = QVBoxLayout(w)
        lv.setContentsMargins(16,16,16,16); lv.setSpacing(12)

        # Chart
        self.fig_xe = Figure(facecolor="#ffffff", figsize=(10,3.5))
        self.canvas_xe = FigureCanvasQTAgg(self.fig_xe)
        self.canvas_xe.setStyleSheet("border-radius:12px;border:1px solid #e2e8f0;")
        self.canvas_xe.setMinimumHeight(300)
        lv.addWidget(self.canvas_xe)

        lbl = QLabel("Danh sách xe theo trạng thái")
        lbl.setStyleSheet("font-size:13px;font-weight:600;color:#0f172a;background:transparent;")
        lv.addWidget(lbl)
        self.tbl_xe = self._make_table(["MÃ XE","TÊN XE","NĂM","GIÁ BÁN","TRẠNG THÁI"])
        lv.addWidget(self.tbl_xe)
        return w

    def _build_tab_donhang(self):
        w = QWidget(); lv = QVBoxLayout(w)
        lv.setContentsMargins(16,16,16,16); lv.setSpacing(12)
        lbl = QLabel("Báo cáo đơn hàng")
        lbl.setStyleSheet("font-size:13px;font-weight:600;color:#0f172a;background:transparent;")
        lv.addWidget(lbl)
        self.tbl_dh = self._make_table(
            ["MÃ ĐƠN","XE","KHÁCH HÀNG","NHÂN VIÊN","GIÁ BÁN","TRẠNG THÁI","NGÀY ĐẶT"])
        lv.addWidget(self.tbl_dh)
        return w

    def _build_tab_kh(self):
        w = QWidget(); lv = QVBoxLayout(w)
        lv.setContentsMargins(16,16,16,16); lv.setSpacing(12)
        lbl = QLabel("Thống kê khách hàng")
        lbl.setStyleSheet("font-size:13px;font-weight:600;color:#0f172a;background:transparent;")
        lv.addWidget(lbl)
        self.tbl_kh = self._make_table(["MÃ KH","HỌ TÊN","SỐ ĐT","SỐ ĐƠN","TỔNG CHI","LOẠI KH"])
        lv.addWidget(self.tbl_kh)
        return w

    def _stat_card(self, icon, label, val, color):
        w = QWidget()
        w.setStyleSheet("background:#ffffff;border-radius:10px;border:1px solid #e2e8f0;border-top:4px solid "+color)
        lv = QVBoxLayout(w); lv.setContentsMargins(16,12,16,12); lv.setSpacing(3)
        li = QLabel(icon); li.setStyleSheet("font-size:18px;background:transparent;")
        ll = QLabel(label); ll.setStyleSheet("font-size:11px;color:#0f172a;font-weight:900;letter-spacing:0.5px;background:transparent;")
        lv2 = QLabel(val); lv2.setStyleSheet(f"font-size:22px;font-weight:800;color:{color};background:transparent;")
        lv.addWidget(li); lv.addWidget(ll); lv.addWidget(lv2)
        w._val_lbl = lv2
        return w

    def _make_table(self, cols):
        t = QTableWidget(0, len(cols))
        t.setHorizontalHeaderLabels(cols)
        # Style header
        header = t.horizontalHeader()
        header_font = QFont("Segoe UI", 11)
        header_font.setBold(True)
        t.horizontalHeader().setFont(header_font)
        t.horizontalHeader().setStyleSheet("background-color:#f1f5f9;color:#0f172a;font-weight:bold;")
        t.setAlternatingRowColors(True)
        t.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        t.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        t.setShowGrid(False); t.verticalHeader().setVisible(False)
        h = t.horizontalHeader()
        for i in range(1, len(cols)-1):
            h.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
        return t

    def _load(self):
        year = self.cmb_year.currentData() or datetime.now().year
        conn = get_conn()

        # ── Doanh thu theo tháng ────────────────────────────────────────
        months_data = []
        tong_dt = 0; so_don_hoan = 0
        for m in range(1, 13):
            rows = conn.execute("""
                SELECT SUM(gia_ban_thuc), SUM(chiet_khau), COUNT(*)
                FROM don_hang
                WHERE strftime('%Y', ngay_dat)=? AND strftime('%m', ngay_dat)=?
                AND trang_thai IN ('Đã thanh toán','Đã giao xe')
            """, (str(year), f"{m:02d}")).fetchone()
            dt = rows[0] or 0; ck = rows[1] or 0; cnt = rows[2] or 0
            months_data.append({"thang":m,"so_don":cnt,"dt":dt,"ck":ck,"thuc_thu":dt-ck})
            tong_dt += dt-ck; so_don_hoan += cnt

        # Update stat cards
        cur_m = datetime.now().month
        dt_thang = months_data[cur_m-1]["thuc_thu"]
        tb_don = (tong_dt / so_don_hoan) if so_don_hoan > 0 else 0

        self.lbl_tong_dt._val_lbl.setText(f"{tong_dt/1e9:.2f} tỷ ₫")
        self.lbl_so_don._val_lbl.setText(str(so_don_hoan))
        self.lbl_dt_thang._val_lbl.setText(f"{dt_thang/1e9:.2f} tỷ ₫")
        self.lbl_tb_don._val_lbl.setText(f"{tb_don/1e6:.0f} triệu ₫")

        # Biểu đồ doanh thu
        self.fig_dt.clear()
        ax = self.fig_dt.add_subplot(111)
        ax.set_facecolor("#f8fafc"); self.fig_dt.set_facecolor("#ffffff")
        x = list(range(1,13))
        y = [d["thuc_thu"]/1e9 for d in months_data]
        bars = ax.bar(x, y, color=["#7c3aed" if i==cur_m-1 else "#3d4470" for i in range(12)], width=0.6, zorder=3)
        for bar,val in zip(bars,y):
            if val > 0:
                ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.01,
                        f"{val:.1f}", ha="center", color="#e2e8f0", fontsize=9)
        ax.set_xticks(x)
        ax.set_xticklabels([f"T{i}" for i in x], color="#64748b", fontsize=9)
        ax.tick_params(colors="#64748b"); ax.spines[:].set_visible(False); ax.yaxis.set_visible(False)
        self.fig_dt.text(0.5,0.97,f"Doanh thu theo tháng năm {year} (tỷ ₫)",
                         ha="center", color="#94a3b8", fontsize=11, fontweight="bold")
        self.canvas_dt.draw()

        # Bảng doanh thu
        self.tbl_dt.setRowCount(0)
        for d in months_data:
            if d["so_don"] > 0:
                r = self.tbl_dt.rowCount(); self.tbl_dt.insertRow(r)
                self.tbl_dt.setRowHeight(r,40)
                vals = [f"Tháng {d['thang']:02d}",str(d["so_don"]),
                        f"{d['dt']/1e9:.3f} tỷ",
                        f"{(d['dt']/d['so_don']/1e6 if d['so_don'] else 0):.0f} tr",
                        f"{d['ck']/1e6:.0f} tr",
                        f"{d['thuc_thu']/1e9:.3f} tỷ"]
                for c,v in enumerate(vals):
                    item = QTableWidgetItem(v)
                    if c in [2,5]: item.setForeground(QColor("#4ade80"))
                    self.tbl_dt.setItem(r,c,item)

        # ── Tab Xe ───────────────────────────────────────────────────────
        xe_rows = conn.execute("SELECT ma_xe,hang_xe,dong_xe,nam_sx,gia_ban,trang_thai FROM xe ORDER BY trang_thai").fetchall()
        # Biểu đồ xe theo hãng
        hang_data = {}
        for xe in xe_rows:
            hang_data[xe[1]] = hang_data.get(xe[1],0)+1
        self.fig_xe.clear()
        ax2 = self.fig_xe.add_subplot(111)
        ax2.set_facecolor("#f8fafc"); self.fig_xe.set_facecolor("#ffffff")
        hangs = list(hang_data.keys()); cnts = list(hang_data.values())
        colors = ["#7c3aed","#60a5fa","#4ade80","#f59e0b","#f87171","#2dd4bf"]
        ax2.bar(range(len(hangs)), cnts, color=colors[:len(hangs)], width=0.5, zorder=3)
        for i,(h,c) in enumerate(zip(hangs,cnts)):
            ax2.text(i, c+0.1, str(c), ha="center", color="#0f172a", fontsize=10, fontweight="bold")
        ax2.set_xticks(range(len(hangs)))
        ax2.set_xticklabels(hangs, rotation=45, ha='right', fontsize=9, color="#475569")
        ax2.tick_params(colors="#475569",labelsize=9); ax2.spines[:].set_visible(False); ax2.yaxis.set_visible(False)
        self.fig_xe.text(0.5,0.97,"Số lượng xe theo hãng",ha="center",color="#475569",fontsize=11,fontweight="bold")
        self.fig_xe.tight_layout()
        self.canvas_xe.draw()

        STATUS_COL={"Còn hàng":"#4ade80","Đặt cọc":"#fbbf24","Đã bán":"#f87171","Bảo dưỡng":"#a855f7"}
        self.tbl_xe.setRowCount(0)
        for xe in xe_rows:
            r=self.tbl_xe.rowCount(); self.tbl_xe.insertRow(r)
            self.tbl_xe.setRowHeight(r,44)
            for c,v in enumerate([xe[0],f"{xe[1]} {xe[2]}",str(xe[3]),f"{xe[4]/1e9:.2f} tỷ",xe[5]]):
                item=QTableWidgetItem(v)
                if c==4: item.setForeground(QColor(STATUS_COL.get(v,"#94a3b8")))
                if c==3: item.setForeground(QColor("#4ade80"))
                self.tbl_xe.setItem(r,c,item)

        # ── Tab Đơn hàng ─────────────────────────────────────────────────
        dh_rows = conn.execute("""
            SELECT dh.ma_don,x.hang_xe||' '||x.dong_xe,kh.ho_ten,nv.ho_ten,
                   dh.gia_ban_thuc,dh.trang_thai,dh.ngay_dat
            FROM don_hang dh JOIN xe x ON dh.xe_id=x.id
            JOIN khach_hang kh ON dh.kh_id=kh.id
            JOIN nhan_vien nv ON dh.nv_id=nv.id
            ORDER BY dh.id DESC""").fetchall()
        STATUS2={"Đã giao xe":"#4ade80","Đã thanh toán":"#60a5fa","Chờ xử lý":"#fbbf24","Huỷ":"#f87171"}
        self.tbl_dh.setRowCount(0)
        for dh in dh_rows:
            r=self.tbl_dh.rowCount(); self.tbl_dh.insertRow(r); self.tbl_dh.setRowHeight(r,44)
            for c,v in enumerate([dh[0],dh[1],dh[2],dh[3],f"{dh[4]/1e9:.2f} tỷ",dh[5],dh[6]]):
                item=QTableWidgetItem(str(v))
                if c==5: item.setForeground(QColor(STATUS2.get(v,"#94a3b8")))
                if c==4: item.setForeground(QColor("#4ade80"))
                self.tbl_dh.setItem(r,c,item)

        # ── Tab Khách hàng ───────────────────────────────────────────────
        kh_rows = conn.execute("""
            SELECT kh.ma_kh,kh.ho_ten,kh.so_dt,
                   COUNT(dh.id) as so_don,
                   COALESCE(SUM(dh.gia_ban_thuc),0) as tong_chi,
                   kh.loai_kh
            FROM khach_hang kh
            LEFT JOIN don_hang dh ON kh.id=dh.kh_id
            GROUP BY kh.id ORDER BY tong_chi DESC""").fetchall()
        self.tbl_kh.setRowCount(0)
        for kh in kh_rows:
            r=self.tbl_kh.rowCount(); self.tbl_kh.insertRow(r); self.tbl_kh.setRowHeight(r,44)
            for c,v in enumerate([kh[0],kh[1],kh[2],str(kh[3]),f"{kh[4]/1e9:.2f} tỷ",kh[5]]):
                item=QTableWidgetItem(v)
                if c==4: item.setForeground(QColor("#4ade80")); item.setFont(QFont("Segoe UI",12,QFont.Weight.Bold))
                self.tbl_kh.setItem(r,c,item)

        conn.close()

    def _export_excel(self):
        year = self.cmb_year.currentData()
        conn = get_conn()
        from openpyxl.styles import PatternFill, Font, Alignment, Border, Side

        def style_sheet(ws, header_color="1E3A5F"):
            thin = Side(style="thin", color="E5E7EB")
            border = Border(left=thin, right=thin, top=thin, bottom=thin)
            # ── Header ──
            for cell in ws[1]:
                cell.fill = PatternFill("solid", fgColor=header_color)
                cell.font = Font(bold=True, color="FFFFFF", size=11)
                cell.alignment = Alignment(horizontal="center", vertical="center")
                cell.border = border
            ws.row_dimensions[1].height = 30
            # ── Data rows ──
            for row_idx, row in enumerate(ws.iter_rows(min_row=2), start=2):
                bg = "F0F9FF" if row_idx % 2 == 0 else "FFFFFF"
                for cell in row:
                    cell.fill = PatternFill("solid", fgColor=bg)
                    cell.border = border
                    cell.alignment = Alignment(vertical="center")
                    cell.font = Font(size=11)
                ws.row_dimensions[row_idx].height = 22
            # ── Auto-fit cột ──
            for col in ws.columns:
                max_len = max((len(str(c.value or "")) for c in col), default=10)
                ws.column_dimensions[col[0].column_letter].width = max_len + 4

        with pd.ExcelWriter(f"bao_cao_tong_hop_{year}.xlsx", engine="openpyxl") as writer:

            # ── Sheet Đơn hàng ────────────────────────────────────────
            dh = conn.execute("""
                SELECT dh.ma_don, x.hang_xe||' '||x.dong_xe,
                       kh.ho_ten, dh.gia_ban_thuc,
                       dh.chiet_khau, dh.trang_thai, dh.ngay_dat
                FROM don_hang dh JOIN xe x ON dh.xe_id=x.id
                JOIN khach_hang kh ON dh.kh_id=kh.id
                ORDER BY dh.id DESC""").fetchall()

            # ✅ FIX: Format số → chuỗi, tránh hiện 1,13E+09
            dh_data = [[
                r[0], r[1], r[2],
                f"{r[3]/1e9:.3f} tỷ",
                f"{r[4]/1e6:.0f} tr" if r[4] else "—",
                r[5], r[6]
            ] for r in dh]

            pd.DataFrame(dh_data, columns=[
                "Mã đơn", "Tên xe", "Khách hàng",
                "Giá bán", "Chiết khấu", "Trạng thái", "Ngày đặt"
            ]).to_excel(writer, sheet_name="Đơn hàng", index=False)

            style_sheet(writer.sheets["Đơn hàng"], "1E3A5F")

            # Tô màu cột Trạng thái (cột F = index 5)
            ws_dh = writer.sheets["Đơn hàng"]
            tt_colors = {
                "Đã giao xe":    "DCFCE7",
                "Đã thanh toán": "DBEAFE",
                "Chờ xử lý":     "FEF3C7",
                "Huỷ":           "FEE2E2",
            }
            for row in ws_dh.iter_rows(min_row=2):
                tt_val = str(row[5].value or "")
                if tt_val in tt_colors:
                    row[5].fill = PatternFill("solid", fgColor=tt_colors[tt_val])
                    row[5].font = Font(bold=True, size=11)
                # Tô màu cột Giá bán (index 3) — xanh lá đậm
                row[3].font = Font(bold=True, color="15803D", size=11)

            # ── Sheet Xe ──────────────────────────────────────────────
            xe = conn.execute(
                "SELECT ma_xe,hang_xe,dong_xe,nam_sx,gia_nhap,gia_ban,trang_thai FROM xe"
            ).fetchall()

            # ✅ FIX: Format giá xe
            xe_data = [[
                r[0], r[1], r[2], r[3],
                f"{r[4]/1e9:.3f} tỷ",
                f"{r[5]/1e9:.3f} tỷ",
                r[6]
            ] for r in xe]

            pd.DataFrame(xe_data, columns=[
                "Mã xe", "Hãng", "Dòng xe", "Năm",
                "Giá nhập", "Giá bán", "Trạng thái"
            ]).to_excel(writer, sheet_name="Xe", index=False)

            style_sheet(writer.sheets["Xe"], "064E3B")

            # Tô màu Trạng thái xe (cột G = index 6)
            ws_xe = writer.sheets["Xe"]
            xe_tt_colors = {
                "Còn hàng":  "DCFCE7",
                "Đặt cọc":   "FEF3C7",
                "Đã bán":    "FEE2E2",
            }
            for row in ws_xe.iter_rows(min_row=2):
                tt_val = str(row[6].value or "")
                if tt_val in xe_tt_colors:
                    row[6].fill = PatternFill("solid", fgColor=xe_tt_colors[tt_val])
                    row[6].font = Font(bold=True, size=11)

            # ── Sheet Khách hàng ──────────────────────────────────────
            kh = conn.execute(
                "SELECT ma_kh,ho_ten,so_dt,email,loai_kh FROM khach_hang"
            ).fetchall()

            pd.DataFrame([list(r) for r in kh], columns=[
                "Mã KH", "Họ tên", "Số ĐT", "Email", "Loại KH"
            ]).to_excel(writer, sheet_name="Khách hàng", index=False)

            style_sheet(writer.sheets["Khách hàng"], "4C1D95")

        conn.close()
        QMessageBox.information(self, "Xuất Excel",
            f"✅ Đã xuất: bao_cao_tong_hop_{year}.xlsx\n"
            f"3 sheet: Đơn hàng, Xe, Khách hàng")

    def _export_pdf(self):
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib import colors
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            import io

            year = self.cmb_year.currentData()
            fname = f"bao_cao_{year}.pdf"
            conn = get_conn()

            doc = SimpleDocTemplate(fname, pagesize=A4,
                rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
            styles = getSampleStyleSheet()
            story = []

            # Tiêu đề
            title_style = ParagraphStyle('title', fontSize=18, fontName='Helvetica-Bold',
                spaceAfter=6, alignment=1, textColor=colors.HexColor('#7c3aed'))
            sub_style = ParagraphStyle('sub', fontSize=10, fontName='Helvetica',
                spaceAfter=16, alignment=1, textColor=colors.grey)
            story.append(Paragraph("BAO CAO TONG HOP", title_style))
            story.append(Paragraph(f"He thong Quan ly Dai ly Xe Hoi AutoViet - Nam {year}", sub_style))

            # Thống kê tổng
            stats = conn.execute("""
                SELECT COUNT(*), COALESCE(SUM(gia_ban_thuc),0),
                       COALESCE(SUM(gia_ban_thuc-chiet_khau),0)
                FROM don_hang WHERE trang_thai IN ('Đã thanh toán','Đã giao xe')
            """).fetchone()

            head_style = ParagraphStyle('head', fontSize=12, fontName='Helvetica-Bold',
                spaceBefore=12, spaceAfter=6, textColor=colors.HexColor('#1a1a2e'))
            story.append(Paragraph("1. THONG KE TONG QUAN", head_style))

            stat_data = [
                ["Chi tieu","Gia tri"],
                ["So don hang hoan thanh", str(stats[0])],
                ["Tong doanh thu", f"{stats[1]/1e9:.3f} ty dong"],
                ["Thuc thu (sau chiet khau)", f"{stats[2]/1e9:.3f} ty dong"],
                ["So xe con hang", str(conn.execute("SELECT COUNT(*) FROM xe WHERE trang_thai='Còn hàng'").fetchone()[0])],
                ["Tong khach hang", str(conn.execute("SELECT COUNT(*) FROM khach_hang").fetchone()[0])],
            ]
            t = Table(stat_data, colWidths=[250,250])
            t.setStyle(TableStyle([
                ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#6d28d9')),
                ('TEXTCOLOR',(0,0),(-1,0),colors.white),
                ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
                ('FONTSIZE',(0,0),(-1,-1),10),
                ('GRID',(0,0),(-1,-1),0.5,colors.lightgrey),
                ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f3f0ff')]),
                ('PADDING',(0,0),(-1,-1),8),
            ]))
            story.append(t); story.append(Spacer(1,12))

            # Bảng đơn hàng
            story.append(Paragraph("2. DANH SACH DON HANG", head_style))
            dh_rows = conn.execute("""
                SELECT dh.ma_don,x.hang_xe||' '||x.dong_xe,kh.ho_ten,
                       dh.gia_ban_thuc/1000000.0,dh.trang_thai,dh.ngay_dat
                FROM don_hang dh JOIN xe x ON dh.xe_id=x.id
                JOIN khach_hang kh ON dh.kh_id=kh.id
                ORDER BY dh.id DESC LIMIT 20""").fetchall()
            dh_data = [["Ma don","Ten xe","Khach hang","Gia (trieu)","Trang thai","Ngay dat"]]
            for r in dh_rows:
                dh_data.append([r[0],r[1][:20],r[2][:15],f"{r[3]:.0f}",r[4],r[5]])
            t2 = Table(dh_data, colWidths=[60,140,100,70,80,70])
            t2.setStyle(TableStyle([
                ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#1e2236')),
                ('TEXTCOLOR',(0,0),(-1,0),colors.white),
                ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
                ('FONTSIZE',(0,0),(-1,-1),8),
                ('GRID',(0,0),(-1,-1),0.3,colors.lightgrey),
                ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f8f8ff')]),
                ('PADDING',(0,0),(-1,-1),5),
            ]))
            story.append(t2)
            conn.close()
            doc.build(story)
            QMessageBox.information(self,"Xuất PDF",f"✅ Đã xuất: {fname}")
        except ImportError:
            QMessageBox.warning(self,"Thiếu thư viện",
                "Cần cài reportlab:\npip install reportlab")
        except Exception as e:
            QMessageBox.critical(self,"Lỗi",str(e))

    def refresh(self): self._load()