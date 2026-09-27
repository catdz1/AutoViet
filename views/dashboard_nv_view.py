"""
views/dashboard_nv_view.py — Dashboard KPI Nhân viên NÂNG CẤP
+ Giữ nguyên toàn bộ tính năng cũ
+ THÊM: Gauge KPI % hoàn thành cá nhân
+ THÊM: Biểu đồ so sánh doanh số với trung bình công ty
+ THÊM: Cảnh báo cá nhân (đơn cần xử lý, lịch BD)
+ THÊM: Mini leaderboard vị trí của NV
+ Giao diện đẹp hơn, màu sắc nhất quán
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QFrame, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer
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
from datetime import datetime, date
import calendar

# ── Màu chủ đạo ──────────────────────────────────────────
C_BLUE   = "#2563eb"
C_GREEN  = "#10b981"
C_AMBER  = "#f59e0b"
C_RED    = "#ef4444"
C_PURPLE = "#8b5cf6"
C_TEAL   = "#06b6d4"
C_MUTED  = "#64748b"
C_TEXT   = "#0f172a"


class DashboardNVView(QWidget):
    """Dashboard KPI cá nhân dành riêng cho Nhân viên — Phiên bản nâng cấp"""

    def __init__(self, current_user=None):
        super().__init__()
        self.setObjectName("page_dashboard_nv")
        self.current_user = current_user or {}
        self.lbl_time = QLabel()
        self._build()
        self.refresh()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(1000)
        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self.refresh)
        self._refresh_timer.start(30000)

    def _build(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea{background:#f1f5f9;border:none;}
            QScrollBar:vertical{width:6px;background:#e2e8f0;border-radius:3px;}
            QScrollBar::handle:vertical{background:#94a3b8;border-radius:3px;min-height:30px;}
            QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{height:0px;}
        """)
        content = QWidget()
        content.setStyleSheet("background:#f1f5f9;")
        self._lv = QVBoxLayout(content)
        self._lv.setContentsMargins(20, 16, 20, 24)
        self._lv.setSpacing(14)
        scroll.setWidget(content)
        root = QVBoxLayout(self); root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(scroll)

        # ── HEADER ─────────────────────────────────────────
        hr = QHBoxLayout()
        name = self.current_user.get("ho_ten", "Nhân viên")
        outer_title = QWidget()
        outer_title.setStyleSheet("background:#10b981;border-radius:6px;")
        otl = QHBoxLayout(outer_title); otl.setContentsMargins(4,0,0,0); otl.setSpacing(0)
        inner_title = QWidget()
        inner_title.setStyleSheet("background:#f1f5f9;border-radius:4px;")
        itl = QHBoxLayout(inner_title); itl.setContentsMargins(10,6,10,6)
        title = QLabel(f"KPI ca nhan — {name}")
        title.setStyleSheet("font-size:17px;font-weight:800;color:#0f172a;background:transparent;")
        itl.addWidget(title)
        otl.addWidget(inner_title)
        self.lbl_time.setStyleSheet("color:#64748b;font-size:12px;background:transparent;")
        hr.addWidget(outer_title); hr.addStretch(); hr.addWidget(self.lbl_time)
        self._lv.addLayout(hr)

        # ── CẢNH BÁO CÁ NHÂN ──────────────────────────────
        self.alert_widget = QWidget()
        self.alert_lv = QVBoxLayout(self.alert_widget)
        self.alert_lv.setContentsMargins(0, 0, 0, 0)
        self.alert_lv.setSpacing(4)
        self.alert_widget.hide()
        self._lv.addWidget(self.alert_widget)

        # ── MỤC TIÊU THÁNG (card nâng cấp) ────────────────
        goal_w = QWidget()
        goal_w.setStyleSheet(
            "background:#ffffff;border-radius:14px;border:1.5px solid #dcfce7;"
        )
        gl = QVBoxLayout(goal_w); gl.setContentsMargins(18, 14, 18, 16); gl.setSpacing(10)

        goal_header = QHBoxLayout()
        gl_title = QLabel("🎯  Mục tiêu tháng này")
        gl_title.setStyleSheet("font-size:15px;font-weight:800;color:#065f46;background:transparent;")
        self.lbl_goal_pct = QLabel("0%")
        self.lbl_goal_pct.setStyleSheet("font-size:22px;font-weight:800;color:#10b981;background:transparent;")
        goal_header.addWidget(gl_title); goal_header.addStretch(); goal_header.addWidget(self.lbl_goal_pct)
        gl.addLayout(goal_header)

        # Progress doanh thu
        self.lbl_goal_dt = QLabel("Doanh thu: 0 / 2 tỷ")
        self.lbl_goal_dt.setStyleSheet("font-size:13px;font-weight:700;color:#1e40af;background:transparent;")
        self.pb_dt = self._make_progress("#10b981")
        # Progress số đơn
        self.lbl_goal_don = QLabel("Số đơn: 0 / 5 đơn")
        self.lbl_goal_don.setStyleSheet("font-size:13px;font-weight:700;color:#065f46;background:transparent;")
        self.pb_don = self._make_progress("#2563eb")
        for w in [self.lbl_goal_dt, self.pb_dt, self.lbl_goal_don, self.pb_don]:
            gl.addWidget(w)
        self._lv.addWidget(goal_w)

        # ── 4 STAT CARDS ───────────────────────────────────
        stat_h = QHBoxLayout();
        stat_h.setSpacing(10)
        self.sc_don = self._stat("📋", "ĐƠN THÁNG NÀY", "0", C_BLUE)
        self.sc_dt = self._stat("💰", "DOANH THU", "0 ₫", C_GREEN)
        self.sc_dv = self._stat("🔧", "DỊCH VỤ", "0", C_AMBER)
        self.sc_hang = self._stat("🏆", "XẾP HẠNG", "#0", C_PURPLE)
        self.sc_luong = self._stat("💵", "LƯƠNG TT", "0 ₫", C_TEAL)  # ← THÊM
        for sc in [self.sc_don, self.sc_dt, self.sc_dv, self.sc_hang, self.sc_luong]:
            stat_h.addWidget(sc)
        self._lv.addLayout(stat_h)

        # ── BIỂU ĐỒ HÀNG 1: Gauge + Bar doanh thu ─────────
        row_charts1 = QHBoxLayout(); row_charts1.setSpacing(12)

        # Gauge KPI cá nhân
        self.fig_gauge = Figure(facecolor="#ffffff", figsize=(4, 3), dpi=80)
        self.canvas_gauge = FigureCanvasQTAgg(self.fig_gauge)
        self.canvas_gauge.setStyleSheet("border-radius:12px;border:1.5px solid #dcfce7;")
        row_charts1.addWidget(self.canvas_gauge, 2)

        # Bar doanh thu theo tháng
        self.fig = Figure(facecolor="#ffffff", figsize=(7, 3), dpi=80)
        self.canvas = FigureCanvasQTAgg(self.fig)
        self.canvas.setStyleSheet("border-radius:12px;border:1.5px solid #dcfce7;")
        self.canvas.setMinimumHeight(240)
        row_charts1.addWidget(self.canvas, 3)
        self._lv.addLayout(row_charts1)

        # ── BIỂU ĐỒ HÀNG 2: So sánh với TB công ty ────────
        self.fig_compare = Figure(facecolor="#ffffff", figsize=(10, 2.8), dpi=80)
        self.canvas_compare = FigureCanvasQTAgg(self.fig_compare)
        self.canvas_compare.setStyleSheet("border-radius:12px;border:1.5px solid #dcfce7;")
        self.canvas_compare.setMinimumHeight(200)
        self._lv.addWidget(self.canvas_compare)

        # ── ĐƠN HÀNG CỦA TÔI ──────────────────────────────
        lh = QLabel("📋  Đơn hàng của tôi")
        lh.setStyleSheet("font-size:14px;font-weight:800;color:#065f46;background:transparent;margin-top:4px;")
        self._lv.addWidget(lh)
        self.don_widget = QWidget()
        self.don_lv = QVBoxLayout(self.don_widget)
        self.don_lv.setContentsMargins(0, 0, 0, 0)
        self.don_lv.setSpacing(5)
        self._lv.addWidget(self.don_widget)

    # ── WIDGET HELPERS ─────────────────────────────────────
    def _make_progress(self, color):
        pb = QProgressBar()
        pb.setRange(0, 100); pb.setValue(0)
        pb.setFixedHeight(14)
        pb.setStyleSheet(f"""
            QProgressBar{{background:#f1f5f9;border-radius:7px;border:none;
                text-align:center;color:{color};font-size:10px;font-weight:700;}}
            QProgressBar::chunk{{background:{color};border-radius:7px;}}
        """)
        return pb

    def _stat(self, icon, label, val, color):
        outer = QWidget()
        outer.setStyleSheet(f"background:{color};border-radius:12px;")
        outer_lv = QVBoxLayout(outer)
        outer_lv.setContentsMargins(0, 4, 0, 0)
        outer_lv.setSpacing(0)
        w = QWidget()
        w.setStyleSheet("background:#ffffff;border-radius:10px;")
        lv = QVBoxLayout(w); lv.setContentsMargins(14, 12, 14, 12); lv.setSpacing(3)
        li = QLabel(icon); li.setStyleSheet("font-size:22px;background:transparent;")
        ll = QLabel(label); ll.setStyleSheet(f"font-size:10px;color:{color};font-weight:800;letter-spacing:1px;background:transparent;")
        lv2 = QLabel(val); lv2.setStyleSheet(f"font-size:22px;font-weight:800;color:{color};background:transparent;")
        lv.addWidget(li); lv.addWidget(ll); lv.addWidget(lv2)
        outer_lv.addWidget(w)
        outer._val = lv2; return outer

    # ── REFRESH ────────────────────────────────────────────
    def refresh(self):
        try:
            self._do_refresh()
        except Exception as e:
            import traceback
            print(f"[DashboardNV refresh error] {e}")
            traceback.print_exc()

    def _do_refresh(self):
        nv_id = self.current_user.get("nv_id")
        if not nv_id:
            return

        conn = get_conn()
        cur_m = datetime.now().month
        cur_y = datetime.now().year

        # ── Thống kê tháng ─────────────────────────────────
        don_thang = conn.execute("""
            SELECT COUNT(*), COALESCE(SUM(gia_ban_thuc),0)
            FROM don_hang WHERE nv_id=?
            AND strftime('%Y-%m',ngay_dat)=?
        """, (nv_id, f"{cur_y}-{cur_m:02d}")).fetchone()

        dv_thang = conn.execute("""
            SELECT COUNT(*) FROM dich_vu WHERE nv_id=?
            AND strftime('%Y-%m',ngay_nhan)=?
        """, (nv_id, f"{cur_y}-{cur_m:02d}")).fetchone()[0]

        all_dt = conn.execute("""
            SELECT nv_id, COALESCE(SUM(gia_ban_thuc),0) as dt
            FROM don_hang WHERE trang_thai IN ('Đã thanh toán','Đã giao xe')
            AND strftime('%Y',ngay_dat)=?
            GROUP BY nv_id ORDER BY dt DESC
        """, (str(cur_y),)).fetchall()
        rank = next((i+1 for i, r in enumerate(all_dt) if r[0]==nv_id), len(all_dt)+1)

        so_don    = don_thang[0] or 0
        dt_thang  = don_thang[1] or 0
        self.sc_don._val.setText(str(so_don))
        self.sc_dt._val.setText(f"{dt_thang/1e9:.3f} tỷ")
        self.sc_dv._val.setText(str(dv_thang))
        self.sc_hang._val.setText(f"#{rank}/{len(all_dt) if all_dt else 1}")

        # ── Mục tiêu ───────────────────────────────────────
        goal_dt = 2e9; goal_don = 5
        pct_dt  = min(int(dt_thang / goal_dt * 100), 100)
        pct_don = min(int(so_don / goal_don * 100), 100)
        overall = (pct_dt + pct_don) // 2
        self.lbl_goal_pct.setText(f"{overall}%")
        color_pct = C_GREEN if overall >= 80 else (C_AMBER if overall >= 50 else C_RED)
        self.lbl_goal_pct.setStyleSheet(f"font-size:22px;font-weight:800;color:{color_pct};background:transparent;")
        self.pb_dt.setValue(pct_dt); self.pb_dt.setFormat(f"{pct_dt}%")
        self.pb_don.setValue(pct_don); self.pb_don.setFormat(f"{pct_don}%")
        self.lbl_goal_dt.setText(f"Doanh thu: {dt_thang/1e9:.3f} / 2.000 tỷ ₫")
        self.lbl_goal_don.setText(f"Số đơn: {so_don} / 5 đơn")

        # ── Cảnh báo cá nhân ───────────────────────────────
        try:
            self._update_alerts(conn, nv_id)
        except Exception as e:
            print(f"[alerts error] {e}")
            self.alert_widget.hide()

        # ── Biểu đồ ────────────────────────────────────────
        months_dt = []
        for m in range(1, 13):
            v = conn.execute("""SELECT COALESCE(SUM(gia_ban_thuc),0)
                FROM don_hang WHERE nv_id=?
                AND strftime('%Y-%m',ngay_dat)=?""",
                (nv_id, f"{cur_y}-{m:02d}")).fetchone()[0]
            months_dt.append(v / 1e9)

        # TB công ty theo tháng
        tb_company = []
        nv_count = max(conn.execute("SELECT COUNT(*) FROM nhan_vien").fetchone()[0], 1)
        for m in range(1, 13):
            v = conn.execute("""SELECT COALESCE(SUM(gia_ban_thuc),0)
                FROM don_hang WHERE strftime('%Y-%m',ngay_dat)=?""",
                (f"{cur_y}-{m:02d}",)).fetchone()[0]
            tb_company.append(v / 1e9 / nv_count)

        self._draw_gauge(dt_thang, goal_dt, cur_y)
        self._draw_bar(months_dt, cur_m, cur_y)
        self._draw_compare(months_dt, tb_company, cur_y)
        self._draw_gauge(dt_thang, goal_dt, cur_y)
        self._draw_bar(months_dt, cur_m, cur_y)
        self._draw_compare(months_dt, tb_company, cur_y)

        # ── Tính lương TT tháng này ──────────────────────────  ← THÊM TỪ ĐÂY
        try:
            nv_info = conn.execute(
                "SELECT luong FROM nhan_vien WHERE id=?", (nv_id,)
            ).fetchone()
            luong_cb = float(nv_info[0] or 0) if nv_info else 0

            days_in = calendar.monthrange(cur_y, cur_m)[1]
            work_days = sum(1 for d in range(1, days_in + 1)
                            if date(cur_y, cur_m, d).weekday() < 5)

            cc_rows = conn.execute("""
                    SELECT trang_thai, phat, thuong FROM cham_cong
                    WHERE nv_id=? AND strftime('%Y-%m', ngay)=?
                """, (nv_id, f"{cur_y}-{cur_m:02d}")).fetchall()

            di_lam = sum(1 for r in cc_rows if r[0] != "Vắng mặt")
            tong_phat = sum(float(r[1] or 0) for r in cc_rows)
            tong_thuong = sum(float(r[2] or 0) for r in cc_rows)

            luong_tt = (luong_cb / work_days * di_lam
                        if work_days > 0 else 0) - tong_phat + tong_thuong
            luong_tt = max(0, luong_tt)  # không âm

            mau_luong = C_TEAL if luong_tt > 0 else C_MUTED
            self.sc_luong._val.setText(f"{luong_tt / 1e6:.2f}tr")
            self.sc_luong._val.setStyleSheet(
                f"font-size:20px;font-weight:800;color:{mau_luong};background:transparent;"
            )
        except Exception as e:
            print(f"[luong_tt error] {e}")
            self.sc_luong._val.setText("—")
        # ── KẾT THÚC THÊM ────────────────────────────────────

        self._draw_recent(conn, nv_id)
        conn.close()
        return  # _do_refresh end

    # ── CẢNH BÁO CÁ NHÂN ──────────────────────────────────
    def _update_alerts(self, conn, nv_id):
        while self.alert_lv.count():
            item = self.alert_lv.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        alerts = []
        cho_xu_ly = conn.execute("""
            SELECT COUNT(*) FROM don_hang WHERE nv_id=? AND trang_thai='Chờ xử lý'
        """, (nv_id,)).fetchone()[0]
        if cho_xu_ly > 0:
            alerts.append(("📋", f"Bạn có {cho_xu_ly} đơn hàng đang chờ xử lý!", C_AMBER, "rgba(245,158,11,.08)", "rgba(245,158,11,.3)"))

        bd_sap = conn.execute("""
            SELECT COUNT(*) FROM lich_baoduong
            WHERE date(ngay_hen) <= date('now','+7 days')
            AND trang_thai != 'Hoàn thành'
        """).fetchone()[0]
        if bd_sap > 0:
            alerts.append(("🔧", f"Có {bd_sap} lịch bảo dưỡng sắp đến hạn trong 7 ngày tới.", C_BLUE, "rgba(37,99,235,.08)", "rgba(37,99,235,.3)"))

        if not alerts:
            self.alert_widget.hide(); return

        for icon, msg, color, bg, border_c in alerts:
            row = QWidget()
            row.setStyleSheet(f"background:{bg};border:1px solid {border_c};border-radius:8px;padding-left:4px;")
            rl = QHBoxLayout(row); rl.setContentsMargins(12, 8, 12, 8)
            li = QLabel(icon); li.setStyleSheet("font-size:16px;background:transparent;")
            lm = QLabel(msg); lm.setStyleSheet(f"color:{color};font-size:13px;font-weight:600;background:transparent;")
            rl.addWidget(li); rl.addWidget(lm); rl.addStretch()
            self.alert_lv.addWidget(row)
        self.alert_widget.show()

    # ── GAUGE CÁ NHÂN ─────────────────────────────────────
    def _draw_gauge(self, dt_thang, goal, cur_y):
        self.fig_gauge.clear()
        ax = self.fig_gauge.add_subplot(111)
        ax.set_facecolor("#ffffff"); self.fig_gauge.set_facecolor("#ffffff")
        ax.set_aspect('equal'); ax.axis('off')

        pct  = min(dt_thang / goal, 1.0)
        col  = C_GREEN if pct >= 0.8 else (C_AMBER if pct >= 0.5 else C_RED)
        theta = np.linspace(np.pi, 0, 100)

        # Nền
        ax.plot(np.cos(theta), np.sin(theta), color="#e2e8f0", linewidth=14, solid_capstyle='round')
        # Tiến độ
        theta2 = np.linspace(np.pi, np.pi - pct * np.pi, 100)
        ax.plot(np.cos(theta2), np.sin(theta2), color=col, linewidth=14, solid_capstyle='round')

        # Kim
        angle = np.pi - pct * np.pi
        ax.annotate("", xy=(0.58*np.cos(angle), 0.58*np.sin(angle)), xytext=(0, 0),
                    arrowprops=dict(arrowstyle="->", color=col, lw=2.5))
        ax.add_patch(mpatches.Circle((0, 0), 0.07, color=col, zorder=5))

        ax.text(0, -0.18, f"{pct*100:.0f}%", ha="center", va="center",
                fontsize=22, fontweight="bold", color=col)
        ax.text(0, -0.38, f"{dt_thang/1e9:.2f} / {goal/1e9:.1f} tỷ ₫",
                ha="center", va="center", fontsize=9, color=C_MUTED)

        months_label = datetime.now().strftime("%m/%Y")
        ax.text(-0.95, -0.12, "0%",   ha="center", fontsize=8, color="#94a3b8")
        ax.text(0.95,  -0.12, "100%", ha="center", fontsize=8, color="#94a3b8")
        ax.set_xlim(-1.1, 1.1); ax.set_ylim(-0.55, 1.1)
        self.fig_gauge.text(0.5, 0.96, f"KPI doanh thu thang {months_label}",
                            ha="center", color="#065f46", fontsize=10, fontweight="bold")
        self.fig_gauge.subplots_adjust(top=0.86, bottom=0.04, left=0.04, right=0.96)
        self.canvas_gauge.draw()

    # ── BAR DOANH THU CÁ NHÂN ─────────────────────────────
    def _draw_bar(self, months_dt, cur_m, cur_y):
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.set_facecolor("#f8fafc"); self.fig.set_facecolor("#ffffff")
        x = list(range(1, 13))
        max_v = max(months_dt) if months_dt and max(months_dt) > 0 else 1
        colors = [C_GREEN if i+1 == cur_m else "#bbf7d0" for i in range(12)]
        ax.bar(x, months_dt, color=colors, width=0.65, zorder=3, edgecolor="#fff", linewidth=1)
        ax.plot(x, months_dt, color="#059669", linewidth=2.5,
                marker="o", markersize=5, markerfacecolor="#fff",
                markeredgecolor=C_GREEN, markeredgewidth=2, zorder=4)
        ax.fill_between(x, months_dt, alpha=0.07, color=C_GREEN)
        for i, v in enumerate(months_dt):
            if v > max_v * 0.05:
                ax.text(i+1, v + max_v*0.03, f"{v:.2f}", ha="center",
                        color="#334155", fontsize=7, fontweight="600")
        ax.set_xticks(x)
        ax.set_xticklabels([f"T{i}" for i in x], color="#475569", fontsize=8)
        ax.spines[:].set_visible(False); ax.yaxis.set_visible(False)
        ax.set_ylim(0, max_v * 1.5)
        ax.grid(axis='y', linestyle='--', alpha=0.3, color="#dcfce7")
        ax.tick_params(colors="#64748b")
        self.fig.text(0.5, 0.95, f"Doanh thu ca nhan nam {cur_y} (ty d)",
                      ha="center", color="#065f46", fontsize=10, fontweight="bold")
        self.fig.subplots_adjust(top=0.86, bottom=0.14, left=0.02, right=0.98)
        self.canvas.draw()

    # ── SO SÁNH VỚI TB CÔNG TY ────────────────────────────
    def _draw_compare(self, months_dt, tb_company, cur_y):
        self.fig_compare.clear()
        ax = self.fig_compare.add_subplot(111)
        ax.set_facecolor("#f8fafc"); self.fig_compare.set_facecolor("#ffffff")
        x = list(range(1, 13))
        width = 0.35
        x_arr = np.array(x)

        ax.bar(x_arr - width/2, months_dt, width, label="Của tôi",
               color=C_GREEN, alpha=0.85, zorder=3, edgecolor="#fff")
        ax.bar(x_arr + width/2, tb_company, width, label="TB công ty",
               color="#94a3b8", alpha=0.7, zorder=3, edgecolor="#fff")

        ax.set_xticks(x)
        ax.set_xticklabels([f"T{i}" for i in x], color="#475569", fontsize=8)
        ax.spines[:].set_visible(False); ax.yaxis.set_visible(False)
        ax.legend(loc="upper right", fontsize=9, facecolor="#fff",
                  edgecolor="#e2e8f0", labelcolor="#334155")
        ax.grid(axis='y', linestyle='--', alpha=0.25, color="#dcfce7")
        ax.tick_params(colors="#64748b")
        all_vals = months_dt + tb_company
        max_v = max(all_vals) if all_vals and max(all_vals) > 0 else 1
        ax.set_ylim(0, max_v * 1.5 if max_v > 0 else 1)
        self.fig_compare.text(0.5, 0.95, f"So sanh doanh so voi trung binh cong ty {cur_y}",
                              ha="center", color="#065f46", fontsize=10, fontweight="bold")
        self.fig_compare.subplots_adjust(top=0.86, bottom=0.16, left=0.02, right=0.98)
        self.canvas_compare.draw()

    # ── ĐƠN HÀNG GẦN ĐÂY ─────────────────────────────────
    def _draw_recent(self, conn, nv_id):
        recent = conn.execute("""
            SELECT dh.ma_don, x.hang_xe||' '||x.dong_xe,
                   kh.ho_ten, dh.gia_ban_thuc, dh.trang_thai, dh.ngay_dat
            FROM don_hang dh JOIN xe x ON dh.xe_id=x.id
            JOIN khach_hang kh ON dh.kh_id=kh.id
            WHERE dh.nv_id=? ORDER BY dh.id DESC LIMIT 5
        """, (nv_id,)).fetchall()

        while self.don_lv.count():
            item = self.don_lv.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        STATUS_COL = {
            "Đã giao xe": C_GREEN, "Đã thanh toán": C_BLUE,
            "Chờ xử lý": C_AMBER, "Huỷ": C_RED, "Đặt cọc": C_PURPLE
        }
        for r in recent:
            col = STATUS_COL.get(r[4], C_MUTED)
            row_w = QWidget()
            row_w.setStyleSheet(
                f"background:#ffffff;border-radius:10px;border:1px solid #dcfce7;"
            )
            rl = QHBoxLayout(row_w); rl.setContentsMargins(14, 10, 14, 10); rl.setSpacing(12)
            ma  = QLabel(r[0]); ma.setStyleSheet(f"color:{C_BLUE};font-weight:800;font-size:14px;background:#eff6ff;border-radius:6px;padding:2px 8px;min-width:60px;")
            ten = QLabel(r[1]); ten.setStyleSheet(f"color:{C_TEXT};font-size:14px;font-weight:700;background:transparent;")
            kh  = QLabel(r[2]); kh.setStyleSheet(f"color:{C_MUTED};font-size:13px;font-weight:600;background:transparent;")
            gia = QLabel(f"{r[3]/1e9:.2f} tỷ"); gia.setStyleSheet(f"color:{C_GREEN};font-weight:800;font-size:14px;background:transparent;")
            tt  = QLabel(r[4]); tt.setStyleSheet(f"color:{col};font-weight:700;font-size:13px;background:transparent;min-width:100px;")
            tt.setAlignment(Qt.AlignmentFlag.AlignRight)
            ngay = QLabel(r[5]); ngay.setStyleSheet(f"color:#94a3b8;font-size:12px;background:transparent;min-width:80px;")
            ngay.setAlignment(Qt.AlignmentFlag.AlignRight)
            rl.addWidget(ma); rl.addWidget(ten, 1); rl.addWidget(kh)
            rl.addWidget(gia); rl.addWidget(tt); rl.addWidget(ngay)
            self.don_lv.addWidget(row_w)

    def _tick(self):
        self.lbl_time.setText(datetime.now().strftime("%d/%m/%Y  %H:%M:%S"))