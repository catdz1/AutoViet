"""
views/dashboard_view.py — Dashboard Admin NÂNG CẤP
+ Giữ nguyên toàn bộ tính năng cũ
+ THÊM: Heatmap doanh thu theo ngày/tuần
+ THÊM: Funnel bán hàng (pipeline)
+ THÊM: Gauge KPI hoàn thành mục tiêu
+ THÊM: Cảnh báo thông minh nâng cao
+ THÊM: Leaderboard top nhân viên
+ Giao diện đẹp hơn — dark/light card
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QFrame, QPushButton, QGridLayout,
    QDateEdit, QComboBox, QTabWidget
)
from PyQt6.QtCore import Qt, QTimer, QDate
from PyQt6.QtGui import QFont
import matplotlib
matplotlib.use("QtAgg")
import matplotlib as mpl
mpl.rcParams["font.family"] = "DejaVu Sans"
mpl.rcParams["axes.unicode_minus"] = False
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.patches as mpatches
import numpy as np
from database import get_conn
from datetime import datetime, timedelta
import calendar

# ── Màu chủ đạo ──────────────────────────────────────────
C_BLUE   = "#2563eb"
C_GREEN  = "#10b981"
C_AMBER  = "#f59e0b"
C_RED    = "#ef4444"
C_PURPLE = "#8b5cf6"
C_TEAL   = "#06b6d4"
C_CARD   = "#ffffff"
C_BG     = "#f1f5f9"
C_TEXT   = "#0f172a"
C_MUTED  = "#64748b"


class DashboardView(QWidget):
    def __init__(self, current_user=None):
        super().__init__()
        self.setObjectName("page_dashboard")
        self.current_user = current_user or {"role": "admin"}
        self._build()
        self.refresh()

    def _build(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("background:#f1f5f9;")
        content = QWidget()
        content.setStyleSheet("background:#f1f5f9;")
        self._scroll_content = content
        self._scroll = scroll
        self._lv = QVBoxLayout(content)
        self._lv.setContentsMargins(20, 16, 20, 24)
        self._lv.setSpacing(16)
        scroll.setWidget(content)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(scroll)

        # ── TITLE BAR ──────────────────────────────────────
        title_row = QHBoxLayout()
        ico = QLabel("📊")
        ico.setStyleSheet("font-size:24px;background:transparent;")
        ttl = QLabel("Dashboard — Tổng quan hệ thống")
        ttl.setStyleSheet(
            "font-size:20px;font-weight:800;color:#0f172a;background:transparent;"
            "border-left:4px solid #2563eb;padding-left:12px;"
        )
        self.lbl_time = QLabel()
        self.lbl_time.setStyleSheet("color:#64748b;font-size:12px;background:transparent;")
        title_row.addWidget(ico)
        title_row.addWidget(ttl)
        title_row.addStretch()
        title_row.addWidget(self.lbl_time)
        self._lv.addLayout(title_row)

        # ── CẢNH BÁO THÔNG MINH ────────────────────────────
        self.alert_widget = QWidget()
        self.alert_lv = QVBoxLayout(self.alert_widget)
        self.alert_lv.setContentsMargins(0, 0, 0, 0)
        self.alert_lv.setSpacing(4)
        self.alert_widget.hide()
        self._lv.addWidget(self.alert_widget)

        # ── BỘ LỌC ─────────────────────────────────────────
        filter_row = QHBoxLayout()
        lbl_filter = QLabel("📅  Xem doanh thu theo:")
        lbl_filter.setStyleSheet("color:#8b5cf6;font-size:13px;font-weight:700;background:transparent;")
        self.cmb_filter = QComboBox()
        self.cmb_filter.setStyleSheet("""
            QComboBox{background:#ffffff;color:#1e293b;border:1.5px solid #e2e8f0;
                border-radius:8px;padding:6px 12px;font-size:13px;min-width:120px;}
            QComboBox::drop-down{border:none;}
            QComboBox QAbstractItemView{background:#ffffff;color:#1e293b;
                border:1px solid #e2e8f0;selection-background-color:#ede9fe;}
        """)
        self.cmb_filter.addItems(["Theo tháng", "Theo ngày", "Theo năm"])
        self.cmb_filter.currentTextChanged.connect(self.refresh)
        self.date_picker = QDateEdit()
        self.date_picker.setDate(QDate.currentDate())
        self.date_picker.setCalendarPopup(True)
        self.date_picker.setDisplayFormat("dd/MM/yyyy")
        self.date_picker.setStyleSheet("""
            QDateEdit{background:#ffffff;color:#1e293b;border:1.5px solid #e2e8f0;
                border-radius:8px;padding:6px 12px;font-size:13px;}
            QDateEdit::drop-down{border:none;}
        """)
        self.date_picker.dateChanged.connect(self.refresh)
        self.lbl_refresh = QLabel()
        self.lbl_refresh.setStyleSheet("color:#94a3b8;font-size:11px;background:transparent;")
        filter_row.addWidget(lbl_filter)
        filter_row.addWidget(self.cmb_filter)
        filter_row.addWidget(self.date_picker)
        filter_row.addStretch()
        filter_row.addWidget(self.lbl_refresh)
        self._lv.addLayout(filter_row)

        # ── 6 KPI CARDS ────────────────────────────────────
        self.card_grid = QGridLayout()
        self.card_grid.setSpacing(10)
        self.cards = {}
        card_defs = [
            ("tong_xe",    "🚗", "TỔNG XE",    "0", C_PURPLE),
            ("con_hang",   "📦", "CÒN HÀNG",   "0", C_GREEN),
            ("da_ban",     "💰", "ĐÃ BÁN",     "0", C_AMBER),
            ("khach_hang", "👥", "KHÁCH HÀNG", "0", C_BLUE),
            ("don_hang",   "📋", "ĐƠN HÀNG",  "0", C_RED),
            ("dich_vu",    "🔧", "DỊCH VỤ",   "0", C_TEAL),
        ]
        for i, (key, icon, label, val, color) in enumerate(card_defs):
            card = self._make_kpi_card(icon, label, val, color)
            self.cards[key] = card
            self.card_grid.addWidget(card, 0, i)
        self._lv.addLayout(self.card_grid)

        # ── 4 DOANH THU STATS ──────────────────────────────
        dt_row = QHBoxLayout()
        dt_row.setSpacing(10)
        self.card_dt_ngay  = self._make_stat("📆 Doanh thu hôm nay", "0 ₫", C_BLUE)
        self.card_dt_thang = self._make_stat("💰 Tháng này",         "0 ₫", C_GREEN)
        self.card_dt_nam   = self._make_stat("📅 Doanh thu năm nay", "0 ₫", C_PURPLE)
        self.card_dt_tb    = self._make_stat("📊 TB mỗi đơn",        "0 ₫", C_AMBER)
        for c in [self.card_dt_ngay, self.card_dt_thang, self.card_dt_nam, self.card_dt_tb]:
            dt_row.addWidget(c, 1)
        self._lv.addLayout(dt_row)

        # ── TAB BIỂU ĐỒ ────────────────────────────────────
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane{border:none;background:#f1f5f9;}
            QTabBar::tab{background:#e2e8f0;color:#64748b;padding:8px 18px;
                border-radius:8px 8px 0 0;font-size:12px;font-weight:600;margin-right:3px;}
            QTabBar::tab:selected{background:#ffffff;color:#2563eb;border-bottom:3px solid #2563eb;}
            QTabBar::tab:hover{background:#f8fafc;color:#1e293b;}
        """)
        tabs.setMinimumHeight(420)

        # Tab 1 — Doanh thu + Tỷ lệ xe
        tab1 = QWidget(); tab1.setStyleSheet("background:#f1f5f9;")
        t1l = QHBoxLayout(tab1); t1l.setSpacing(12); t1l.setContentsMargins(0, 8, 0, 0)
        self.fig_dt = Figure(facecolor="#ffffff", figsize=(7, 4.5))
        self.canvas_dt = FigureCanvasQTAgg(self.fig_dt)
        self.canvas_dt.setStyleSheet("border-radius:12px;border:1px solid #e2e8f0;")
        self.canvas_dt.setMinimumHeight(340)
        self.fig_pie = Figure(facecolor="#ffffff", figsize=(4, 4.5))
        self.canvas_pie = FigureCanvasQTAgg(self.fig_pie)
        self.canvas_pie.setStyleSheet("border-radius:12px;border:1px solid #e2e8f0;")
        self.canvas_pie.setMinimumHeight(340)
        t1l.addWidget(self.canvas_dt, 3)
        t1l.addWidget(self.canvas_pie, 2)
        tabs.addTab(tab1, "📈 Doanh thu")

        # Tab 2 — Heatmap doanh thu
        tab2 = QWidget(); tab2.setStyleSheet("background:#f1f5f9;")
        t2l = QVBoxLayout(tab2); t2l.setContentsMargins(0, 8, 0, 0)
        self.fig_heat = Figure(facecolor="#ffffff", figsize=(10, 3.5))
        self.canvas_heat = FigureCanvasQTAgg(self.fig_heat)
        self.canvas_heat.setStyleSheet("border-radius:12px;border:1px solid #e2e8f0;")
        self.canvas_heat.setMinimumHeight(300)
        t2l.addWidget(self.canvas_heat)
        tabs.addTab(tab2, "🌡 Heatmap")

        # Tab 3 — Funnel + Gauge
        tab3 = QWidget(); tab3.setStyleSheet("background:#f1f5f9;")
        t3l = QHBoxLayout(tab3); t3l.setSpacing(12); t3l.setContentsMargins(0, 8, 0, 0)
        self.fig_funnel = Figure(facecolor="#ffffff", figsize=(5, 3.5))
        self.canvas_funnel = FigureCanvasQTAgg(self.fig_funnel)
        self.canvas_funnel.setStyleSheet("border-radius:12px;border:1px solid #e2e8f0;")
        self.canvas_funnel.setMinimumHeight(300)
        self.fig_gauge = Figure(facecolor="#ffffff", figsize=(5, 3.5))
        self.canvas_gauge = FigureCanvasQTAgg(self.fig_gauge)
        self.canvas_gauge.setStyleSheet("border-radius:12px;border:1px solid #e2e8f0;")
        self.canvas_gauge.setMinimumHeight(300)
        t3l.addWidget(self.canvas_funnel, 1)
        t3l.addWidget(self.canvas_gauge, 1)
        tabs.addTab(tab3, "🎯 Funnel & KPI")

        # Tab 4 — Leaderboard NV
        tab4 = QWidget(); tab4.setStyleSheet("background:#f1f5f9;")
        t4l = QVBoxLayout(tab4); t4l.setContentsMargins(0, 8, 0, 0)
        self.fig_lead = Figure(facecolor="#ffffff", figsize=(10, 3.5))
        self.canvas_lead = FigureCanvasQTAgg(self.fig_lead)
        self.canvas_lead.setStyleSheet("border-radius:12px;border:1px solid #e2e8f0;")
        self.canvas_lead.setMinimumHeight(300)
        t4l.addWidget(self.canvas_lead)
        tabs.addTab(tab4, "🏆 Leaderboard NV")

        self._lv.addWidget(tabs, 1)

        # ── ĐƠN HÀNG GẦN ĐÂY ──────────────────────────────
        sep = QWidget(); sep.setFixedHeight(1)
        sep.setStyleSheet("background:#e2e8f0;")
        self._lv.addWidget(sep)
        lh = QLabel("🛒  Đơn hàng gần đây")
        lh.setStyleSheet("font-size:15px;font-weight:800;color:#1e293b;background:transparent;padding-top:8px;")
        self._lv.addWidget(lh)
        self.recent_widget = QWidget()
        self.recent_lv = QVBoxLayout(self.recent_widget)
        self.recent_lv.setContentsMargins(0, 0, 0, 0)
        self.recent_lv.setSpacing(5)
        self._lv.addWidget(self.recent_widget)

        # ── TIMERS ─────────────────────────────────────────
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(1000)
        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self._auto_refresh)
        self._refresh_timer.start(30000)

    # ── WIDGET HELPERS ─────────────────────────────────────
    def _make_kpi_card(self, icon, label, val, color):
        outer = QWidget()
        outer.setStyleSheet(f"background:{color};border-radius:12px;")
        outer_lv = QVBoxLayout(outer)
        outer_lv.setContentsMargins(0, 4, 0, 0)
        outer_lv.setSpacing(0)
        w = QWidget()
        w.setStyleSheet("background:#ffffff;border-radius:10px;")
        lv = QVBoxLayout(w); lv.setContentsMargins(14, 12, 14, 12); lv.setSpacing(2)
        li = QLabel(icon); li.setStyleSheet("font-size:22px;background:transparent;")
        ll = QLabel(label)
        ll.setStyleSheet(f"font-size:10px;color:{color};font-weight:800;letter-spacing:1.2px;background:transparent;")
        lv2 = QLabel(val)
        lv2.setStyleSheet(f"font-size:24px;font-weight:800;color:{color};background:transparent;")
        lv.addWidget(li); lv.addWidget(ll); lv.addWidget(lv2)
        outer_lv.addWidget(w)
        outer._val = lv2
        return outer

    def _make_stat(self, label, val, color):
        outer = QWidget()
        outer.setStyleSheet(
            f"background:{color};border-radius:10px;"
        )
        outer_lv = QHBoxLayout(outer)
        outer_lv.setContentsMargins(4, 0, 0, 0)
        outer_lv.setSpacing(0)
        w = QWidget()
        w.setStyleSheet("background:#ffffff;border-radius:8px;")
        lv = QVBoxLayout(w); lv.setContentsMargins(12, 10, 12, 10); lv.setSpacing(2)
        ll = QLabel(label)
        ll.setStyleSheet(f"font-size:12px;color:{C_MUTED};font-weight:600;background:transparent;")
        lv2 = QLabel(val)
        lv2.setStyleSheet(f"font-size:18px;font-weight:800;color:{color};background:transparent;")
        lv.addWidget(ll); lv.addWidget(lv2)
        outer_lv.addWidget(w)
        outer._lbl = ll; outer._val = lv2
        return outer

    def _auto_refresh(self):
        try:
            self.refresh()
            self.lbl_refresh.setText(f"🔄 Cập nhật lúc {datetime.now().strftime('%H:%M:%S')}")
        except RuntimeError:
            # Widget/canvas đã bị huỷ (ví dụ do đăng xuất) trong lúc timer vẫn còn kích hoạt
            # -> bỏ qua an toàn, không để crash cả ứng dụng
            try: self._refresh_timer.stop()
            except Exception: pass

    # ── REFRESH CHÍNH ──────────────────────────────────────
    def refresh(self):
        conn = get_conn()

        t  = conn.execute("SELECT COUNT(*) FROM xe").fetchone()[0]
        c  = conn.execute("SELECT COUNT(*) FROM xe WHERE trang_thai='Còn hàng'").fetchone()[0]
        b  = conn.execute("SELECT COUNT(*) FROM xe WHERE trang_thai='Đã bán'").fetchone()[0]
        kh = conn.execute("SELECT COUNT(*) FROM khach_hang").fetchone()[0]
        dh = conn.execute("SELECT COUNT(*) FROM don_hang").fetchone()[0]
        dv = conn.execute("SELECT COUNT(*) FROM dich_vu").fetchone()[0]
        bd = conn.execute("SELECT COUNT(*) FROM xe WHERE trang_thai='Bảo dưỡng'").fetchone()[0]
        dc = conn.execute("SELECT COUNT(*) FROM xe WHERE trang_thai='Đặt cọc'").fetchone()[0]

        self.cards["tong_xe"]._val.setText(str(t))
        self.cards["con_hang"]._val.setText(str(c))
        self.cards["da_ban"]._val.setText(str(b))
        self.cards["khach_hang"]._val.setText(str(kh))
        self.cards["don_hang"]._val.setText(str(dh))
        self.cards["dich_vu"]._val.setText(str(dv))

        # ── Cảnh báo thông minh ────────────────────────────
        self._update_alerts(conn, c, bd)

        now = datetime.now()
        cur_y = now.year; cur_m = now.month; cur_d = now.day
        filter_type = self.cmb_filter.currentText() if hasattr(self, 'cmb_filter') else "Theo tháng"
        sel_date = self.date_picker.date() if hasattr(self, 'date_picker') else None
        sel_y = sel_date.year()  if sel_date else cur_y
        sel_m = sel_date.month() if sel_date else cur_m
        sel_d = sel_date.day()   if sel_date else cur_d

        # Doanh thu hôm nay
        dt_ngay = conn.execute("""
            SELECT COALESCE(SUM(gia_ban_thuc - COALESCE(chiet_khau,0)),0)
            FROM don_hang
            WHERE strftime('%Y-%m-%d', datetime(created_at,'+7 hours'))=?""",
            (f"{cur_y}-{cur_m:02d}-{cur_d:02d}",)).fetchone()[0]
        self.card_dt_ngay._val.setText(f"{dt_ngay/1e9:.3f} tỷ ₫")

        if filter_type == "Theo ngày":
            dt_f = conn.execute("""SELECT COALESCE(SUM(gia_ban_thuc-COALESCE(chiet_khau,0)),0)
                FROM don_hang WHERE strftime('%Y-%m-%d',ngay_dat)=?""",
                (f"{sel_y}-{sel_m:02d}-{sel_d:02d}",)).fetchone()[0]
            self.card_dt_thang._lbl.setText(f"💰 Ngày {sel_d}/{sel_m}/{sel_y}")
            chart_y, chart_m = sel_y, sel_m
        elif filter_type == "Theo năm":
            dt_f = conn.execute("""SELECT COALESCE(SUM(gia_ban_thuc-COALESCE(chiet_khau,0)),0)
                FROM don_hang WHERE strftime('%Y',ngay_dat)=?""", (str(sel_y),)).fetchone()[0]
            self.card_dt_thang._lbl.setText(f"💰 Năm {sel_y}")
            chart_y, chart_m = sel_y, cur_m
        else:
            dt_f = conn.execute("""SELECT COALESCE(SUM(gia_ban_thuc-COALESCE(chiet_khau,0)),0)
                FROM don_hang WHERE strftime('%Y-%m',ngay_dat)=?""",
                (f"{sel_y}-{sel_m:02d}",)).fetchone()[0]
            self.card_dt_thang._lbl.setText(f"💰 Tháng {sel_m}/{sel_y}")
            chart_y, chart_m = sel_y, sel_m
        self.card_dt_thang._val.setText(f"{dt_f/1e9:.3f} tỷ ₫")

        dt_nam = conn.execute("""SELECT COALESCE(SUM(gia_ban_thuc-COALESCE(chiet_khau,0)),0)
            FROM don_hang WHERE strftime('%Y',ngay_dat)=?""", (str(sel_y),)).fetchone()[0]
        self.card_dt_nam._val.setText(f"{dt_nam/1e9:.3f} tỷ ₫")
        so_don = conn.execute("SELECT COUNT(*) FROM don_hang").fetchone()[0]
        dt_tb = dt_nam / so_don if so_don > 0 else 0
        self.card_dt_tb._val.setText(f"{dt_tb/1e6:.0f} triệu ₫")

        # ── Vẽ các biểu đồ ────────────────────────────────
        self._draw_revenue(conn, filter_type, sel_y, sel_m, sel_d, cur_m, cur_d)
        self._draw_pie(conn, c, b, bd, dc, t)
        self._draw_heatmap(conn, sel_y, sel_m)
        self._draw_funnel(conn)
        self._draw_gauge(dt_nam, cur_y)
        self._draw_leaderboard(conn, sel_y)
        self._draw_recent(conn)
        conn.close()

        # Ép tính lại kích thước nội dung — đảm bảo thanh cuộn luôn phủ hết nội dung thực tế
        self._scroll_content.adjustSize()
        self._scroll_content.updateGeometry()

    # ── CẢnh báo thông minh ────────────────────────────────
    def _update_alerts(self, conn, con_hang, bao_duong):
        while self.alert_lv.count():
            item = self.alert_lv.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        alerts = []
        if con_hang < 3:
            alerts.append(("⚠️", f"Tồn kho thấp! Chỉ còn {con_hang} xe — cần nhập thêm hàng gấp.", C_RED, "rgba(239,68,68,.08)", "rgba(239,68,68,.25)"))
        if bao_duong > 0:
            alerts.append(("🔧", f"Có {bao_duong} xe đang bảo dưỡng — kiểm tra tiến độ.", C_AMBER, "rgba(245,158,11,.08)", "rgba(245,158,11,.25)"))

        # KH sinh nhật hôm nay
        today = datetime.now().strftime("%m-%d")
        bd_kh = conn.execute("""
            SELECT COUNT(*) FROM khach_hang
            WHERE strftime('%m-%d', ngay_sinh) = ?""", (today,)).fetchone()[0]
        if bd_kh > 0:
            alerts.append(("🎂", f"{bd_kh} khách hàng có sinh nhật hôm nay — nhớ gửi lời chúc!", C_PURPLE, "rgba(139,92,246,.08)", "rgba(139,92,246,.25)"))

        # Đơn chờ xử lý
        cho_xu_ly = conn.execute("""
            SELECT COUNT(*) FROM don_hang WHERE trang_thai='Chờ xử lý'""").fetchone()[0]
        if cho_xu_ly > 0:
            alerts.append(("📋", f"Có {cho_xu_ly} đơn hàng đang chờ xử lý.", C_BLUE, "rgba(37,99,235,.08)", "rgba(37,99,235,.25)"))

        if not alerts:
            self.alert_widget.hide()
            return

        for icon, msg, color, bg, border_c in alerts:
            row = QWidget()
            row.setStyleSheet(f"background:{bg};border:1px solid {border_c};border-radius:8px;padding-left:4px;")
            rl = QHBoxLayout(row); rl.setContentsMargins(12, 8, 12, 8)
            li = QLabel(icon); li.setStyleSheet("font-size:16px;background:transparent;")
            lm = QLabel(msg); lm.setStyleSheet(f"color:{color};font-size:13px;font-weight:600;background:transparent;")
            rl.addWidget(li); rl.addWidget(lm); rl.addStretch()
            self.alert_lv.addWidget(row)
        self.alert_widget.show()

    # ── BIỂU ĐỒ DOANH THU ─────────────────────────────────
    def _draw_revenue(self, conn, filter_type, sel_y, sel_m, sel_d, cur_m, cur_d):
        if filter_type == "Theo ngày":
            y_data = []
            for h in range(24):
                v = conn.execute("""SELECT COALESCE(SUM(gia_ban_thuc-COALESCE(chiet_khau,0)),0)
                    FROM don_hang
                    WHERE strftime('%Y-%m-%d',datetime(created_at,'+7 hours'))=?
                    AND CAST(strftime('%H',datetime(created_at,'+7 hours')) AS INTEGER)=?""",
                    (f"{sel_y}-{sel_m:02d}-{sel_d:02d}", h)).fetchone()[0]
                y_data.append(v/1e9)
            x_data = list(range(24))
            x_lbls = [f"{h}h" for h in range(24)]
            cur_x  = datetime.now().hour
            title  = f"Doanh thu ngày {sel_d}/{sel_m}/{sel_y} (tỷ ₫)"
        elif filter_type == "Theo năm":
            y_data = []
            for m in range(1, 13):
                v = conn.execute("""SELECT COALESCE(SUM(gia_ban_thuc-COALESCE(chiet_khau,0)),0)
                    FROM don_hang WHERE strftime('%Y-%m',ngay_dat)=?""",
                    (f"{sel_y}-{m:02d}",)).fetchone()[0]
                y_data.append(v/1e9)
            x_data = list(range(1, 13))
            x_lbls = [f"T{m}" for m in range(1, 13)]
            cur_x  = cur_m
            title  = f"Doanh thu năm {sel_y} (tỷ ₫)"
        else:
            days_in = calendar.monthrange(sel_y, sel_m)[1]
            y_data  = []
            for d in range(1, days_in+1):
                v = conn.execute("""SELECT COALESCE(SUM(gia_ban_thuc-COALESCE(chiet_khau,0)),0)
                    FROM don_hang WHERE strftime('%Y-%m-%d',ngay_dat)=?""",
                    (f"{sel_y}-{sel_m:02d}-{d:02d}",)).fetchone()[0]
                y_data.append(v/1e9)
            x_data = list(range(1, days_in+1))
            x_lbls = [str(d) for d in x_data]
            cur_x  = cur_d if sel_m == datetime.now().month else 1
            title  = f"Doanh thu tháng {sel_m}/{sel_y} (tỷ ₫)"

        self.fig_dt.clear()
        ax = self.fig_dt.add_subplot(111)
        ax.set_facecolor("#f8fafc"); self.fig_dt.set_facecolor("#ffffff")
        max_v = max(y_data) if max(y_data) > 0 else 1
        colors = [C_BLUE if x == cur_x else "#bfdbfe" for x in x_data]
        ax.bar(x_data, y_data, color=colors, width=0.65, zorder=3, alpha=0.9)
        ax.plot(x_data, y_data, color="#1d4ed8", linewidth=2.5,
                marker="o", markersize=5, markerfacecolor="#fff",
                markeredgecolor=C_BLUE, markeredgewidth=2, zorder=4)
        ax.fill_between(x_data, y_data, alpha=0.07, color=C_BLUE)
        for i, v in enumerate(y_data):
            if v > max_v * 0.05:
                ax.text(x_data[i], v + max_v*0.03, f"{v:.1f}",
                        ha="center", color="#334155", fontsize=7, fontweight="600")
        if filter_type == "Theo tháng":
            ticks = [x for x in x_data if x % 5 == 0 or x == 1]
            ax.set_xticks(ticks); ax.set_xticklabels([str(x) for x in ticks], color="#475569", fontsize=8)
        else:
            ax.set_xticks(x_data); ax.set_xticklabels(x_lbls, color="#475569", fontsize=8)
        ax.spines[:].set_visible(False); ax.yaxis.set_visible(False)
        ax.set_ylim(0, max_v * 1.5); ax.grid(axis='y', linestyle='--', alpha=0.3, color="#cbd5e1")
        ax.tick_params(colors="#64748b")
        self.fig_dt.text(0.5, 0.95, title, ha="center", color="#1e293b", fontsize=11, fontweight="bold")
        self.fig_dt.subplots_adjust(top=0.90, bottom=0.10, left=0.01, right=0.99)
        self.canvas_dt.draw()

    # ── BIỂU ĐỒ PIE ───────────────────────────────────────
    def _draw_pie(self, conn, c, b, bd, dc, t):
        self.fig_pie.clear()
        ax = self.fig_pie.add_subplot(111)
        ax.set_facecolor("#ffffff"); self.fig_pie.set_facecolor("#ffffff")
        data_map = [
            (c,  "Còn hàng",  C_GREEN),
            (b,  "Đã bán",    C_RED),
            (bd, "Bảo dưỡng", C_PURPLE),
            (dc, "Đặt cọc",   C_AMBER),
        ]
        filtered = [(v, l, c2) for v, l, c2 in data_map if v > 0]
        if filtered:
            vals, lbls, clrs = zip(*filtered)
            wedges, _, auto = ax.pie(
                vals, labels=None, colors=clrs,
                autopct=lambda p: f"{p:.0f}%" if p > 5 else "",
                startangle=90, pctdistance=0.75,
                wedgeprops={"width": 0.55, "edgecolor": "#fff", "linewidth": 2})
            for at in auto: at.set_color("#fff"); at.set_fontsize(9); at.set_fontweight("bold")
            ax.legend(lbls, loc="lower center", ncol=2, fontsize=8,
                      facecolor="#ffffff", edgecolor="#e2e8f0", labelcolor="#334155", framealpha=0.95)
        self.fig_pie.text(0.5, 0.95, "Tỷ lệ trạng thái xe", ha="center",
                          color="#334155", fontsize=10, fontweight="bold")
        self.fig_pie.subplots_adjust(top=0.90, bottom=0.10)
        self.canvas_pie.draw()

    # ── HEATMAP DOANH THU ──────────────────────────────────
    def _draw_heatmap(self, conn, sel_y, sel_m):
        self.fig_heat.clear()
        ax = self.fig_heat.add_subplot(111)
        ax.set_facecolor("#f8fafc"); self.fig_heat.set_facecolor("#ffffff")

        days_in = calendar.monthrange(sel_y, sel_m)[1]
        # Tạo ma trận tuần × ngày trong tuần
        first_wd = calendar.monthrange(sel_y, sel_m)[0]  # 0=Mon
        weeks = []
        week = [0] * 7
        for d in range(1, days_in + 1):
            v = conn.execute("""SELECT COALESCE(SUM(gia_ban_thuc-COALESCE(chiet_khau,0)),0)
                FROM don_hang WHERE strftime('%Y-%m-%d',ngay_dat)=?""",
                (f"{sel_y}-{sel_m:02d}-{d:02d}",)).fetchone()[0]
            wd = (first_wd + d - 1) % 7
            week[wd] = v / 1e9
            if wd == 6 or d == days_in:
                weeks.append(week[:])
                week = [0] * 7

        if not weeks:
            return

        data = np.array(weeks)
        im = ax.imshow(data, aspect='auto', cmap='Blues', interpolation='nearest')
        ax.set_xticks(range(7))
        ax.set_xticklabels(["T2","T3","T4","T5","T6","T7","CN"], color="#475569", fontsize=9)
        ax.set_yticks(range(len(weeks)))
        ax.set_yticklabels([f"Tuần {i+1}" for i in range(len(weeks))], color="#475569", fontsize=9)

        for i in range(len(weeks)):
            for j in range(7):
                val = data[i, j]
                if val > 0:
                    ax.text(j, i, f"{val:.1f}", ha="center", va="center",
                            color="#fff" if val > data.max()*0.5 else "#1e3a5f",
                            fontsize=8, fontweight="bold")

        self.fig_heat.colorbar(im, ax=ax, label="Tỷ đồng", shrink=0.8)
        ax.spines[:].set_visible(False)
        self.fig_heat.text(0.5, 0.97, f"Heatmap doanh thu tháng {sel_m}/{sel_y}",
                           ha="center", color="#1e293b", fontsize=11, fontweight="bold")
        self.fig_heat.subplots_adjust(top=0.90, bottom=0.08, left=0.1, right=0.92)
        self.canvas_heat.draw()

    # ── FUNNEL BÁN HÀNG ───────────────────────────────────
    def _draw_funnel(self, conn):
        self.fig_funnel.clear()
        ax = self.fig_funnel.add_subplot(111)
        ax.set_facecolor("#ffffff"); self.fig_funnel.set_facecolor("#ffffff")

        tong_kh  = conn.execute("SELECT COUNT(*) FROM khach_hang").fetchone()[0]
        co_don   = conn.execute("SELECT COUNT(DISTINCT kh_id) FROM don_hang").fetchone()[0]
        dat_coc  = conn.execute("SELECT COUNT(*) FROM don_hang WHERE trang_thai='Đặt cọc'").fetchone()[0]
        da_giao  = conn.execute("""SELECT COUNT(*) FROM don_hang
                                   WHERE trang_thai IN ('Đã giao xe','Đã thanh toán')""").fetchone()[0]

        stages  = ["Khách hàng", "Có đơn hàng", "Đặt cọc", "Đã giao xe"]
        values  = [tong_kh, co_don, dat_coc + co_don, da_giao]
        colors2 = [C_BLUE, C_TEAL, C_AMBER, C_GREEN]

        max_v = max(values) if max(values) > 0 else 1
        for i, (s, v, col) in enumerate(zip(stages, values, colors2)):
            w = v / max_v
            left = (1 - w) / 2
            bar = mpatches.FancyBboxPatch(
                (left, len(stages)-i-1.0+0.05), w, 0.8,
                boxstyle="round,pad=0.02", facecolor=col, alpha=0.85, edgecolor="#fff", linewidth=1.5)
            ax.add_patch(bar)
            ax.text(0.5, len(stages)-i-0.55, f"{s}: {v}", ha="center", va="center",
                    color="#fff", fontsize=10, fontweight="bold")

        ax.set_xlim(0, 1); ax.set_ylim(0, len(stages))
        ax.axis("off")
        self.fig_funnel.text(0.5, 0.97, "Funnel bán hàng",
                             ha="center", color="#1e293b", fontsize=11, fontweight="bold")
        self.fig_funnel.subplots_adjust(top=0.88, bottom=0.04, left=0.02, right=0.98)
        self.canvas_funnel.draw()

    # ── GAUGE KPI ─────────────────────────────────────────
    def _draw_gauge(self, dt_nam, cur_y):
        self.fig_gauge.clear()
        ax = self.fig_gauge.add_subplot(111)
        ax.set_facecolor("#ffffff"); self.fig_gauge.set_facecolor("#ffffff")
        ax.set_aspect('equal'); ax.axis('off')

        goal = 500e9  # Mục tiêu 500 tỷ/năm
        pct  = min(dt_nam / goal, 1.0)

        # Nền cung tròn
        theta = np.linspace(np.pi, 0, 100)
        ax.fill_between(np.cos(theta), np.sin(theta)*0, np.sin(theta),
                        alpha=0.08, color=C_BLUE)
        ax.plot(np.cos(theta), np.sin(theta), color="#e2e8f0", linewidth=12, solid_capstyle='round')

        # Cung tiến độ
        theta2 = np.linspace(np.pi, np.pi - pct * np.pi, 100)
        col = C_GREEN if pct >= 0.8 else (C_AMBER if pct >= 0.5 else C_RED)
        ax.plot(np.cos(theta2), np.sin(theta2), color=col, linewidth=12, solid_capstyle='round')

        # Kim đồng hồ
        angle = np.pi - pct * np.pi
        ax.annotate("", xy=(0.55*np.cos(angle), 0.55*np.sin(angle)), xytext=(0, 0),
                    arrowprops=dict(arrowstyle="->", color=col, lw=2.5))
        ax.add_patch(plt_circle := mpatches.Circle((0, 0), 0.06, color=col, zorder=5))
        ax.add_patch(plt_circle)

        ax.text(0, -0.22, f"{pct*100:.1f}%", ha="center", va="center",
                fontsize=20, fontweight="bold", color=col)
        ax.text(0, -0.42, f"{dt_nam/1e9:.1f} / {goal/1e9:.0f} tỷ ₫",
                ha="center", va="center", fontsize=9, color="#64748b")
        ax.text(-0.95, -0.12, "0%", ha="center", fontsize=8, color="#94a3b8")
        ax.text(0.95,  -0.12, "100%", ha="center", fontsize=8, color="#94a3b8")

        ax.set_xlim(-1.1, 1.1); ax.set_ylim(-0.6, 1.1)
        self.fig_gauge.text(0.5, 0.97, f"KPI doanh thu năm {cur_y}",
                            ha="center", color="#1e293b", fontsize=11, fontweight="bold")
        self.fig_gauge.subplots_adjust(top=0.88, bottom=0.04)
        self.canvas_gauge.draw()

    # ── LEADERBOARD NHÂN VIÊN ─────────────────────────────
    def _draw_leaderboard(self, conn, sel_y):
        self.fig_lead.clear()
        ax = self.fig_lead.add_subplot(111)
        ax.set_facecolor("#ffffff"); self.fig_lead.set_facecolor("#ffffff")

        rows = conn.execute("""
            SELECT nv.ho_ten, COALESCE(SUM(dh.gia_ban_thuc),0) as dt, COUNT(dh.id) as so_don
            FROM nhan_vien nv
            LEFT JOIN don_hang dh ON dh.nv_id=nv.id
                AND strftime('%Y',dh.ngay_dat)=?
            GROUP BY nv.id ORDER BY dt DESC LIMIT 8
        """, (str(sel_y),)).fetchall()

        if not rows:
            ax.text(0.5, 0.5, "Chua co du lieu", ha="center", va="center",
                    transform=ax.transAxes, color="#94a3b8", fontsize=13)
            self.canvas_lead.draw(); return

        # Sắp xếp: top1 ở trên cùng → reverse để barh hiện đúng
        names_raw = [r[0][:14] for r in rows]
        vals_raw  = [r[1]/1e9  for r in rows]
        n         = len(rows)

        # Dùng ytick label thay vì ax.text để tên hiện đúng chỗ
        names_rev = names_raw[::-1]   # top1 ở index cao nhất
        vals_rev  = vals_raw[::-1]
        rank_rev  = list(range(n-1, -1, -1))  # rank thực

        max_v = max(vals_raw) if max(vals_raw) > 0 else 1

        medal_col = [C_AMBER, C_BLUE, C_TEAL]
        bar_colors = []
        for rank in rank_rev:
            if rank == 0:   bar_colors.append(C_AMBER)
            elif rank == 1: bar_colors.append(C_BLUE)
            elif rank == 2: bar_colors.append(C_TEAL)
            else:           bar_colors.append("#bfdbfe")

        y_pos = list(range(n))

        # Nền xen kẽ
        for i in range(n):
            ax.barh(i, max_v * 1.5, height=0.72,
                    color="#f8fafc" if i % 2 == 0 else "#ffffff",
                    zorder=0, left=0)

        # Bar chính
        bars = ax.barh(y_pos, vals_rev, color=bar_colors,
                       height=0.55, zorder=3,
                       edgecolor="#ffffff", linewidth=1)

        # Tên nhân viên dùng yticks — cách đáng tin cậy nhất
        medal_prefix = ["#1 ", "#2 ", "#3 "]
        yticklabels = []
        for i, rank in enumerate(rank_rev):
            prefix = medal_prefix[rank] if rank < 3 else "    "
            yticklabels.append(f"{prefix}{names_rev[i]}")

        ax.set_yticks(y_pos)
        ax.set_yticklabels(yticklabels, fontsize=10, fontweight="bold")

        # Màu từng ytick label theo rank
        for i, (tick, rank) in enumerate(zip(ax.get_yticklabels(), rank_rev)):
            if rank == 0:   tick.set_color(C_AMBER)
            elif rank == 1: tick.set_color(C_BLUE)
            elif rank == 2: tick.set_color(C_TEAL)
            else:           tick.set_color("#475569"); tick.set_fontweight("normal")

        # Giá trị ở cuối bar
        for bar, v, rank in zip(bars, vals_rev, rank_rev):
            col = medal_col[rank] if rank < 3 else "#334155"
            fw  = "bold" if rank < 3 else "normal"
            txt = f"{v:.2f} ty" if v > 0 else "0.00 ty"
            tcol = col if v > 0 else "#94a3b8"
            ax.text(v + max_v * 0.02,
                    bar.get_y() + bar.get_height() / 2,
                    txt, va="center", ha="left",
                    color=tcol, fontsize=10, fontweight=fw)

        ax.set_xlim(0, max_v * 1.45)
        ax.set_ylim(-0.6, n - 0.3)
        ax.spines[:].set_visible(False)
        ax.xaxis.set_visible(False)
        ax.tick_params(axis="y", length=0, pad=6)
        ax.grid(axis="x", linestyle="--", alpha=0.2, color="#e2e8f0", zorder=0)

        self.fig_lead.text(0.5, 0.97,
                           f"Leaderboard doanh so nhan vien {sel_y}",
                           ha="center", color="#1e293b",
                           fontsize=11, fontweight="bold")
        self.fig_lead.subplots_adjust(top=0.90, bottom=0.04, left=0.22, right=0.88)
        self.canvas_lead.draw()

    # ── ĐƠN HÀNG GẦN ĐÂY ─────────────────────────────────
    def _draw_recent(self, conn):
        recent = conn.execute("""
            SELECT dh.ma_don, x.hang_xe||' '||x.dong_xe,
                   kh.ho_ten, dh.gia_ban_thuc, dh.trang_thai
            FROM don_hang dh JOIN xe x ON dh.xe_id=x.id
            JOIN khach_hang kh ON dh.kh_id=kh.id
            ORDER BY dh.id DESC LIMIT 5""").fetchall()

        while self.recent_lv.count():
            item = self.recent_lv.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        STATUS_COL = {
            "Đã giao xe": C_GREEN, "Đã thanh toán": C_BLUE,
            "Chờ xử lý": C_AMBER, "Huỷ": C_RED, "Đặt cọc": C_PURPLE
        }
        STATUS_BG = {
            "Đã giao xe": "rgba(16,185,129,.08)", "Đã thanh toán": "rgba(37,99,235,.08)",
            "Chờ xử lý": "rgba(245,158,11,.08)", "Huỷ": "rgba(239,68,68,.08)",
            "Đặt cọc": "rgba(139,92,246,.08)"
        }
        for r in recent:
            row_w = QWidget()
            col = STATUS_COL.get(r[4], C_MUTED)
            row_w.setStyleSheet(
                f"background:#ffffff;border-radius:10px;border:1px solid #e2e8f0;"
            )
            rl = QHBoxLayout(row_w); rl.setContentsMargins(16, 12, 16, 12)
            ma  = QLabel(r[0]); ma.setStyleSheet(f"color:{C_BLUE};font-weight:800;font-size:14px;background:transparent;min-width:66px;")
            ten = QLabel(r[1]); ten.setStyleSheet(f"color:{C_TEXT};font-size:14px;font-weight:700;background:transparent;")
            kh  = QLabel(r[2]); kh.setStyleSheet(f"color:{C_MUTED};font-size:13px;font-weight:600;background:transparent;")
            gia = QLabel(f"{r[3]/1e9:.2f} tỷ"); gia.setStyleSheet(f"color:{C_GREEN};font-weight:800;font-size:14px;background:transparent;")
            tt  = QLabel(r[4]); tt.setStyleSheet(f"color:{col};font-weight:700;font-size:13px;background:transparent;min-width:110px;")
            tt.setAlignment(Qt.AlignmentFlag.AlignRight)
            rl.addWidget(ma); rl.addWidget(ten, 1); rl.addWidget(kh); rl.addWidget(gia); rl.addWidget(tt)
            self.recent_lv.addWidget(row_w)

    def _tick(self):
        try:
            self.lbl_time.setText(datetime.now().strftime("%d/%m/%Y  %H:%M:%S"))
        except RuntimeError:
            try: self._timer.stop()
            except Exception: pass