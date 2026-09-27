"""
views/cham_cong_view.py — Quản lý Chấm công
+ Chấm công theo ngày (vào/ra)
+ Lịch tháng trực quan
+ Thống kê: đúng giờ, đi muộn, vắng, nửa buổi
+ Thưởng/Phạt tự động
+ Tính lương theo ngày công
+ Xuất Excel
+ Admin xem tất cả NV, NV xem cá nhân
"""
import sys, os, calendar
from datetime import datetime, date, timedelta
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QDialog, QFormLayout, QComboBox, QLineEdit, QTextEdit,
    QMessageBox, QScrollArea, QGridLayout, QDoubleSpinBox,
    QTimeEdit, QTabWidget, QSplitter
)
from PyQt6.QtCore import Qt, QTimer, QTime, QDate
from PyQt6.QtGui import QColor, QFont, QCursor
from database import get_conn

# ── Giờ quy định ──────────────────────────────────────
GIO_VAO_CHUAN  = QTime(8, 0)   # 08:00
GIO_VAO_MUON   = QTime(8, 15)  # Sau 08:15 → đi muộn
GIO_RA_CHUAN   = QTime(17, 30) # 17:30
GIO_RA_SOM     = QTime(17, 0)  # Trước 17:00 → về sớm

# Thưởng/Phạt
PHAT_DI_MUON   = 50_000   # 50k/lần đi muộn
PHAT_VE_SOM    = 50_000   # 50k/lần về sớm
PHAT_VANG      = 200_000  # 200k/ngày vắng
PHAT_NUA_BUOI  = 100_000  # 100k/nửa buổi
THUONG_CC_DAY  = 200_000  # Thưởng chuyên cần đủ tháng

STYLE = """
QWidget { font-family: 'Segoe UI', Arial; }
QTabWidget::pane { border: none; background: #0a0c12; }
QTabBar::tab {
    background: #13151c; color: #64748b;
    padding: 10px 22px; font-size: 12px; font-weight: 600;
    border: none; border-bottom: 2px solid transparent;
}
QTabBar::tab:selected { color: #a78bfa; border-bottom: 2px solid #7c3aed; background: #1a1d28; }
QTabBar::tab:hover { color: #c8d0e0; background: #1a1d28; }

QPushButton#btn_cc {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #6d28d9, stop:1 #7c3aed);
    color: white; border: none; border-radius: 12px;
    font-size: 14px; font-weight: 800; padding: 14px 28px;
}
QPushButton#btn_cc:hover { background: #7c3aed; }
QPushButton#btn_cc:disabled { background: #2c1f6e; color: #64748b; }

QPushButton#btn_ra {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #065f46, stop:1 #059669);
    color: white; border: none; border-radius: 12px;
    font-size: 14px; font-weight: 800; padding: 14px 28px;
}
QPushButton#btn_ra:hover { background: #059669; }
QPushButton#btn_ra:disabled { background: #1a3a2a; color: #64748b; }

QPushButton#btn_excel {
    background: #14532d; color: #86efac;
    border: 1px solid #166534; border-radius: 8px;
    font-size: 12px; padding: 8px 16px;
}
QPushButton#btn_excel:hover { background: #166534; }
QPushButton#btn_edit {
    background: #1e3a5f; color: #60a5fa;
    border: 1px solid #1e3a5f; border-radius: 8px;
    font-size: 12px; padding: 8px 14px;
}
QPushButton#btn_del {
    background: #450a0a; color: #fca5a5;
    border: 1px solid #7f1d1d; border-radius: 8px;
    font-size: 12px; padding: 8px 14px;
}
QComboBox#sel_nv, QComboBox#sel_thang, QComboBox#sel_nam {
    background: #f9fafb; 
    color: #111827;
    border: 2px solid #e5e7eb; 
    border-radius: 8px;
    padding: 8px 12px; 
    font-size: 13px; 
    font-weight: 700;
    min-width: 140px;
}
QComboBox#sel_nv:focus, QComboBox#sel_thang:focus, QComboBox#sel_nam:focus {
    border: 2px solid #2563eb;
}
QComboBox::drop-down { border: none; }
QComboBox QAbstractItemView {
    background: #ffffff; 
    color: #111827;
    border: 1px solid #e5e7eb; 
    selection-background-color: #dbeafe;
    selection-color: #0284c7;
}
QTableWidget {
  background: #ffffff; alternate-background-color: #f0f4ff;
  gridline-color: #e5e7eb; border: none;
}
QTableWidget::item { padding: 10px 12px; color: #0f172a; }
QTableWidget::item:selected { background: #dbeafe; color: #1d4ed8; }
QHeaderView::section {
  background: #0f172a; color: #ffffff;
  font-size: 12px; font-weight: 800; letter-spacing: 1px;
  padding: 14px 12px; border: none;
}
"""

TT_COLOR = {
    "Đúng giờ":  "#4ade80",
    "Đi muộn":   "#fbbf24",
    "Về sớm":    "#f97316",
    "Vắng mặt":  "#f87171",
    "Nửa buổi":  "#a78bfa",
    "Nghỉ phép": "#60a5fa",
    "Ngày lễ":   "#2dd4bf",
}

TT_ICON = {
    "Đúng giờ":  "✅",
    "Đi muộn":   "⏰",
    "Về sớm":    "🏃",
    "Vắng mặt":  "❌",
    "Nửa buổi":  "⚡",
    "Nghỉ phép": "🌴",
    "Ngày lễ":   "🎉",
}


def _ensure_table():
    conn = get_conn()
    conn.execute('''CREATE TABLE IF NOT EXISTS cham_cong (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nv_id INTEGER NOT NULL,
        ngay TEXT NOT NULL,
        gio_vao TEXT,
        gio_ra TEXT,
        trang_thai TEXT DEFAULT 'Đúng giờ',
        ghi_chu TEXT,
        thuong REAL DEFAULT 0,
        phat REAL DEFAULT 0,
        created_at TEXT DEFAULT (datetime('now','localtime')),
        FOREIGN KEY(nv_id) REFERENCES nhan_vien(id)
    )''')
    conn.commit(); conn.close()


def _tinh_trang_thai(gio_vao_str, gio_ra_str):
    """Tự động tính trạng thái từ giờ vào/ra"""
    if not gio_vao_str:
        return "Vắng mặt", PHAT_VANG, 0
    try:
        gv = QTime.fromString(gio_vao_str, "HH:mm")
        gr = QTime.fromString(gio_ra_str, "HH:mm") if gio_ra_str else None

        muon = gv > GIO_VAO_MUON
        ve_som = gr and gr < GIO_RA_SOM if gr else False

        if muon and ve_som:
            return "Nửa buổi", PHAT_NUA_BUOI, 0
        elif muon:
            return "Đi muộn", PHAT_DI_MUON, 0
        elif ve_som:
            return "Về sớm", PHAT_VE_SOM, 0
        else:
            return "Đúng giờ", 0, 0
    except Exception:
        return "Đúng giờ", 0, 0


