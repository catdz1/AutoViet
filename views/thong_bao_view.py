"""
views/thong_bao_view.py — Thông báo trong app (Bell icon)
File MỚI — thêm vào views/
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QDialog, QApplication
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from database import get_conn
from datetime import datetime, timedelta


def get_thong_bao(current_user=None):
    """Lấy danh sách thông báo"""
    conn = get_conn()
    msgs = []
    nv_id = (current_user or {}).get("nv_id")
    is_admin = (current_user or {}).get("role") == "admin"

    # 1. Đơn hàng mới (trong 24h)
    if is_admin:
        rows = conn.execute("""
            SELECT dh.ma_don, x.hang_xe||' '||x.dong_xe, kh.ho_ten, dh.ngay_dat
            FROM don_hang dh JOIN xe x ON dh.xe_id=x.id
            JOIN khach_hang kh ON dh.kh_id=kh.id
            WHERE date(dh.ngay_dat) >= date('now','-1 day')
            ORDER BY dh.id DESC LIMIT 5
        """).fetchall()
        for r in rows:
            msgs.append({
                "icon":"📋","type":"don_hang","color":"#60a5fa",
                "title":f"Đơn hàng mới: {r[0]}",
                "body":f"{r[2]} mua {r[1]}",
                "time": r[3]
            })

    # 2. NV — đơn hàng của mình
    if nv_id and not is_admin:
        rows = conn.execute("""
            SELECT dh.ma_don, x.hang_xe||' '||x.dong_xe, kh.ho_ten, dh.ngay_dat
            FROM don_hang dh JOIN xe x ON dh.xe_id=x.id
            JOIN khach_hang kh ON dh.kh_id=kh.id
            WHERE dh.nv_id=? AND date(dh.ngay_dat)>=date('now','-7 day')
            ORDER BY dh.id DESC LIMIT 3
        """, (nv_id,)).fetchall()
        for r in rows:
            msgs.append({
                "icon":"📋","type":"don_hang","color":"#60a5fa",
                "title":f"Đơn của tôi: {r[0]}",
                "body":f"{r[2]} — {r[1]}",
                "time": r[3]
            })

    # 3. Xe tồn kho thấp
    if is_admin:
        cnt = conn.execute("SELECT COUNT(*) FROM xe WHERE trang_thai='Còn hàng'").fetchone()[0]
        if cnt < 4:
            msgs.append({
                "icon":"📦","type":"ton_kho","color":"#f87171",
                "title":f"⚠️ Tồn kho thấp: chỉ còn {cnt} xe!",
                "body":"Cần nhập thêm xe hàng sớm",
                "time": datetime.now().strftime("%Y-%m-%d")
            })

    # 4. Dịch vụ đang thực hiện
    dv_rows = conn.execute("""
        SELECT dv.ma_dv, x.hang_xe||' '||x.dong_xe, kh.ho_ten
        FROM dich_vu dv LEFT JOIN xe x ON dv.xe_id=x.id
        LEFT JOIN khach_hang kh ON dv.kh_id=kh.id
        WHERE dv.trang_thai='Đang thực hiện'
        AND (? OR dv.nv_id=?)
    """, (1 if is_admin else 0, nv_id or 0)).fetchall()
    for r in dv_rows:
        msgs.append({
            "icon":"🔧","type":"dich_vu","color":"#fbbf24",
            "title":f"DV đang thực hiện: {r[0]}",
            "body":f"{r[2]} — {r[1]}",
            "time": datetime.now().strftime("%Y-%m-%d")
        })

    # 5. Nhắc dịch vụ hoàn thành trễ
    tre_rows = conn.execute("""
        SELECT dv.ma_dv, kh.ho_ten
        FROM dich_vu dv LEFT JOIN khach_hang kh ON dv.kh_id=kh.id
        WHERE dv.trang_thai='Tiếp nhận'
        AND date(dv.ngay_nhan) <= date('now','-3 day')
    """).fetchall()
    for r in tre_rows:
        msgs.append({
            "icon":"⏰","type":"tre_han","color":"#f97316",
            "title":f"Phiếu DV chờ xử lý: {r[0]}",
            "body":f"KH {r[1]} đã chờ > 3 ngày!",
            "time": datetime.now().strftime("%Y-%m-%d")
        })

    conn.close()
    return msgs


class ThongBaoWidget(QDialog):
    """Popup thông báo đẹp"""
    def __init__(self, parent=None, current_user=None):
        super().__init__(parent)
        self.current_user = current_user
        self.setWindowTitle("🔔  Thông báo")
        self.setMinimumWidth(440); self.setMinimumHeight(500)
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet("""
            QDialog {
                background:#1a1d28;
                border:1px solid #2c3050;
                border-radius:14px;
            }
        """)
        self._build()
        self._load()
    def _build(self):
        lv = QVBoxLayout(self); lv.setContentsMargins(0,0,0,0); lv.setSpacing(0)
        # Header
        hdr = QWidget()
        hdr.setStyleSheet("background:#13151c;border-radius:14px 14px 0 0;")
        hl = QHBoxLayout(hdr); hl.setContentsMargins(16,14,16,14)
        title = QLabel("🔔  Thông báo")
        title.setStyleSheet("font-size:15px;font-weight:700;color:#e2e8f0;background:transparent;")
        btn_close = QPushButton("✕"); btn_close.setFixedSize(28,28)
        btn_close.setStyleSheet("""
            QPushButton{background:#252840;color:#9ca3af;border:none;border-radius:14px;font-size:13px;}
            QPushButton:hover{background:#f87171;color:white;}
        """)
        btn_close.clicked.connect(self.close)
        btn_clear = QPushButton("Xoá tất cả")
        btn_clear.setStyleSheet("background:transparent;color:#4a5568;font-size:11px;border:none;padding:4px 8px;")
        btn_clear.clicked.connect(self.close)
        hl.addWidget(title); hl.addStretch(); hl.addWidget(btn_clear); hl.addWidget(btn_close)
        lv.addWidget(hdr)

        # Scroll
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background:transparent;")
        self.content = QWidget()
        self.content_lv = QVBoxLayout(self.content)
        self.content_lv.setContentsMargins(12,12,12,12); self.content_lv.setSpacing(8)
        scroll.setWidget(self.content)
        lv.addWidget(scroll)
    def _load(self):
        msgs = get_thong_bao(self.current_user)
        while self.content_lv.count():
            item = self.content_lv.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        if not msgs:
            empty = QLabel("✅  Không có thông báo mới")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet("color:#4a5568;font-size:13px;background:transparent;padding:40px;")
            self.content_lv.addWidget(empty)
            return

        for msg in msgs:
            card = QWidget()
            card.setStyleSheet(f"""
                QWidget {{
                    background:#1e2236;
                    border-radius:10px;
                    border-left:4px solid {msg['color']};
                }}
            """)
            cl = QHBoxLayout(card); cl.setContentsMargins(12,10,12,10); cl.setSpacing(10)

            icon = QLabel(msg['icon'])
            icon.setStyleSheet(f"font-size:20px;background:transparent;min-width:28px;")
            icon.setAlignment(Qt.AlignmentFlag.AlignTop)

            info = QVBoxLayout(); info.setSpacing(2)
            title = QLabel(msg['title'])
            title.setStyleSheet(f"font-size:12px;font-weight:700;color:{msg['color']};background:transparent;")
            title.setWordWrap(True)
            body = QLabel(msg['body'])
            body.setStyleSheet("font-size:11px;color:#9ca3af;background:transparent;")
            body.setWordWrap(True)
            time_lbl = QLabel(msg.get('time',''))
            time_lbl.setStyleSheet("font-size:10px;color:#374151;background:transparent;")
            info.addWidget(title); info.addWidget(body); info.addWidget(time_lbl)

            cl.addWidget(icon); cl.addLayout(info,1)
            self.content_lv.addWidget(card)

        self.content_lv.addStretch()


class BellButton(QPushButton):
    """Nút chuông thông báo cho titlebar"""
    clicked_bell = pyqtSignal()

    def __init__(self, parent=None, current_user=None):
        super().__init__(parent)
        self.current_user = current_user
        self._count = 0
        self.setFixedSize(36,36)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background:#1e2236;border:1px solid #2c3050;
                border-radius:8px;font-size:16px;color:#9ca3af;
            }
            QPushButton:hover{background:#252a42;color:#e2e8f0;}
        """)
        self.setText("🔔")
        self.clicked.connect(self._show_popup)
        # Auto refresh mỗi 30 giây
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh_count)
        self._timer.start(30000)
        self._refresh_count()

    def _refresh_count(self):
        msgs = get_thong_bao(self.current_user)
        self._count = len(msgs)
        if self._count > 0:
            self.setText(f"🔔")
            self.setStyleSheet("""
                QPushButton {
                    background:#2c1f6e;border:1px solid #7c3aed;
                    border-radius:8px;font-size:16px;color:#a78bfa;
                    font-weight:700;
                }
                QPushButton:hover{background:#3d2a8a;}
            """)
            self.setToolTip(f"{self._count} thông báo mới")
        else:
            self.setText("🔔")
            self.setStyleSheet("""
                QPushButton {
                    background:#1e2236;border:1px solid #2c3050;
                    border-radius:8px;font-size:16px;color:#4a5568;
                }
                QPushButton:hover{background:#252a42;color:#e2e8f0;}
            """)
            self.setToolTip("Không có thông báo mới")

    def _show_popup(self):
        popup = ThongBaoWidget(self.window(), self.current_user)
        # Vị trí popup gần nút chuông
        pos = self.mapToGlobal(self.rect().bottomRight())
        popup.move(pos.x()-440, pos.y()+4)
        popup.exec()
