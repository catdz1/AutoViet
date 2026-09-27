"""
views/bao_cao_nhanvien_view.py — Admin xem báo cáo theo từng nhân viên
File MỚI — thêm vào views/
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QComboBox, QMessageBox, QTabWidget, QScrollArea,
    QGridLayout, QProgressBar, QDialog, QApplication
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


STYLE = """
QWidget { font-family: 'Segoe UI', Arial; background:#ffffff; }
QWidget#nv_card {
    background:#f8fafc; border-radius:12px;
    border:1px solid #e5e7eb;
}
QWidget#nv_card:hover { background:#f1f5f9; border-color:#2563eb; }
QWidget#nv_card_active { border-left:4px solid #059669; }
QWidget#nv_card_idle { border-left:4px solid #dc2626; }
QLabel#nv_name { font-size:16px; font-weight:900; color:#0f172a; background:transparent; }
QLabel#nv_role { font-size:12px; color:#6b7280; background:transparent; font-weight:600; }
QLabel#stat_val { font-size:22px; font-weight:900; background:transparent; }
QLabel#stat_lbl { font-size:11px; color:#6b7280; font-weight:700; background:transparent; letter-spacing:0.5px; }
QTabWidget::pane { border:none; }
QTabBar::tab {
    padding:12px 20px; font-size:13px; font-weight:700;
    color:#6b7280; background:#ffffff; border:none;
    border-bottom:3px solid transparent;
}
QTabBar::tab:selected { color:#2563eb; border-bottom:3px solid #2563eb; }
QTabBar::tab:hover { color:#374151; background:#f3f4f6; }
QTableWidget {
    background:#ffffff; alternate-background-color:#f8fafc;
    gridline-color:#e5e7eb; border:none;
}
QTableWidget::item { padding:10px 12px; color:#0f172a; font-size:14px; font-weight:600; }
QHeaderView::section {
    background:#f3f4f6; color:#0f172a; font-size:14px;
    font-weight:900; letter-spacing:0.5px; padding:12px; border:none;
    border-bottom:2px solid #2563eb;
}
QPushButton#btn_excel {
    background:#f0fdf4; color:#059669; border:1px solid #86efac;
    border-radius:8px; font-size:13px; font-weight:700; padding:8px 16px;
}
QPushButton#btn_excel:hover { background:#dcfce7; }
QPushButton#btn_pdf {
    background:#eff6ff; color:#0284c7; border:1px solid #93c5fd;
    border-radius:8px; font-size:13px; font-weight:700; padding:8px 16px;
}
QComboBox {
    background:#ffffff; color:#0f172a; border:1px solid #d1d5db;
    border-radius:8px; padding:8px 12px; font-size:14px; font-weight:600;
}
QComboBox QAbstractItemView {
    background:#ffffff; color:#0f172a; border:1px solid #d1d5db;
    selection-background-color:#e0e7ff;
}
"""


class BaoCaoNhanVienView(QWidget):
    """Admin xem báo cáo hoạt động từng nhân viên"""

    def __init__(self):
        super().__init__()
        self.setObjectName("page_bc_nv")
        self.setStyleSheet(STYLE)
        self._sel_nv_id = None
        self._build()
        self._load()

    def _build(self):
        root = QVBoxLayout(self); root.setContentsMargins(0,0,0,0); root.setSpacing(0)

        # Toolbar
        tb = QWidget()
        tb.setStyleSheet("background:#ffffff;border-bottom:2px solid #e5e7eb;")
        tbh = QHBoxLayout(tb); tbh.setContentsMargins(20,14,20,14); tbh.setSpacing(14)
        title = QLabel("👥  Báo cáo Hoạt động Nhân viên")
        title.setStyleSheet("font-size:18px;font-weight:900;color:#0f172a;background:transparent;")

        self.cmb_period = QComboBox()
        cur_y = datetime.now().year
        self.cmb_period.addItem(f"Năm {cur_y}", cur_y)
        self.cmb_period.addItem(f"Năm {cur_y-1}", cur_y-1)
        self.cmb_period.addItem("Tất cả thời gian", 0)
        self.cmb_period.currentIndexChanged.connect(self._load)

        btn_excel = QPushButton("📊 Xuất Excel tổng hợp NV")
        btn_excel.setObjectName("btn_excel")
        btn_excel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_excel.clicked.connect(self._export)

        tbh.addWidget(title); tbh.addStretch()
        tbh.addWidget(QLabel("Thời gian:"))
        tbh.addWidget(self.cmb_period)
        tbh.addWidget(btn_excel)
        root.addWidget(tb)

        # Main content: splitter-like layout
        main = QWidget()
        main_h = QHBoxLayout(main); main_h.setContentsMargins(0,0,0,0); main_h.setSpacing(0)

        # LEFT: Danh sách NV
        left = QWidget()
        left.setFixedWidth(280)
        left.setStyleSheet("background:#f9fafb;border-right:1px solid #e5e7eb;")
        lv = QVBoxLayout(left); lv.setContentsMargins(14,14,14,14); lv.setSpacing(10)

        lh = QLabel("  NHÂN VIÊN")
        lh.setStyleSheet("font-size:12px;font-weight:900;color:#374151;letter-spacing:1px;background:transparent;padding:6px 8px;")
        lv.addWidget(lh)

        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.nv_list_w = QWidget()
        self.nv_list_lv = QVBoxLayout(self.nv_list_w)
        self.nv_list_lv.setContentsMargins(0,0,0,0); self.nv_list_lv.setSpacing(8)
        self.nv_list_lv.addStretch()
        scroll.setWidget(self.nv_list_w)
        lv.addWidget(scroll, 1)
        main_h.addWidget(left)

        # RIGHT: Chi tiết NV được chọn
        self.right = QWidget()
        self.right.setStyleSheet("background:#ffffff;")
        self.right_lv = QVBoxLayout(self.right)
        self.right_lv.setContentsMargins(0,0,0,0)

        # Placeholder
        self.placeholder = QLabel("← Chọn nhân viên để xem báo cáo chi tiết")
        self.placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder.setStyleSheet("color:#9ca3af;font-size:15px;font-weight:600;background:transparent;")
        self.right_lv.addWidget(self.placeholder)

        main_h.addWidget(self.right, 1)
        root.addWidget(main, 1)

    def _load(self):
        year = self.cmb_period.currentData()
        conn = get_conn()
        nv_rows = conn.execute("""
            SELECT nv.id, nv.ma_nv, nv.ho_ten, nv.chuc_vu, nv.trang_thai,
                   COUNT(DISTINCT dh.id) as so_don,
                   COALESCE(SUM(dh.gia_ban_thuc),0) as tong_dt,
                   COUNT(DISTINCT dv.id) as so_dv
            FROM nhan_vien nv
            LEFT JOIN don_hang dh ON nv.id=dh.nv_id
            LEFT JOIN dich_vu dv ON nv.id=dv.nv_id
            GROUP BY nv.id ORDER BY tong_dt DESC
        """).fetchall()
        conn.close()
        self._nv_data = [dict(r) for r in nv_rows]

        # Clear danh sách NV
        while self.nv_list_lv.count() > 1:
            item = self.nv_list_lv.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        for nv in self._nv_data:
            card = self._make_nv_mini_card(nv)
            self.nv_list_lv.insertWidget(self.nv_list_lv.count()-1, card)

    def _make_nv_mini_card(self, nv):
        w = QWidget()
        active = nv["trang_thai"] == "Đang làm"
        w.setStyleSheet(f"""
            QWidget {{
                background:#f8fafc; border-radius:10px;
                border:1px solid #e5e7eb; border-left:4px solid {'#059669' if active else '#dc2626'};
            }}
            QWidget:hover {{ background:#f1f5f9; border-color:#2563eb; }}
        """)
        lv = QVBoxLayout(w); lv.setContentsMargins(12,10,12,10); lv.setSpacing(3)

        hr = QHBoxLayout()
        name = QLabel(nv["ho_ten"])
        name.setStyleSheet("font-size:14px;font-weight:900;color:#0f172a;background:transparent;")
        dot = QLabel("●")
        dot.setStyleSheet(f"color:{'#059669' if active else '#dc2626'};font-size:12px;background:transparent;")
        hr.addWidget(dot); hr.addWidget(name,1)
        lv.addLayout(hr)

        role = QLabel(f"{nv['chuc_vu']} • {nv['so_don']} đơn • {nv['tong_dt']/1e9:.2f}tỷ")
        role.setStyleSheet("font-size:12px;color:#6b7280;background:transparent;font-weight:600;")
        lv.addWidget(role)

        w.mousePressEvent = lambda e, n=nv: self._select_nv(n)
        w.setCursor(Qt.CursorShape.PointingHandCursor)
        return w

    def _select_nv(self, nv):
        self._sel_nv_id = nv["id"]
        # Clear right panel
        while self.right_lv.count():
            item = self.right_lv.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        # Build detail panel
        detail = self._build_nv_detail(nv)
        self.right_lv.addWidget(detail)

    def _build_nv_detail(self, nv):
        year = self.cmb_period.currentData() or 0
        conn = get_conn()

        # Đơn hàng của NV
        sql_dh = """SELECT dh.ma_don, x.hang_xe||' '||x.dong_xe as ten_xe,
                    kh.ho_ten as ten_kh, dh.gia_ban_thuc,
                    dh.trang_thai, dh.ngay_dat
                    FROM don_hang dh JOIN xe x ON dh.xe_id=x.id
                    JOIN khach_hang kh ON dh.kh_id=kh.id
                    WHERE dh.nv_id=?"""
        if year: sql_dh += f" AND strftime('%Y',dh.ngay_dat)='{year}'"
        dh_rows = [dict(r) for r in conn.execute(sql_dh+" ORDER BY dh.id DESC",(nv["id"],)).fetchall()]

        # Dịch vụ của NV
        sql_dv = """SELECT dv.ma_dv, x.hang_xe||' '||x.dong_xe as ten_xe,
                    kh.ho_ten as ten_kh, dv.loai_dv,
                    dv.chi_phi, dv.trang_thai, dv.ngay_nhan
                    FROM dich_vu dv LEFT JOIN xe x ON dv.xe_id=x.id
                    LEFT JOIN khach_hang kh ON dv.kh_id=kh.id
                    WHERE dv.nv_id=?"""
        dv_rows = [dict(r) for r in conn.execute(sql_dv+" ORDER BY dv.id DESC",(nv["id"],)).fetchall()]

        # Doanh thu theo tháng
        months_dt = []
        for m in range(1,13):
            v = conn.execute("""SELECT COALESCE(SUM(gia_ban_thuc),0)
                FROM don_hang WHERE nv_id=?
                AND trang_thai IN ('Đã thanh toán','Đã giao xe')
                AND strftime('%m',ngay_dat)=?""",
                (nv["id"],f"{m:02d}")).fetchone()[0]
            months_dt.append(v/1e9)
        conn.close()

        tong_dt = sum(r["gia_ban_thuc"] for r in dh_rows)
        so_hoan = sum(1 for r in dh_rows if r["trang_thai"] in ["Đã thanh toán","Đã giao xe"])
        dt_dv   = sum(r["chi_phi"] or 0 for r in dv_rows)

        w = QWidget(); w.setStyleSheet("background:#ffffff;")
        lv = QVBoxLayout(w); lv.setContentsMargins(0,0,0,0); lv.setSpacing(0)

        # Header NV
        hdr = QWidget()
        hdr.setStyleSheet("background:#ffffff;border-bottom:2px solid #e5e7eb;")
        hl = QHBoxLayout(hdr); hl.setContentsMargins(24,18,24,18); hl.setSpacing(16)

        avatar = QLabel(nv["ho_ten"][0].upper() if nv["ho_ten"] else "N")
        avatar.setFixedSize(64,64)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet("""
            background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #2563eb,stop:1 #7c3aed);
            color:white; font-size:28px; font-weight:900;
            border-radius:32px;
        """)

        info = QVBoxLayout(); info.setSpacing(4)
        name_lbl = QLabel(nv["ho_ten"])
        name_lbl.setStyleSheet("font-size:20px;font-weight:900;color:#0f172a;background:transparent;")
        role_lbl = QLabel(f"{nv['chuc_vu']}  •  {nv['ma_nv']}")
        role_lbl.setStyleSheet("font-size:13px;color:#6b7280;background:transparent;font-weight:700;")
        active = nv["trang_thai"]=="Đang làm"
        st_lbl = QLabel(f"● {nv['trang_thai']}")
        st_lbl.setStyleSheet(f"font-size:13px;color:{'#059669' if active else '#dc2626'};font-weight:700;background:transparent;")
        info.addWidget(name_lbl); info.addWidget(role_lbl); info.addWidget(st_lbl)

        hl.addWidget(avatar); hl.addLayout(info,1)

        # Export buttons
        btn_e = QPushButton("📊 Excel NV này"); btn_e.setObjectName("btn_excel")
        btn_e.clicked.connect(lambda: self._export_nv(nv, dh_rows, dv_rows))
        hl.addWidget(btn_e)
        lv.addWidget(hdr)

        # Stat cards
        stat_w = QWidget(); stat_w.setStyleSheet("background:#f9fafb;padding:14px;")
        stat_h = QHBoxLayout(stat_w); stat_h.setSpacing(12)

        for icon,lbl,val,col in [
            ("📋","Tổng đơn hàng",    str(len(dh_rows)),            "#0284c7"),
            ("✅","Đơn hoàn thành",   str(so_hoan),                 "#059669"),
            ("💰","Doanh thu bán xe", f"{tong_dt/1e9:.3f}tỷ",      "#7c3aed"),
            ("🔧","Phiếu dịch vụ",   str(len(dv_rows)),             "#d97706"),
            ("🛠️","DT dịch vụ",       f"{dt_dv/1e6:.1f}tr",        "#0891b2"),
        ]:
            sc = QWidget()
            sc.setStyleSheet(f"background:#ffffff;border-radius:12px;border:1px solid #e5e7eb;border-top:3px solid {col};")
            sl = QVBoxLayout(sc); sl.setContentsMargins(13,11,13,11); sl.setSpacing(3)
            sl.addWidget(QLabel(icon).setParent(None) or self._mini_lbl(icon,"font-size:18px;"))
            sl.addWidget(self._mini_lbl(lbl, "font-size:11px;color:#6b7280;font-weight:700;letter-spacing:0.5px;"))
            vl = QLabel(val); vl.setStyleSheet(f"font-size:17px;font-weight:900;color:{col};background:transparent;")
            sl.addWidget(vl); stat_h.addWidget(sc)
        lv.addWidget(stat_w)

        # Tabs chi tiết
        tabs = QTabWidget()
        tabs.setStyleSheet(STYLE)

        # Tab 1: Biểu đồ + đơn hàng
        tab1 = QWidget(); t1v = QVBoxLayout(tab1); t1v.setContentsMargins(12,12,12,12)

        # Biểu đồ doanh thu theo tháng của NV
        fig = Figure(facecolor="#1e2236", figsize=(8,2.8))
        canvas = FigureCanvasQTAgg(fig)
        ax = fig.add_subplot(111)
        ax.set_facecolor("#1e2236"); fig.set_facecolor("#1e2236")
        x = list(range(1,13))
        cur_m = datetime.now().month
        colors = ["#7c3aed" if i+1==cur_m else "#2c1f6e" for i in range(12)]
        ax.bar(x, months_dt, color=colors, width=0.6, zorder=3)
        ax.plot(x, months_dt, color="#4ade80", linewidth=1.5,
                marker="o", markersize=4, markerfacecolor="#4ade80", zorder=4)
        ax.set_xticks(x); ax.set_xticklabels([f"T{i}" for i in x], color="#64748b", fontsize=8)
        ax.tick_params(colors="#64748b"); ax.spines[:].set_visible(False); ax.yaxis.set_visible(False)
        fig.text(0.5,0.96,f"Doanh thu {datetime.now().year} (tỷ ₫)",
                 ha="center",color="#94a3b8",fontsize=10,fontweight="bold")
        canvas.draw()
        t1v.addWidget(canvas)

        # Bảng đơn hàng
        lh = QLabel("📋  Danh sách đơn hàng")
        lh.setStyleSheet("font-size:13px;font-weight:700;color:#e2e8f0;background:transparent;margin-top:8px;")
        t1v.addWidget(lh)
        tbl_dh = QTableWidget(0,6)
        tbl_dh.setHorizontalHeaderLabels(["MÃ ĐƠN","XE","KHÁCH HÀNG","GIÁ BÁN","TRẠNG THÁI","NGÀY"])
        tbl_dh.setShowGrid(False); tbl_dh.verticalHeader().setVisible(False)
        tbl_dh.setAlternatingRowColors(True)
        tbl_dh.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        tbl_dh.horizontalHeader().setSectionResizeMode(1,QHeaderView.ResizeMode.Stretch)
        STATUS_COL={"Đã giao xe":"#4ade80","Đã thanh toán":"#60a5fa","Chờ xử lý":"#fbbf24","Huỷ":"#f87171"}
        for dh in dh_rows:
            r=tbl_dh.rowCount(); tbl_dh.insertRow(r); tbl_dh.setRowHeight(r,44)
            for c,v in enumerate([dh["ma_don"],dh["ten_xe"],dh["ten_kh"],
                                   f"{dh['gia_ban_thuc']/1e9:.2f} tỷ",
                                   dh["trang_thai"],dh["ngay_dat"]]):
                item=QTableWidgetItem(str(v))
                if c==0: item.setForeground(QColor("#a78bfa")); item.setFont(QFont("Segoe UI",12,QFont.Weight.Bold))
                if c==3: item.setForeground(QColor("#4ade80"))
                if c==4: item.setForeground(QColor(STATUS_COL.get(v,"#94a3b8")))
                tbl_dh.setItem(r,c,item)
        t1v.addWidget(tbl_dh)
        tabs.addTab(tab1,"📋  Đơn hàng")

        # Tab 2: Dịch vụ
        tab2 = QWidget(); t2v = QVBoxLayout(tab2); t2v.setContentsMargins(12,12,12,12)
        tbl_dv = QTableWidget(0,7)
        tbl_dv.setHorizontalHeaderLabels(["MÃ PHIẾU","XE","KHÁCH HÀNG","LOẠI DV","CHI PHÍ","TRẠNG THÁI","NGÀY"])
        tbl_dv.setShowGrid(False); tbl_dv.verticalHeader().setVisible(False)
        tbl_dv.setAlternatingRowColors(True)
        tbl_dv.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        tbl_dv.horizontalHeader().setSectionResizeMode(1,QHeaderView.ResizeMode.Stretch)
        for dv in dv_rows:
            r=tbl_dv.rowCount(); tbl_dv.insertRow(r); tbl_dv.setRowHeight(r,44)
            for c,v in enumerate([dv["ma_dv"],dv["ten_xe"] or "—",dv["ten_kh"] or "—",
                                   dv["loai_dv"],f"{int(dv['chi_phi'] or 0):,} ₫",
                                   dv["trang_thai"],dv["ngay_nhan"]]):
                item=QTableWidgetItem(str(v))
                if c==4: item.setForeground(QColor("#4ade80"))
                tbl_dv.setItem(r,c,item)
        t2v.addWidget(tbl_dv)
        tabs.addTab(tab2,"🔧  Dịch vụ")

        # Tab 3: Tổng kết
        tab3 = QWidget(); t3v = QVBoxLayout(tab3); t3v.setContentsMargins(12,12,12,12); t3v.setSpacing(10)

        # Xếp hạng hiệu suất
        conn2 = get_conn()
        all_nv_dt = conn2.execute("""
            SELECT nv.ho_ten, COALESCE(SUM(dh.gia_ban_thuc),0) as dt
            FROM nhan_vien nv LEFT JOIN don_hang dh ON nv.id=dh.nv_id
            WHERE dh.trang_thai IN ('Đã thanh toán','Đã giao xe') OR dh.id IS NULL
            GROUP BY nv.id ORDER BY dt DESC""").fetchall()
        conn2.close()
        all_dts = [r[1] for r in all_nv_dt]
        max_dt = max(all_dts) if all_dts else 1
        rank = next((i+1 for i,r in enumerate(all_nv_dt) if r[0]==nv["ho_ten"]),0)

        sum_lbl = QLabel("📊  Tổng kết hiệu suất")
        sum_lbl.setStyleSheet("font-size:14px;font-weight:700;color:#e2e8f0;background:transparent;")
        t3v.addWidget(sum_lbl)

        def info_row(k,v,vc="#e2e8f0"):
            rw=QHBoxLayout()
            lk=QLabel(k); lk.setStyleSheet("font-size:12px;color:#4a5568;font-weight:600;background:transparent;min-width:180px;")
            lv2=QLabel(v); lv2.setStyleSheet(f"font-size:13px;color:{vc};font-weight:600;background:transparent;")
            rw.addWidget(lk); rw.addWidget(lv2,1); return rw

        t3v.addLayout(info_row("Xếp hạng doanh thu",f"#{rank} / {len(all_nv_dt)} nhân viên","#f59e0b"))
        t3v.addLayout(info_row("Tổng đơn hàng",str(len(dh_rows)),"#60a5fa"))
        t3v.addLayout(info_row("Đơn hoàn thành",f"{so_hoan} ({so_hoan/len(dh_rows)*100:.0f}%)" if dh_rows else "0","#4ade80"))
        t3v.addLayout(info_row("Tổng doanh thu bán xe",f"{tong_dt/1e9:.3f} tỷ ₫","#a78bfa"))
        t3v.addLayout(info_row("Doanh thu dịch vụ",f"{dt_dv/1e6:.1f} triệu ₫","#2dd4bf"))
        t3v.addLayout(info_row("TB doanh thu/đơn",
            f"{tong_dt/len(dh_rows)/1e6:.0f} triệu ₫" if dh_rows else "—","#f59e0b"))

        # Progress bar so với NV giỏi nhất
        pb_lbl = QLabel("Hiệu suất so với NV tốt nhất:")
        pb_lbl.setStyleSheet("font-size:12px;color:#4a5568;font-weight:600;background:transparent;margin-top:8px;")
        t3v.addWidget(pb_lbl)
        pb = QProgressBar()
        pct = int(tong_dt/max_dt*100) if max_dt > 0 else 0
        pb.setValue(pct)
        pb.setTextVisible(True)
        pb.setFormat(f"{pct}%")
        pb.setStyleSheet("""
            QProgressBar { background:#1e2236; border-radius:8px; height:20px; text-align:center; color:white; font-weight:700; }
            QProgressBar::chunk { background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #6d28d9,stop:1 #4ade80); border-radius:8px; }
        """)
        t3v.addWidget(pb)
        t3v.addStretch()
        tabs.addTab(tab3,"📈  Tổng kết")

        lv.addWidget(tabs, 1)
        return w

    def _mini_lbl(self, text, style=""):
        l = QLabel(text)
        l.setStyleSheet(style + "background:transparent;")
        return l

    def _export(self):
        import openpyxl
        from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
        from openpyxl.utils import get_column_letter
        import datetime

        conn = get_conn()
        rows = conn.execute("""
            SELECT nv.ma_nv, nv.ho_ten, nv.chuc_vu, nv.trang_thai,
                   COUNT(DISTINCT dh.id) as so_don,
                   COALESCE(SUM(CASE WHEN dh.trang_thai IN ('Đã thanh toán','Đã giao xe')
                       THEN dh.gia_ban_thuc ELSE 0 END),0) as dt_hoan,
                   COUNT(DISTINCT dv.id) as so_dv
            FROM nhan_vien nv
            LEFT JOIN don_hang dh ON nv.id=dh.nv_id
            LEFT JOIN dich_vu dv ON nv.id=dv.nv_id
            GROUP BY nv.id ORDER BY dt_hoan DESC""").fetchall()
        conn.close()

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Tong hop NV"

        ws.merge_cells("A1:G1")
        ws["A1"] = "BÁO CÁO TỔNG HỢP NHÂN VIÊN — AUTOVIET"
        ws["A1"].font = Font(name="Segoe UI", size=14, bold=True, color="FFFFFF")
        ws["A1"].fill = PatternFill("solid", fgColor="0F1F35")
        ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[1].height = 36

        ws.merge_cells("A2:G2")
        ws["A2"] = f"Ngày xuất: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}"
        ws["A2"].font = Font(name="Segoe UI", size=10, italic=True, color="64748B")
        ws["A2"].alignment = Alignment(horizontal="right")
        ws.row_dimensions[2].height = 20

        headers = ["MÃ NV", "HỌ TÊN", "CHỨC VỤ", "TRẠNG THÁI", "SỐ ĐƠN", "DOANH THU", "SỐ PHIẾU DV"]
        col_widths = [12, 25, 18, 14, 10, 20, 14]
        thin = Side(style="thin", color="CBD5E1")
        border = Border(left=thin, right=thin, top=thin, bottom=thin)

        for i, (h, w) in enumerate(zip(headers, col_widths), 1):
            cell = ws.cell(row=3, column=i, value=h)
            cell.font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor="1E3A5F")
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = border
            ws.column_dimensions[get_column_letter(i)].width = w
        ws.row_dimensions[3].height = 28

        fill_white = PatternFill("solid", fgColor="FFFFFF")
        fill_alt   = PatternFill("solid", fgColor="F0F4FF")

        for ri, row in enumerate(rows, 4):
            fill = fill_white if ri % 2 == 0 else fill_alt
            ws.row_dimensions[ri].height = 24
            for ci, val in enumerate(row, 1):
                cell = ws.cell(row=ri, column=ci, value=val)
                cell.fill = fill
                cell.border = border
                cell.alignment = Alignment(vertical="center",
                    horizontal="center" if ci in (1, 5, 6, 7) else "left")
                if ci == 1:
                    cell.font = Font(name="Segoe UI", size=11, bold=True, color="2563EB")
                elif ci == 5:
                    cell.font = Font(name="Segoe UI", size=11, bold=True, color="7C3AED")
                elif ci == 6:
                    cell.value = int(val)
                    cell.number_format = '#,##0 "₫"'
                    cell.font = Font(name="Segoe UI", size=11, bold=True, color="059669")
                elif ci == 7:
                    cell.font = Font(name="Segoe UI", size=11, bold=True, color="0891B2")
                elif ci == 4:
                    color = "059669" if str(val) == "Đang làm" else "DC2626"
                    cell.font = Font(name="Segoe UI", size=11, bold=True, color=color)
                else:
                    cell.font = Font(name="Segoe UI", size=11, color="374151")

        ws.freeze_panes = "A4"
        fname = f"BaoCao_NhanVien_{datetime.datetime.now().strftime('%d%m%Y_%H%M')}.xlsx"
        wb.save(fname)
        QMessageBox.information(self, "✅ Xuất thành công!", f"Đã xuất: {fname}")

    def _export_nv(self, nv, dh_rows, dv_rows):
        import openpyxl
        from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
        from openpyxl.utils import get_column_letter
        import datetime

        import re
        ten_safe = re.sub(r'[^\w\-]', '_', nv['ho_ten'])
        fname = f"BC_NV_{nv['ma_nv']}_{ten_safe}.xlsx"
        wb = openpyxl.Workbook()
        thin = Side(style="thin", color="CBD5E1")
        border = Border(left=thin, right=thin, top=thin, bottom=thin)

        # ── Sheet 1: Đơn hàng ────────────────────────────────────────────
        ws1 = wb.active
        ws1.title = "Don hang"

        ws1.merge_cells("A1:F1")
        ws1["A1"] = f"ĐƠN HÀNG — {nv['ho_ten'].upper()}"
        ws1["A1"].font = Font(name="Segoe UI", size=13, bold=True, color="FFFFFF")
        ws1["A1"].fill = PatternFill("solid", fgColor="2563EB")
        ws1["A1"].alignment = Alignment(horizontal="center", vertical="center")
        ws1.row_dimensions[1].height = 32

        dh_headers = ["MÃ ĐƠN", "XE", "KHÁCH HÀNG", "GIÁ BÁN", "TRẠNG THÁI", "NGÀY ĐẶT"]
        dh_widths  = [12, 28, 22, 18, 16, 14]
        for i, (h, w) in enumerate(zip(dh_headers, dh_widths), 1):
            cell = ws1.cell(row=2, column=i, value=h)
            cell.font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor="1E40AF")
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = border
            ws1.column_dimensions[get_column_letter(i)].width = w
        ws1.row_dimensions[2].height = 26

        fill_w = PatternFill("solid", fgColor="FFFFFF")
        fill_a = PatternFill("solid", fgColor="EFF6FF")
        STATUS_DH = {"Đã giao xe":"059669","Đã thanh toán":"2563EB","Chờ xử lý":"D97706","Huỷ":"DC2626"}
        for ri, row in enumerate(dh_rows, 3):
            fill = fill_w if ri % 2 == 0 else fill_a
            ws1.row_dimensions[ri].height = 22
            vals = [
                row.get("ma_don", ""),
                row.get("ten_xe", ""),
                row.get("ten_kh", ""),
                f"{row.get('gia_ban_thuc', 0) / 1e9:.2f} tỷ",
                row.get("trang_thai", ""),
                row.get("ngay_dat", "")
            ]
            for ci, val in enumerate(vals, 1):
                cell = ws1.cell(row=ri, column=ci, value=val)
                cell.fill = fill;
                cell.border = border
                cell.alignment = Alignment(vertical="center",
                                           horizontal="center" if ci in (1, 4, 5, 6) else "left")
                if ci == 1:
                    cell.font = Font(name="Segoe UI", size=11, bold=True, color="2563EB")
                elif ci == 4:
                    cell.font = Font(name="Segoe UI", size=11, bold=True, color="059669")
                elif ci == 5:
                    c = STATUS_DH.get(str(val), "64748B")
                    cell.font = Font(name="Segoe UI", size=11, bold=True, color=c)
                else:
                    cell.font = Font(name="Segoe UI", size=11, color="374151")
        ws1.freeze_panes = "A3"

        # ── Sheet 2: Dịch vụ ─────────────────────────────────────────────
        ws2 = wb.create_sheet("Dich vu")

        ws2.merge_cells("A1:G1")
        ws2["A1"] = f"DỊCH VỤ — {nv['ho_ten'].upper()}"
        ws2["A1"].font = Font(name="Segoe UI", size=13, bold=True, color="FFFFFF")
        ws2["A1"].fill = PatternFill("solid", fgColor="006064")
        ws2["A1"].alignment = Alignment(horizontal="center", vertical="center")
        ws2.row_dimensions[1].height = 32

        dv_headers = ["MÃ PHIẾU", "XE", "KHÁCH HÀNG", "LOẠI DV", "CHI PHÍ", "TRẠNG THÁI", "NGÀY NHẬN"]
        dv_widths  = [12, 25, 22, 20, 14, 16, 14]
        for i, (h, w) in enumerate(zip(dv_headers, dv_widths), 1):
            cell = ws2.cell(row=2, column=i, value=h)
            cell.font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor="00838F")
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = border
            ws2.column_dimensions[get_column_letter(i)].width = w
        ws2.row_dimensions[2].height = 26

        fill_w2 = PatternFill("solid", fgColor="FFFFFF")
        fill_a2 = PatternFill("solid", fgColor="E0F7FA")
        STATUS_DV = {"Hoàn thành":"059669","Đang thực hiện":"2563EB","Tiếp nhận":"D97706","Huỷ":"DC2626"}
        for ri, row in enumerate(dv_rows, 3):
            fill = fill_w2 if ri % 2 == 0 else fill_a2
            ws2.row_dimensions[ri].height = 22
            vals = [
                row.get("ma_dv", ""),
                row.get("ten_xe", "") or "—",
                row.get("ten_kh", "") or "—",
                row.get("loai_dv", ""),
                f"{int(row.get('chi_phi', 0) or 0):,} ₫",
                row.get("trang_thai", ""),
                row.get("ngay_nhan", "") or "—"
            ]
            for ci, val in enumerate(vals, 1):
                cell = ws2.cell(row=ri, column=ci, value=val)
                cell.fill = fill;
                cell.border = border
                cell.alignment = Alignment(vertical="center",
                                           horizontal="center" if ci in (1, 5, 6, 7) else "left")
                if ci == 1:
                    cell.font = Font(name="Segoe UI", size=11, bold=True, color="006064")
                elif ci == 5:
                    cell.font = Font(name="Segoe UI", size=11, bold=True, color="059669")
                elif ci == 6:
                    c = STATUS_DV.get(str(val), "64748B")
                    cell.font = Font(name="Segoe UI", size=11, bold=True, color=c)
                else:
                    cell.font = Font(name="Segoe UI", size=11, color="374151")
        ws2.freeze_panes = "A3"
        wb.save(fname)
        QMessageBox.information(self, "✅ Xuất thành công!", f"Đã xuất: {fname}")

    def refresh(self): self._load()