class ChamCongView(QWidget):
    def __init__(self, current_user=None):
        super().__init__()
        self.setObjectName("page_cham_cong")
        self.setStyleSheet(STYLE)
        self.current_user = current_user or {}
        self.is_admin = current_user.get("role") == "admin" if current_user else False
        self.nv_id_current = current_user.get("nv_id") if current_user else None
        # ✅ AUTO-CREATE NHAN_VIEN nếu chưa tồn tại
        if not self.nv_id_current and current_user:
            conn = get_conn()
            ho_ten = current_user.get("ho_ten", "")
            user_id = current_user.get("id")
            email = current_user.get("email", "")
            if ho_ten and user_id:
                try:
                    # Kiểm tra xem có nhân viên cùng tên chưa
                    nv = conn.execute(
                        "SELECT id FROM nhan_vien WHERE LOWER(ho_ten)=LOWER(?)",
                        (ho_ten,)
                    ).fetchone()
                    if nv:
                        # Có rồi → liên kết
                        self.nv_id_current = nv[0]
                        conn.execute("UPDATE users SET nv_id=? WHERE id=?", (nv[0], user_id))
                        conn.commit()
                        print(f"[✓] Liên kết NV: {ho_ten} (id={self.nv_id_current})")
                    else:
                        # Chưa có → tạo mới
                        cnt = conn.execute("SELECT COUNT(*) FROM nhan_vien").fetchone()[0]
                        ma_nv = f"NV{cnt + 1:03d}"

                        while conn.execute("SELECT id FROM nhan_vien WHERE ma_nv=?", (ma_nv,)).fetchone():
                            cnt += 1
                            ma_nv = f"NV{cnt + 1:03d}"
                        # ✅ FIX: Dùng cursor để lấy lastrowid
                        c = conn.cursor()
                        c.execute("""
                            INSERT INTO nhan_vien(ma_nv, ho_ten, chuc_vu, trang_thai, email)
                            VALUES(?, ?, 'Nhân viên', 'Dang lam', ?)
                        """, (ma_nv, ho_ten, email))
                        self.nv_id_current = c.lastrowid  # ✅ FIX: Lấy từ cursor
                        conn.execute("UPDATE users SET nv_id=? WHERE id=?", (self.nv_id_current, user_id))
                        conn.commit()
                        print(f"[✓] Tạo NV mới: {ma_nv} - {ho_ten}")
                except Exception as e:
                    print(f"[!] Lỗi tạo NV: {e}")
                    import traceback
                    traceback.print_exc()
                finally:
                    conn.close()  # ✅ FIX: Đóng ở cuối finally
            else:
                conn.close()

        _ensure_table()
        self._sel_nv_id = None
        self._build()
        if self.is_admin:
            self._load_nvs()
        self._load()

    def _build(self):
        root = QVBoxLayout(self); root.setContentsMargins(0,0,0,0); root.setSpacing(0)

        # Header
        hdr = QWidget()
        hdr.setStyleSheet("background:#ffffff;border-bottom:1px solid #e5e7eb;")
        hl = QHBoxLayout(hdr); hl.setContentsMargins(20,14,20,14); hl.setSpacing(12)

        col = QVBoxLayout(); col.setSpacing(2)
        t = QLabel("⏰  Quản lý Chấm công")
        t.setStyleSheet("font-size:17px;font-weight:900;color:#111827;background:transparent;")
        s = QLabel("Theo dõi giờ làm • Lịch tháng • Thưởng phạt • Tính lương")
        s.setStyleSheet("font-size:12px;color:#6b7280;background:transparent;font-weight:600;")
        col.addWidget(t); col.addWidget(s)
        hl.addLayout(col, 1)

        # Đồng hồ realtime
        self.lbl_clock = QLabel()
        self.lbl_clock.setStyleSheet("font-size:22px;font-weight:800;color:#a78bfa;background:transparent;font-family:'Courier New';")
        hl.addWidget(self.lbl_clock)
        root.addWidget(hdr)

        # Toolbar lọc
        tb = QWidget(); tb.setStyleSheet("background:#f9fafb;border-bottom:1px solid #e5e7eb;")
        tbh = QHBoxLayout(tb); tbh.setContentsMargins(16,10,16,10); tbh.setSpacing(10)

        if self.is_admin:
            lbl_nv = QLabel("Nhân viên:")
            lbl_nv.setStyleSheet(
                "color:#1e293b;font-size:13px;font-weight:800;background:transparent;letter-spacing:.5px;text-transform:uppercase;")
            self.sel_nv = QComboBox();
            self.sel_nv.setObjectName("sel_nv")
            self.sel_nv.currentIndexChanged.connect(self._on_nv_change)
            tbh.addWidget(lbl_nv);
            tbh.addWidget(self.sel_nv)

        lbl_th = QLabel("Tháng:");
        lbl_th.setStyleSheet(
            "color:#1e293b;font-size:13px;font-weight:800;background:transparent;letter-spacing:.5px;text-transform:uppercase;")
        self.sel_thang = QComboBox();
        self.sel_thang.setObjectName("sel_thang")
        for i in range(1, 13): self.sel_thang.addItem(f"Tháng {i}", i)
        self.sel_thang.setCurrentIndex(datetime.now().month - 1)

        lbl_nam = QLabel("Năm:");
        lbl_nam.setStyleSheet(
            "color:#1e293b;font-size:13px;font-weight:800;background:transparent;letter-spacing:.5px;text-transform:uppercase;")
        self.sel_nam = QComboBox();
        self.sel_nam.setObjectName("sel_nam")
        for y in range(2023, 2028): self.sel_nam.addItem(str(y), y)
        self.sel_nam.setCurrentText(str(datetime.now().year))

        self.sel_thang.currentIndexChanged.connect(self._load)
        self.sel_nam.currentIndexChanged.connect(self._load)

        tbh.addWidget(lbl_th); tbh.addWidget(self.sel_thang)
        tbh.addWidget(lbl_nam); tbh.addWidget(self.sel_nam)
        tbh.addStretch()

        btn_xl = QPushButton("📊 Xuất Excel")
        btn_xl.setObjectName("btn_excel")
        btn_xl.setStyleSheet("""
                    QPushButton {
                        background: #fed7aa;
                        color: #b45309;
                        border: 2px solid #fdba74;
                        border-radius: 8px;
                        font-size: 13px;
                        font-weight: 800;
                        padding: 10px 18px;
                        letter-spacing: 0.5px;
                    }
                    QPushButton:hover {
                        background: #fecdd3;
                        border: 2px solid #fb923c;
                    }
                    QPushButton:pressed {
                        background: #fdba74;
                    }
                """)
        btn_xl.clicked.connect(self._export)
        tbh.addWidget(btn_xl)
        root.addWidget(tb)

        # Stats bar
        self.stats_w = QWidget()
        self.stats_w.setStyleSheet("background:#ffffff;border-bottom:1px solid #e5e7eb;padding:14px 16px 12px;")
        sl = QHBoxLayout(self.stats_w);
        sl.setContentsMargins(0, 0, 0, 0);
        sl.setSpacing(12)
        self._stat_lbls = {}
        for key, icon, label, color in [
            ("di_lam", "✅", "Đi làm", "#16a34a"),
            ("di_muon", "⏰", "Đi muộn", "#d97706"),
            ("vang", "❌", "Vắng mặt", "#dc2626"),
            ("nghi_phep", "🌴", "Nghỉ phép", "#2563eb"),
            ("nua_buoi", "⚡", "Nửa buổi", "#7c3aed"),
            ("luong", "💰", "Lương TT", "#16a34a"),
        ]:
            card = QWidget()
            card.setStyleSheet(
                f"background:#f9fafb;border:1px solid #e5e7eb;border-radius:12px;border-left:4px solid {color};")
            cl = QVBoxLayout(card);
            cl.setContentsMargins(14, 10, 14, 10);
            cl.setSpacing(3)
            lv = QLabel("—");
            lv.setStyleSheet(f"font-size:20px;font-weight:900;color:{color};background:transparent;")
            ll = QLabel(f"{icon} {label}");
            ll.setStyleSheet(
                f"font-size:12px;color:{color};background:transparent;font-weight:800;letter-spacing:.5px;")
            cl.addWidget(lv);
            cl.addWidget(ll)
            sl.addWidget(card, 1)
            self._stat_lbls[key] = lv
        root.addWidget(self.stats_w)

        # Main content — Tab
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
                    QTabWidget::pane { border: none; background: #ffffff; }
                    QTabBar::tab {
                        background: #f3f4f6; color: #6b7280;
                        padding: 10px 22px; font-size: 13px; font-weight: 700;
                        border: none; border-bottom: 2px solid transparent;
                    }
                    QTabBar::tab:selected { color: #2563eb; border-bottom: 2px solid #2563eb; background: #ffffff; }
                    QTabBar::tab:hover { color: #1e293b; background: #f9fafb; }
                """)

        # Tab 1: Chấm công hôm nay
        tab1 = self._build_tab_homnay()
        self.tabs.addTab(tab1, "⏰  Chấm công hôm nay")

        # Tab 2: Lịch tháng
        tab2 = self._build_tab_lich()
        self.tabs.addTab(tab2, "📅  Lịch tháng")

        # Tab 3: Bảng chấm công chi tiết
        tab3 = self._build_tab_bang()
        self.tabs.addTab(tab3, "📋  Bảng chấm công")

        # Tab 4: Lương (Admin only)
        if self.is_admin:
            tab4 = self._build_tab_luong()
            self.tabs.addTab(tab4, "💰  Tính lương")

        root.addWidget(self.tabs, 1)

        # Timer đồng hồ
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(1000)

    def _build_tab_homnay(self):
        w = QWidget(); w.setStyleSheet("background:#ffffff;")
        lv = QVBoxLayout(w); lv.setContentsMargins(20,20,20,20); lv.setSpacing(16)

        # Card chấm công lớn
        card = QWidget()
        card.setStyleSheet("background:#f9fafb;border:1px solid #e5e7eb;border-radius:16px;")
        cl = QVBoxLayout(card); cl.setContentsMargins(30,24,30,24); cl.setSpacing(14)

        # Ngày hôm nay
        today = datetime.now()
        ngay_lbl = QLabel(f"📅  {today.strftime('%A, %d/%m/%Y')}")
        ngay_lbl.setStyleSheet("font-size:17px;font-weight:900;color:#2563eb;background:transparent;")
        ngay_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(ngay_lbl)

        sep = QFrame();
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background:#e5e7eb;max-height:1px;")
        cl.addWidget(sep)

        # Trạng thái hôm nay
        self.lbl_tt_homnay = QLabel("📋  Chưa chấm công")
        self.lbl_tt_homnay.setStyleSheet("font-size:15px;color:#1e293b;background:transparent;font-weight:800;")
        self.lbl_tt_homnay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(self.lbl_tt_homnay)

        self.lbl_gio_vao = QLabel("Giờ vào: —")
        self.lbl_gio_vao.setStyleSheet("font-size:14px;color:#2563eb;background:transparent;font-weight:700;")
        self.lbl_gio_vao.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(self.lbl_gio_vao)

        self.lbl_gio_ra = QLabel("Giờ ra: —")
        self.lbl_gio_ra.setStyleSheet("font-size:14px;color:#16a34a;background:transparent;font-weight:700;")
        self.lbl_gio_ra.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(self.lbl_gio_ra)

        # Buttons
        # ✅ MỚI - chỉ 1 nút chấm công bằng khuôn mặt
        btn_row = QHBoxLayout();
        btn_row.setSpacing(12)
        self.btn_face = QPushButton("🎥  Chấm công bằng khuôn mặt")
        self.btn_face.setObjectName("btn_cc")
        self.btn_face.setFixedHeight(64)
        self.btn_face.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #059669, stop:1 #7c3aed);
                color: white; border: none; border-radius: 14px;
                font-size: 15px; font-weight: 800; padding: 14px 28px;
            }
            QPushButton:hover { background: #10b981; }
            QPushButton:disabled { background: #1a2a1a; color: #64748b; }
        """)
        self.btn_face.clicked.connect(self._cham_cong_face)
        btn_row.addWidget(self.btn_face, 1)
        cl.addLayout(btn_row)

        # Ghi chú
        self.lbl_ghichu = QLabel("")
        self.lbl_ghichu.setStyleSheet("font-size:12px;color:#4a5568;background:transparent;")
        self.lbl_ghichu.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_ghichu.setWordWrap(True)
        cl.addWidget(self.lbl_ghichu)

        lv.addWidget(card)

        # Thông tin quy định
        info = QWidget()
        info.setStyleSheet("background:#eff6ff;border:1px solid #bfdbfe;border-radius:12px;")
        il = QHBoxLayout(info); il.setContentsMargins(20,14,20,14); il.setSpacing(20)
        for txt, color in [
            ("⏰  Giờ vào: 08:00", "#60a5fa"),
            ("🚨  Muộn sau: 08:15 (phạt 50k)", "#fbbf24"),
            ("🏁  Giờ ra: 17:30", "#4ade80"),
            ("⚠️  Về sớm: trước 17:00 (phạt 50k)", "#f97316"),
        ]:
            l = QLabel(txt); l.setStyleSheet(f"color:{color};font-size:12px;background:transparent;font-weight:600;")
            il.addWidget(l)
        il.addStretch()
        lv.addWidget(info)
        lv.addStretch()
        return w

    def _build_tab_lich(self):
        w = QWidget(); w.setStyleSheet("background:#ffffff;")
        lv = QVBoxLayout(w); lv.setContentsMargins(16,16,16,16); lv.setSpacing(10)

        # Grid lịch
        self.cal_grid = QGridLayout(); self.cal_grid.setSpacing(4)
        lv.addLayout(self.cal_grid)

        # Chú thích
        legend_w = QWidget()
        legend_w.setStyleSheet("""
                    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                        stop:0 #ffffff, stop:1 #f9fafb);
                    border: 1px solid #e5e7eb;
                    border-radius: 12px;
                    padding: 10px;
                """)
        ll = QHBoxLayout(legend_w);
        ll.setContentsMargins(14, 8, 14, 8);
        ll.setSpacing(16)

        legend_colors = {
            "Đúng giờ": "#10b981",
            "Đi muộn": "#f97316",
            "Về sớm": "#ef4444",
            "Vắng mặt": "#dc2626",
            "Nửa buổi": "#a78bfa",
            "Nghỉ phép": "#3b82f6",
        }

        for tt, color in legend_colors.items():
            lbl = QLabel(f"{TT_ICON.get(tt, '')} {tt}")
            lbl.setStyleSheet(f"color:{color};font-size:12px;font-weight:700;background:transparent;")
            ll.addWidget(lbl)
        ll.addStretch()
        lv.addWidget(legend_w)
        return w

    def _build_tab_bang(self):
        w = QWidget();
        w.setStyleSheet("background:#ffffff;")
        lv = QVBoxLayout(w);
        lv.setContentsMargins(0, 0, 0, 0);
        lv.setSpacing(0)

        # Toolbar - TRẮNG
        tb = QWidget();
        tb.setStyleSheet("background:#ffffff;border-bottom:2px solid #e5e7eb;padding:12px 16px;")
        tbh = QHBoxLayout(tb);
        tbh.setContentsMargins(0, 0, 0, 0);
        tbh.setSpacing(10)

        btn_them = QPushButton("➕ Thêm thủ công")
        btn_them.setObjectName("btn_edit")
        btn_them.setStyleSheet("""
            QPushButton {
                background: #dbeafe;
                color: #0284c7;
                border: 1px solid #93c5fd;
                border-radius: 8px;
                padding: 8px 14px;
                font-size: 12px;
                font-weight: 700;
            }
            QPushButton:hover { background: #bfdbfe; }
        """)
        btn_them.clicked.connect(self._them_thu_cong)

        btn_sua = QPushButton("✏️ Sửa")
        btn_sua.setObjectName("btn_edit")
        btn_sua.setStyleSheet("""
            QPushButton {
                background: #fed7aa;
                color: #b45309;
                border: 1px solid #fdba74;
                border-radius: 8px;
                padding: 8px 14px;
                font-size: 12px;
                font-weight: 700;
            }
            QPushButton:hover { background: #fecdd3; }
        """)
        btn_sua.clicked.connect(self._sua_cc)

        btn_xoa = QPushButton("🗑 Xóa")
        btn_xoa.setObjectName("btn_del")
        btn_xoa.setStyleSheet("""
            QPushButton {
                background: #fee2e2;
                color: #991b1b;
                border: 1px solid #fca5a5;
                border-radius: 8px;
                padding: 8px 14px;
                font-size: 12px;
                font-weight: 700;
            }
            QPushButton:hover { background: #fecaca; }
        """)
        btn_xoa.clicked.connect(self._xoa_cc)

        tbh.addWidget(btn_them);
        tbh.addWidget(btn_sua);
        tbh.addWidget(btn_xoa)
        tbh.addStretch()
        lv.addWidget(tb)

        # Table - TRẮNG
        cols = ["NGÀY", "THỨ", "GIỜ VÀO", "GIỜ RA", "TRẠNG THÁI", "PHẠT", "THƯỞNG", "GHI CHÚ"]
        self.tbl_cc = QTableWidget(0, len(cols))
        self.tbl_cc.setHorizontalHeaderLabels(cols)
        self.tbl_cc.setAlternatingRowColors(True)
        self.tbl_cc.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tbl_cc.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl_cc.setShowGrid(False)
        self.tbl_cc.verticalHeader().setVisible(False)

        # ✅ STYLE TABLE TRẮNG
        self.tbl_cc.setStyleSheet("""
            QTableWidget {
                background: #ffffff;
                alternate-background-color: #f9fafb;
                gridline-color: #e5e7eb;
                border: none;
            }
            QTableWidget::item {
                padding: 10px 12px;
                color: #1e293b;
                border-bottom: 1px solid #e5e7eb;
            }
            QTableWidget::item:selected {
                background: #eff6ff;
                color: #0284c7;
            }
            QHeaderView::section {
                background: #f8fafc;
                color: #2563eb;
                font-size: 12px;
                font-weight: 900;
                letter-spacing: 1px;
                padding: 12px;
                border: none;
                border-bottom: 2px solid #2563eb;
            }
        """)

        h = self.tbl_cc.horizontalHeader()
        h.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # NGÀY
        h.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # THỨ
        h.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # GIỜ VÀO
        h.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # GIỜ RA
        h.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # TRẠNG THÁI
        h.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # PHẠT
        h.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # THƯỞNG
        h.setSectionResizeMode(7, QHeaderView.ResizeMode.Stretch)  # GHI CHÚ

        self.tbl_cc.selectionModel().selectionChanged.connect(self._on_cc_sel)
        lv.addWidget(self.tbl_cc, 1)
        return w

    def _build_tab_luong(self):
        w = QWidget(); w.setStyleSheet("background:#ffffff;")
        lv = QVBoxLayout(w); lv.setContentsMargins(16,16,16,16); lv.setSpacing(12)

        title = QLabel("💰  Tính lương theo ngày công")
        title.setStyleSheet(
            "font-size:16px;font-weight:800;color:#0f172a;"
            "background:transparent;padding:8px 0 4px;"
        )
        lv.addWidget(title)

        cols = ["NHÂN VIÊN", "CHỨC VỤ", "LƯƠNG CB", "NGÀY CÔNG", "THỰC NHẬN CB",
                "TỔNG THƯỞNG", "TỔNG PHẠT", "THỰC LĨNH"]
        self.tbl_luong = QTableWidget(0, len(cols))
        self.tbl_luong.setHorizontalHeaderLabels(cols)
        self.tbl_luong.setAlternatingRowColors(True)
        self.tbl_luong.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl_luong.setShowGrid(False)
        self.tbl_luong.verticalHeader().setVisible(False)
        h2 = self.tbl_luong.horizontalHeader()
        h2.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        lv.addWidget(self.tbl_luong, 1)

        btn_xl = QPushButton("📊 Xuất Excel bảng lương"); btn_xl.setObjectName("btn_excel")
        btn_xl.clicked.connect(self._export_luong)
        lv.addWidget(btn_xl)
        return w

    # ── Load data ─────────────────────────────────────────────

    def _load_nvs(self):
        if not self.is_admin: return
        conn = get_conn()
        nvs = conn.execute("SELECT id, ho_ten, ma_nv FROM nhan_vien WHERE trang_thai != 'Nghỉ việc' ORDER BY ho_ten").fetchall()
        conn.close()
        self.sel_nv.clear()
        self.sel_nv.addItem("-- Tất cả --", None)
        for nv in nvs:
            self.sel_nv.addItem(f"{nv[2]} - {nv[1]}", nv[0])
        # Mặc định chọn NV đầu tiên
        if nvs:
            self.sel_nv.setCurrentIndex(1)

    def _on_nv_change(self):
        if hasattr(self, 'sel_nv'):
            self._sel_nv_id = self.sel_nv.currentData()
        self._load()

    def _get_nv_id(self):
        if self.is_admin:
            return self._sel_nv_id
        return self.nv_id_current

    def _load(self):
        thang = self.sel_thang.currentData()
        nam   = self.sel_nam.currentData()
        nv_id = self._get_nv_id()
        self._load_homnay(nv_id)
        self._load_lich(nv_id, thang, nam)
        self._load_bang(nv_id, thang, nam)
        self._load_stats(nv_id, thang, nam)
        if self.is_admin:
            self._load_luong(thang, nam)

    def _load_homnay(self, nv_id):
        if not nv_id: return
        today = date.today().strftime("%Y-%m-%d")
        conn = get_conn()
        row = conn.execute(
            "SELECT gio_vao, gio_ra, trang_thai, ghi_chu FROM cham_cong WHERE nv_id=? AND ngay=?",
            (nv_id, today)
        ).fetchone()
        conn.close()

        if row:
            gv, gr, tt, gc = row
            self.lbl_gio_vao.setText(f"Giờ vào: {gv or '—'}")
            self.lbl_gio_ra.setText(f"Giờ ra: {gr or '—'}")
            color = TT_COLOR.get(tt, "#94a3b8")
            icon = TT_ICON.get(tt, "")
            self.lbl_tt_homnay.setText(f"{icon}  {tt}")
            self.lbl_tt_homnay.setStyleSheet(f"font-size:15px;color:{color};background:transparent;font-weight:700;")
            self.lbl_ghichu.setText(gc or "")

            # ✅ Cập nhật nút — nằm TRONG if row
            if gv and gr:
                self.btn_face.setEnabled(False)
                self.btn_face.setText("✅ Đã chấm công xong hôm nay")
                self.btn_face.setStyleSheet("""
                    QPushButton {
                        background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                            stop:0 #10b981, stop:0.5 #34d399, stop:1 #6ee7b7);
                        color: white; 
                        border: none; 
                        border-radius: 14px;
                        font-size: 15px; 
                        font-weight: 800; 
                        padding: 14px 28px;
                        letter-spacing: 0.5px;
                    }
                    QPushButton:disabled { 
                        background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                            stop:0 #059669, stop:0.5 #10b981, stop:1 #34d399);
                        color: white;
                        border: 2px solid #10b981;
                    }
                """)
            elif gv:
                self.btn_face.setEnabled(True)
                self.btn_face.setText("🎥 Chấm công RA (quét khuôn mặt)")
            else:
                self.btn_face.setEnabled(True)
                self.btn_face.setText("🎥 Chấm công VÀO (quét khuôn mặt)")

        else:
            # ✅ Chưa có dữ liệu hôm nay
            self.lbl_tt_homnay.setText("📋  Chưa chấm công hôm nay")
            self.lbl_tt_homnay.setStyleSheet("font-size:14px;color:#64748b;background:transparent;font-weight:600;")
            self.lbl_gio_vao.setText("Giờ vào: —")
            self.lbl_gio_ra.setText("Giờ ra: —")
            self.lbl_ghichu.setText("")
            self.btn_face.setEnabled(True)
            self.btn_face.setText("🎥 Chấm công VÀO (quét khuôn mặt)")

    def _load_lich(self, nv_id, thang, nam):
        # Xóa grid cũ
        while self.cal_grid.count():
            item = self.cal_grid.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        # Header ngày trong tuần
        thu_names = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"]
        for i, thu in enumerate(thu_names):
            lbl = QLabel(thu)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            color = "#dc2626" if thu == "CN" else "#64748b"
            lbl.setStyleSheet(f"color:{color};font-size:13px;font-weight:900;background:transparent;padding:8px;")
            self.cal_grid.addWidget(lbl, 0, i)

        if not nv_id:
            return

        # Lấy dữ liệu chấm công tháng
        conn = get_conn()
        rows = conn.execute(
            "SELECT ngay, gio_vao, gio_ra, trang_thai FROM cham_cong WHERE nv_id=? AND strftime('%Y-%m', ngay)=?",
            (nv_id, f"{nam}-{thang:02d}")
        ).fetchall()
        conn.close()
        cc_map = {r[0]: r for r in rows}

        # Tạo lịch
        first_day = date(nam, thang, 1)
        weekday_start = first_day.weekday()
        days_in_month = calendar.monthrange(nam, thang)[1]
        today = date.today()

        row_idx = 1
        col_idx = weekday_start

        for day in range(1, days_in_month + 1):
            d = date(nam, thang, day)
            d_str = d.strftime("%Y-%m-%d")
            weekday = d.weekday()

            cc = cc_map.get(d_str)
            is_today = (d == today)
            is_future = (d > today)
            is_weekend = weekday >= 5

            # Tạo cell
            cell = QWidget()
            cell_lv = QVBoxLayout(cell);
            cell_lv.setContentsMargins(10, 8, 10, 8);
            cell_lv.setSpacing(5)

            # ✅ PHỐI MÀU MỚI - ĐƠNGIẢN, CHUYÊNNGHI
            if is_today:
                # Hôm nay - Xanh dương đậm với bg nhạt
                bg = """
                    background: #eff6ff;
                    border: 2px solid #0284c7;
                    border-radius: 10px;
                """
                day_color = "#0284c7"
            elif is_weekend:
                # Cuối tuần - Xám nhạt
                bg = """
                    background: #f3f4f6;
                    border: 1px solid #d1d5db;
                    border-radius: 10px;
                """
                day_color = "#6b7280"
            elif is_future:
                # Tương lai - Trắng
                bg = """
                    background: #ffffff;
                    border: 1px solid #e5e7eb;
                    border-radius: 10px;
                """
                day_color = "#9ca3af"
            elif cc:
                color_key = cc[3] if cc else "Đúng giờ"
                # Màu theo trạng thái - ĐƠNGIẢN
                bg_map = {
                    "Đúng giờ": ("background:#dcfce7;border:1px solid #86efac;", "#15803d"),
                    "Đi muộn": ("background:#fef3c7;border:1px solid #fcd34d;", "#a16207"),
                    "Về sớm": ("background:#fecdd3;border:1px solid #f87171;", "#be123c"),
                    "Vắng mặt": ("background:#fee2e2;border:1px solid #fca5a5;", "#991b1b"),
                    "Nửa buổi": ("background:#ede9fe;border:1px solid #d8b4fe;", "#6b21a8"),
                    "Nghỉ phép": ("background:#dbeafe;border:1px solid #93c5fd;", "#1e40af"),
                }
                style_info = bg_map.get(color_key, ("background:#f9fafb;border:1px solid #e5e7eb;", "#1f2937"))
                bg = style_info[0] + "border-radius:10px;"
                day_color = style_info[1]
            else:
                # Chưa chấm công - Cam nhạt
                bg = """
                    background: #fed7aa;
                    border: 1px dashed #fb923c;
                    border-radius: 10px;
                """
                day_color = "#b45309"

            cell.setStyleSheet(bg)
            cell.setFixedHeight(95)

            # Số ngày - RỰC RỠ
            day_lbl = QLabel(str(day))
            day_lbl.setStyleSheet(f"color:{day_color};font-size:18px;font-weight:900;background:transparent;")
            day_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cell_lv.addWidget(day_lbl)

            if cc and not is_weekend:
                tt = cc[3] or "Đúng giờ"
                icon = TT_ICON.get(tt, "")
                color = TT_COLOR.get(tt, "#94a3b8")

                # Trạng thái - ĐẬM, RỰC
                tt_lbl = QLabel(f"{icon} {tt}")
                tt_lbl.setStyleSheet(f"color:{color};font-size:11px;font-weight:800;background:transparent;")
                tt_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                tt_lbl.setWordWrap(True)
                cell_lv.addWidget(tt_lbl)

                # Giờ nhỏ gọn
                if cc[1]:
                    gv_lbl = QLabel(f"⏰ {cc[1]}")
                    gv_lbl.setStyleSheet("color:#0284c7;font-size:9px;font-weight:600;background:transparent;")
                    gv_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    cell_lv.addWidget(gv_lbl)
            elif not is_weekend and not is_future:
                vang_lbl = QLabel("Vắng")
                vang_lbl.setStyleSheet("color:#dc2626;font-size:10px;font-weight:800;background:transparent;")
                vang_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                cell_lv.addWidget(vang_lbl)

            cell_lv.addStretch()
            self.cal_grid.addWidget(cell, row_idx, col_idx)

            col_idx += 1
            if col_idx > 6:
                col_idx = 0;
                row_idx += 1

    def _load_bang(self, nv_id, thang, nam):
        self.tbl_cc.setRowCount(0)
        if not nv_id: return

        conn = get_conn()
        rows = conn.execute("""
            SELECT id, ngay, gio_vao, gio_ra, trang_thai, phat, thuong, ghi_chu
            FROM cham_cong WHERE nv_id=? AND strftime('%Y-%m', ngay)=?
            ORDER BY ngay DESC
        """, (nv_id, f"{nam}-{thang:02d}")).fetchall()
        conn.close()

        thu_map = {0: "Thứ 2", 1: "Thứ 3", 2: "Thứ 4", 3: "Thứ 5", 4: "Thứ 6", 5: "Thứ 7", 6: "Chủ nhật"}

        for row in rows:
            r = self.tbl_cc.rowCount();
            self.tbl_cc.insertRow(r)
            self.tbl_cc.setRowHeight(r, 45)

            try:
                d = datetime.strptime(row[1], "%Y-%m-%d")
                thu = thu_map[d.weekday()]
                ngay_fmt = d.strftime("%d/%m/%Y")
            except Exception:
                ngay_fmt = row[1];
                thu = ""

            tt = row[4] or "—"
            color = TT_COLOR.get(tt, "#94a3b8")
            icon = TT_ICON.get(tt, "")
            phat = float(row[5] or 0)
            thuong = float(row[6] or 0)

            vals = [
                ngay_fmt, thu,
                row[2] or "—", row[3] or "—",
                f"{icon} {tt}",
                f"-{phat / 1000:.0f}k" if phat > 0 else "—",
                f"+{thuong / 1000:.0f}k" if thuong > 0 else "—",
                row[7] or ""
            ]

            for c, val in enumerate(vals):
                item = QTableWidgetItem(val)
                item.setData(Qt.ItemDataRole.UserRole, row[0])

                # ✅ FONT CHUNG: ĐẬM, TO
                item.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
                item.setForeground(QColor("#1e293b"))

                # Phối màu theo cột
                if c == 4:  # TRẠNG THÁI
                    item.setForeground(QColor(color))
                    item.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
                elif c == 5 and phat > 0:  # PHẠT
                    item.setForeground(QColor("#dc2626"))
                    item.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
                elif c == 6 and thuong > 0:  # THƯỞNG
                    item.setForeground(QColor("#16a34a"))
                    item.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
                elif c in [0, 1]:  # NGÀY, THỨ
                    item.setForeground(QColor("#0284c7"))
                    item.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))

                self.tbl_cc.setItem(r, c, item)

    def _load_stats(self, nv_id, thang, nam):
        if not nv_id:
            for k in self._stat_lbls: self._stat_lbls[k].setText("—")
            return

        conn = get_conn()
        rows = conn.execute("""
            SELECT trang_thai, phat, thuong FROM cham_cong
            WHERE nv_id=? AND strftime('%Y-%m', ngay)=?
        """, (nv_id, f"{nam}-{thang:02d}")).fetchall()

        nv = conn.execute("SELECT luong FROM nhan_vien WHERE id=?", (nv_id,)).fetchone()
        conn.close()

        luong_cb = float(nv[0] or 0) if nv else 0
        days_in_month = calendar.monthrange(nam, thang)[1]
        working_days = sum(1 for d in range(1, days_in_month+1)
                          if date(nam, thang, d).weekday() < 5)

        di_lam = sum(1 for r in rows if r[0] not in ["Vắng mặt"])
        di_muon = sum(1 for r in rows if r[0] == "Đi muộn")
        vang    = sum(1 for r in rows if r[0] == "Vắng mặt")
        nghi_phep = sum(1 for r in rows if r[0] == "Nghỉ phép")
        nua_buoi  = sum(1 for r in rows if r[0] == "Nửa buổi")
        tong_phat  = sum(float(r[1] or 0) for r in rows)
        tong_thuong= sum(float(r[2] or 0) for r in rows)

        # Tính lương
        if working_days > 0:
            luong_thuc = (luong_cb / working_days) * di_lam
        else:
            luong_thuc = 0
        luong_thuc = luong_thuc - tong_phat + tong_thuong

        # Thưởng chuyên cần
        if vang == 0 and di_muon == 0:
            luong_thuc += THUONG_CC_DAY
            tong_thuong += THUONG_CC_DAY

        self._stat_lbls["di_lam"].setText(f"{di_lam}/{working_days}")
        self._stat_lbls["di_muon"].setText(str(di_muon))
        self._stat_lbls["vang"].setText(str(vang))
        self._stat_lbls["nghi_phep"].setText(str(nghi_phep))
        self._stat_lbls["nua_buoi"].setText(str(nua_buoi))
        self._stat_lbls["luong"].setText(f"{luong_thuc/1e6:.1f}tr")

    def _load_luong(self, thang, nam):
        self.tbl_luong.setRowCount(0)
        conn = get_conn()
        nvs = conn.execute(
            "SELECT id, ho_ten, chuc_vu, luong FROM nhan_vien WHERE trang_thai != 'Nghỉ việc'"
        ).fetchall()

        days_in_month = calendar.monthrange(nam, thang)[1]
        working_days = sum(1 for d in range(1, days_in_month+1)
                          if date(nam, thang, d).weekday() < 5)

        for nv in nvs:
            nv_id = nv[0]
            luong_cb = float(nv[3] or 0)

            rows = conn.execute("""
                SELECT trang_thai, phat, thuong FROM cham_cong
                WHERE nv_id=? AND strftime('%Y-%m', ngay)=?
            """, (nv_id, f"{nam}-{thang:02d}")).fetchall()

            di_lam = sum(1 for r in rows if r[0] not in ["Vắng mặt"])
            tong_phat   = sum(float(r[1] or 0) for r in rows)
            tong_thuong = sum(float(r[2] or 0) for r in rows)
            vang    = sum(1 for r in rows if r[0] == "Vắng mặt")
            di_muon = sum(1 for r in rows if r[0] == "Đi muộn")

            if working_days > 0:
                luong_thuc_cb = (luong_cb / working_days) * di_lam
            else:
                luong_thuc_cb = 0

            if vang == 0 and di_muon == 0:
                tong_thuong += THUONG_CC_DAY

            thuc_linh = luong_thuc_cb - tong_phat + tong_thuong

            r = self.tbl_luong.rowCount(); self.tbl_luong.insertRow(r)
            self.tbl_luong.setRowHeight(r, 52)  # ← tăng từ 44 lên 52

            mau_tl = "#059669" if thuc_linh >= 0 else "#dc2626"  # ← thêm dòng này

            for c, (val, color) in enumerate([
                (nv[1], "#0f172a"),  # Tên NV — đen đậm
                (nv[2], "#475569"),  # Chức vụ — xám đậm
                (f"{luong_cb / 1e6:.1f}tr", "#7c3aed"),  # Lương CB — tím đậm
                (f"{di_lam}/{working_days}", "#1d4ed8"),  # Ngày công — xanh đậm
                (f"{luong_thuc_cb / 1e6:.1f}tr", "#1d4ed8"),  # Thực nhận — xanh đậm
                (f"+{tong_thuong / 1e3:.0f}k" if tong_thuong > 0 else "—", "#059669"),  # Thưởng — xanh lá đậm
                (f"-{tong_phat / 1e3:.0f}k" if tong_phat > 0 else "—", "#dc2626"),  # Phạt — đỏ đậm
                (f"{thuc_linh / 1e6:.2f}tr", mau_tl),  # Thực lĩnh — xanh/đỏ tùy âm dương
            ]):
                item = QTableWidgetItem(val)
                item.setForeground(QColor(color))
                if c == 0:
                    item.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))  # Tên NV — to nhất
                elif c == 1:
                    item.setFont(QFont("Segoe UI", 12))  # Chức vụ — bình thường
                else:
                    item.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))  # Tất cả số liệu — đậm to
                if c == 7:  # Thực lĩnh — to nhất, nổi bật nhất
                    item.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
                self.tbl_luong.setItem(r, c, item)

        conn.close()

    # ── Chấm công ─────────────────────────────────────────────

    def _cham_vao(self):
        nv_id = self._get_nv_id()
        if not nv_id:
            QMessageBox.warning(self, "", "Không xác định được nhân viên!"); return

        today = date.today().strftime("%Y-%m-%d")
        now   = datetime.now().strftime("%H:%M")

        # Tính trạng thái
        gv = QTime.fromString(now, "HH:mm")
        if gv > GIO_VAO_MUON:
            tt   = "Đi muộn"
            phat = PHAT_DI_MUON
            msg  = f"⏰ Đi muộn! Phạt {PHAT_DI_MUON:,} ₫"
        else:
            tt   = "Đúng giờ"
            phat = 0
            msg  = "✅ Đúng giờ! Chấm công thành công."

        conn = get_conn()
        conn.execute("""
            INSERT INTO cham_cong(nv_id, ngay, gio_vao, trang_thai, phat, ghi_chu)
            VALUES(?,?,?,?,?,?)
        """, (nv_id, today, now, tt, phat, msg))
        conn.commit(); conn.close()

        QMessageBox.information(self, "✅ Chấm công VÀO", f"Giờ vào: {now}\n{msg}")
        self._load()

    def _cham_ra(self):
        nv_id = self._get_nv_id()
        if not nv_id: return

        today = date.today().strftime("%Y-%m-%d")
        now   = datetime.now().strftime("%H:%M")

        conn = get_conn()
        row = conn.execute(
            "SELECT id, trang_thai, phat FROM cham_cong WHERE nv_id=? AND ngay=?",
            (nv_id, today)
        ).fetchone()

        if not row:
            conn.close(); QMessageBox.warning(self, "", "Chưa chấm công vào!"); return

        # Tính thêm phạt về sớm
        gr = QTime.fromString(now, "HH:mm")
        phat_them = 0
        tt = row[1]
        if gr < GIO_RA_SOM:
            phat_them = PHAT_VE_SOM
            if tt == "Đúng giờ": tt = "Về sớm"
            elif tt == "Đi muộn": tt = "Nửa buổi"
            msg = f"⚠️ Về sớm! Phạt thêm {PHAT_VE_SOM:,} ₫"
        else:
            msg = "✅ Hoàn thành ca làm việc!"

        tong_phat = float(row[2] or 0) + phat_them

        conn.execute("""
            UPDATE cham_cong SET gio_ra=?, trang_thai=?, phat=?, ghi_chu=?
            WHERE id=?
        """, (now, tt, tong_phat, msg, row[0]))
        conn.commit(); conn.close()

        QMessageBox.information(self, "✅ Chấm công RA", f"Giờ ra: {now}\n{msg}")
        self._load()

    # ── CRUD thủ công ─────────────────────────────────────────
    def _cham_cong_face(self):
        """Cham cong bang nhan dien khuon mat"""
        nv_id = self._get_nv_id()
        if not nv_id:
            QMessageBox.warning(self, "", "Không xác định được nhân viên!");
            return

        conn = get_conn()
        nv = conn.execute("SELECT ho_ten FROM nhan_vien WHERE id=?", (nv_id,)).fetchone()
        conn.close()
        ho_ten = nv[0] if nv else ""

        from face_attendance import FaceChamCongDialog, FaceRegisterDialog, has_face_model

        if not has_face_model(nv_id):
            # Chua co khuon mat → hoi dang ky
            reply = QMessageBox.question(self, "Chưa có khuôn mặt",
                                         f"Bạn chưa đăng ký khuôn mặt!\n\nBạn có muốn đăng ký ngay không?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                dlg = FaceRegisterDialog(self, nv_id=nv_id, ho_ten=ho_ten)
                if dlg.exec():
                    QMessageBox.information(self, "✅ OK",
                                            "Đăng ký thành công!\nNhấn lại để chấm công.")
            return

        # Da co khuon mat → mo camera nhan dien
        today = date.today().strftime("%Y-%m-%d")
        conn = get_conn()
        row = conn.execute(
            "SELECT gio_vao, gio_ra FROM cham_cong WHERE nv_id=? AND ngay=?",
            (nv_id, today)).fetchone()
        conn.close()

        gv = row[0] if row else None
        gr = row[1] if row else None

        if gv and gr:
            QMessageBox.information(self, "Đã chấm công",
                                    "Bạn đã chấm công VÀO và RA hôm nay rồi!");
            return

        dlg = FaceChamCongDialog(self, nv_id=nv_id, ho_ten=ho_ten)

        if not gv:
            # Chua vao → cham vao
            dlg.setWindowTitle("🎥 Chấm công VÀO")

            def on_success(nid, name):
                self._cham_vao()

            dlg.cham_cong_success.connect(on_success)
        else:
            # Da vao, chua ra → cham ra
            dlg.setWindowTitle("🎥 Chấm công RA")

            def on_success(nid, name):
                self._cham_ra()

            dlg.cham_cong_success.connect(on_success)

        dlg.exec()


    def _on_cc_sel(self):
        r = self.tbl_cc.currentRow()
        if r >= 0:
            item = self.tbl_cc.item(r, 0)
            if item: self._sel_cc_id = item.data(Qt.ItemDataRole.UserRole)

    def _them_thu_cong(self):
        nv_id = self._get_nv_id()
        if not nv_id:
            QMessageBox.warning(self, "", "Chọn nhân viên trước!"); return
        if ChamCongDialog(self, nv_id=nv_id).exec():
            self._load()

    def _sua_cc(self):
        if not hasattr(self, '_sel_cc_id') or not self._sel_cc_id:
            QMessageBox.warning(self, "", "Chọn dòng cần sửa!"); return
        conn = get_conn()
        row = conn.execute("SELECT * FROM cham_cong WHERE id=?", (self._sel_cc_id,)).fetchone()
        conn.close()
        if row and ChamCongDialog(self, data=dict(row)).exec():
            self._load()

    def _xoa_cc(self):
        if not hasattr(self, '_sel_cc_id') or not self._sel_cc_id:
            QMessageBox.warning(self, "", "Chọn dòng cần xóa!"); return
        if QMessageBox.question(self, "Xác nhận", "Xóa bản ghi chấm công này?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        ) == QMessageBox.StandardButton.Yes:
            conn = get_conn()
            conn.execute("DELETE FROM cham_cong WHERE id=?", (self._sel_cc_id,))
            conn.commit(); conn.close()
            self._sel_cc_id = None
            self._load()

    def _export(self):
        try:
            import pandas as pd
            nv_id = self._get_nv_id()
            thang = self.sel_thang.currentData()
            nam   = self.sel_nam.currentData()
            conn  = get_conn()
            rows  = conn.execute("""
                SELECT cc.ngay, cc.gio_vao, cc.gio_ra, cc.trang_thai,
                       cc.phat, cc.thuong, cc.ghi_chu, nv.ho_ten
                FROM cham_cong cc JOIN nhan_vien nv ON cc.nv_id=nv.id
                WHERE (?  IS NULL OR cc.nv_id=?)
                AND strftime('%Y-%m', cc.ngay)=?
                ORDER BY nv.ho_ten, cc.ngay
            """, (nv_id, nv_id, f"{nam}-{thang:02d}")).fetchall()
            conn.close()
            df = pd.DataFrame([list(r) for r in rows],
                columns=["Ngày","Giờ vào","Giờ ra","Trạng thái","Phạt","Thưởng","Ghi chú","Nhân viên"])
            fname = f"cham_cong_T{thang}_{nam}.xlsx"
            with pd.ExcelWriter(fname, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Chấm công")
                ws = writer.sheets["Chấm công"]
                # Header màu xanh đậm
                from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
                header_fill = PatternFill("solid", fgColor="0F172A")
                header_font = Font(bold=True, color="FFFFFF", size=11)
                thin = Side(style="thin", color="E5E7EB")
                border = Border(left=thin, right=thin, top=thin, bottom=thin)
                for cell in ws[1]:
                    cell.fill = header_fill
                    cell.font = header_font
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                    cell.border = border
                ws.row_dimensions[1].height = 30
                # Màu xen kẽ dòng
                alt_fill = PatternFill("solid", fgColor="EFF6FF")
                tt_colors = {
                    "Đúng giờ": "DCFCE7", "Đi muộn": "FEF3C7",
                    "Vắng mặt": "FEE2E2", "Về sớm": "FECDD3",
                    "Nửa buổi": "EDE9FE", "Nghỉ phép": "DBEAFE",
                }
                for row_idx, row in enumerate(ws.iter_rows(min_row=2), start=2):
                    # Màu theo trạng thái (cột D = index 4)
                    tt_val = ws.cell(row=row_idx, column=4).value or ""
                    row_color = tt_colors.get(tt_val, "FFFFFF")
                    fill = PatternFill("solid", fgColor=row_color)
                    for cell in row:
                        cell.fill = fill
                        cell.border = border
                        cell.alignment = Alignment(vertical="center")
                    ws.row_dimensions[row_idx].height = 22
                # Auto-fit độ rộng cột
                for col in ws.columns:
                    max_len = max((len(str(c.value or "")) for c in col), default=10)
                    ws.column_dimensions[col[0].column_letter].width = max_len + 4
            QMessageBox.information(self, "✅ OK", f"Đã xuất: {fname}")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))

    def _export_luong(self):
        try:
            import pandas as pd
            thang = self.sel_thang.currentData()
            nam   = self.sel_nam.currentData()
            self.tbl_luong.selectAll()
            data = []
            for r in range(self.tbl_luong.rowCount()):
                row_data = [self.tbl_luong.item(r, c).text() if self.tbl_luong.item(r, c) else "" for c in range(self.tbl_luong.columnCount())]
                data.append(row_data)
            cols = ["Nhân viên","Chức vụ","Lương CB","Ngày công","Thực nhận CB","Thưởng","Phạt","Thực lĩnh"]
            df = pd.DataFrame(data, columns=cols)
            fname = f"bang_luong_T{thang}_{nam}.xlsx"
            with pd.ExcelWriter(fname, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Bảng lương")
                ws = writer.sheets["Bảng lương"]
                from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
                header_fill = PatternFill("solid", fgColor="1E3A5F")
                header_font = Font(bold=True, color="FFFFFF", size=11)
                thin = Side(style="thin", color="E5E7EB")
                border = Border(left=thin, right=thin, top=thin, bottom=thin)
                for cell in ws[1]:
                    cell.fill = header_fill
                    cell.font = header_font
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                    cell.border = border
                ws.row_dimensions[1].height = 32
                # Màu xen kẽ + highlight cột Thực lĩnh
                for row_idx, row in enumerate(ws.iter_rows(min_row=2), start=2):
                    bg = "F0F9FF" if row_idx % 2 == 0 else "FFFFFF"
                    fill = PatternFill("solid", fgColor=bg)
                    for cell in row:
                        cell.fill = fill
                        cell.border = border
                        cell.alignment = Alignment(vertical="center", horizontal="right")
                        cell.font = Font(size=11)
                    # Cột A (Tên NV) — căn trái, đậm
                    ws.cell(row=row_idx, column=1).alignment = Alignment(horizontal="left", vertical="center")
                    ws.cell(row=row_idx, column=1).font = Font(bold=True, size=11)
                    # Cột H (Thực lĩnh) — nổi bật
                    cell_tl = ws.cell(row=row_idx, column=8)
                    try:
                        val = float(str(cell_tl.value or "0").replace("tr", "").replace("-", "").strip())
                        tl_raw = str(cell_tl.value or "")
                        color_tl = "059669" if "-" not in tl_raw else "DC2626"
                    except Exception:
                        color_tl = "059669"
                    cell_tl.font = Font(bold=True, color=color_tl, size=12)
                    ws.row_dimensions[row_idx].height = 24
                # Auto-fit
                for col in ws.columns:
                    max_len = max((len(str(c.value or "")) for c in col), default=10)
                    ws.column_dimensions[col[0].column_letter].width = max_len + 6
            QMessageBox.information(self, "✅ OK", f"Đã xuất: {fname}")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))

    def _tick(self):
        self.lbl_clock.setText(datetime.now().strftime("%H:%M:%S"))

    def refresh(self):
        self._load()


# ── Dialog chấm công thủ công ─────────────────────────────────
class ChamCongDialog(QDialog):
    def __init__(self, parent=None, nv_id=None, data=None):
        super().__init__(parent)
        self.nv_id = nv_id or (data.get("nv_id") if data else None)
        self.data = data
        self.setWindowTitle("Chấm công thủ công")
        self.setMinimumWidth(450)
        # ✅ STYLE MỚI - TRẮNG + XANH
        self.setStyleSheet("""
            QDialog {
                background: #ffffff;
            }
            QLabel {
                color: #1e293b;
                font-size: 12px;
                font-weight: 700;
                background: transparent;
                letter-spacing: 0.5px;
                text-transform: uppercase;
            }
            QLineEdit, QTimeEdit, QComboBox, QDoubleSpinBox, QTextEdit {
                background: #f9fafb;
                color: #111827;
                border: 2px solid #e5e7eb;
                border-radius: 8px;
                padding: 10px 12px;
                font-size: 13px;
                font-weight: 600;
            }
            QLineEdit:focus, QTimeEdit:focus, QComboBox:focus, QDoubleSpinBox:focus {
                border: 2px solid #2563eb;
                background: #ffffff;
            }
            QPushButton#save {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #0891b2, stop:1 #06b6d4);
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 800;
                padding: 11px 24px;
                letter-spacing: 0.5px;
            }
            QPushButton#save:hover {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #06b6d4, stop:1 #5eead4);
            }
            QPushButton#cancel {
                background: #f3f4f6;
                color: #6b7280;
                border: 2px solid #d1d5db;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 700;
                padding: 10px 20px;
            }
            QPushButton#cancel:hover {
                background: #e5e7eb;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background: #ffffff;
                color: #1e293b;
                border: 1px solid #e5e7eb;
                selection-background-color: #dbeafe;
                selection-color: #0284c7;
            }
        """)
        self._build()

    def _build(self):
        outer = QVBoxLayout(self);
        outer.setContentsMargins(28, 24, 28, 24);
        outer.setSpacing(16)

        # Title - XÃ BLUE
        title = QLabel("⏰  CHẤM CÔNG THỦ CÔNG")
        title.setStyleSheet("font-size:16px;font-weight:900;color:#0284c7;background:transparent;letter-spacing:1px;")
        outer.addWidget(title)

        # Separator
        sep = QFrame();
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background:#e5e7eb;max-height:2px;border-radius:1px;")
        outer.addWidget(sep)

        form = QFormLayout();
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        def lbl(t, color="#0284c7"):
            l = QLabel(t)
            l.setStyleSheet(f"color:{color};font-size:12px;font-weight:800;background:transparent;letter-spacing:.8px;")
            return l

        # Input fields
        self.f_ngay = QLineEdit()
        self.f_ngay.setPlaceholderText("YYYY-MM-DD")
        self.f_ngay.setText(self.data.get("ngay", "") if self.data else date.today().strftime("%Y-%m-%d"))

        self.f_vao = QTimeEdit();
        self.f_vao.setDisplayFormat("HH:mm")
        self.f_vao.setTime(QTime(8, 0))

        self.f_ra = QTimeEdit();
        self.f_ra.setDisplayFormat("HH:mm")
        self.f_ra.setTime(QTime(17, 30))

        self.f_tt = QComboBox()
        self.f_tt.addItems(["Đúng giờ", "Đi muộn", "Về sớm", "Vắng mặt", "Nửa buổi", "Nghỉ phép", "Ngày lễ"])

        self.f_phat = QDoubleSpinBox();
        self.f_phat.setRange(0, 10e6);
        self.f_phat.setSingleStep(50000);
        self.f_phat.setSuffix(" ₫")
        self.f_thuong = QDoubleSpinBox();
        self.f_thuong.setRange(0, 10e6);
        self.f_thuong.setSingleStep(50000);
        self.f_thuong.setSuffix(" ₫")
        self.f_gc = QTextEdit();
        self.f_gc.setMaximumHeight(70);
        self.f_gc.setPlaceholderText("Ghi chú...")

        if self.data:
            if self.data.get("gio_vao"): self.f_vao.setTime(QTime.fromString(self.data["gio_vao"], "HH:mm"))
            if self.data.get("gio_ra"):  self.f_ra.setTime(QTime.fromString(self.data["gio_ra"], "HH:mm"))
            idx = self.f_tt.findText(self.data.get("trang_thai", "Đúng giờ"))
            if idx >= 0: self.f_tt.setCurrentIndex(idx)
            self.f_phat.setValue(float(self.data.get("phat", 0) or 0))
            self.f_thuong.setValue(float(self.data.get("thuong", 0) or 0))
            self.f_gc.setPlainText(self.data.get("ghi_chu", "") or "")

        self.f_tt.currentTextChanged.connect(self._auto_phat)

        # Phối màu label
        colors = ["#0284c7", "#d97706", "#059669", "#dc2626", "#9333ea", "#059669", "#6b7280"]
        labels = ["NGÀY *", "GIỜ VÀO", "GIỜ RA", "TRẠNG THÁI", "PHẠT", "THƯỞNG", "GHI CHÚ"]
        fields = [self.f_ngay, self.f_vao, self.f_ra, self.f_tt, self.f_phat, self.f_thuong, self.f_gc]

        for (lbl_txt, color), fld in zip(zip(labels, colors), fields):
            form.addRow(lbl(lbl_txt, color), fld)

        outer.addLayout(form)

        # Buttons
        bh = QHBoxLayout();
        bh.addStretch()
        bc = QPushButton("Huỷ bỏ");
        bc.setObjectName("cancel");
        bc.clicked.connect(self.reject)
        bs = QPushButton("💾  Lưu");
        bs.setObjectName("save");
        bs.clicked.connect(self._save);
        bs.setDefault(True)
        bh.addWidget(bc);
        bh.addWidget(bs)
        outer.addLayout(bh)

    def _auto_phat(self, tt):
        phat_map = {
            "Đi muộn": PHAT_DI_MUON,
            "Về sớm": PHAT_VE_SOM,
            "Vắng mặt": PHAT_VANG,
            "Nửa buổi": PHAT_NUA_BUOI,
        }
        self.f_phat.setValue(phat_map.get(tt, 0))

    def _save(self):
        ngay = self.f_ngay.text().strip()
        if not ngay:
            QMessageBox.warning(self, "", "Nhập ngày!");
            return
        conn = get_conn()
        try:
            vals = (
                self.f_vao.time().toString("HH:mm"),
                self.f_ra.time().toString("HH:mm"),
                self.f_tt.currentText(),
                self.f_phat.value(),
                self.f_thuong.value(),
                self.f_gc.toPlainText()
            )
            if self.data:
                conn.execute("""UPDATE cham_cong SET gio_vao=?,gio_ra=?,trang_thai=?,
                    phat=?,thuong=?,ghi_chu=? WHERE id=?""", vals + (self.data["id"],))
            else:
                conn.execute("""INSERT INTO cham_cong(nv_id,ngay,gio_vao,gio_ra,trang_thai,phat,thuong,ghi_chu)
                    VALUES(?,?,?,?,?,?,?,?)""", (self.nv_id, ngay) + vals)
            conn.commit()
            QMessageBox.information(self, "✅ OK", "Lưu thành công!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))
        finally:
            conn.close()