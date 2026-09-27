# views/payment_success_dialog.py

import random
from PyQt6.QtWidgets import (
    QDialog, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QFrame,
    QWidget, QGridLayout
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPainter, QColor, QPen, QBrush, QRadialGradient, QLinearGradient
from datetime import datetime
import math


# ── Widget vẽ pháo hoa + sao ────────────────────────────────────────────────
class FireworksWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.particles = []
        self.stars     = [(random.randint(0,1100), random.randint(0,760),
                           random.uniform(0.3,1.0)) for _ in range(60)]
        self._init_particles()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(30)

    def _init_particles(self):
        self.particles.clear()
        bursts = [
            (200, 120, "#f59e0b"), (900, 150, "#a78bfa"),
            (150, 400, "#34d399"), (950, 350, "#f87171"),
            (550, 80,  "#60a5fa"), (800, 500, "#fbbf24"),
        ]
        for bx, by, color in bursts:
            for _ in range(22):
                angle = random.uniform(0, 2*math.pi)
                speed = random.uniform(2, 7)
                self.particles.append({
                    "x": bx, "y": by,
                    "vx": math.cos(angle)*speed,
                    "vy": math.sin(angle)*speed,
                    "life": random.randint(40,90),
                    "max": 90,
                    "color": color,
                    "size": random.uniform(3,7),
                    "tail": [],
                })

    def _tick(self):
        alive = []
        for p in self.particles:
            p["tail"].append((p["x"], p["y"]))
            if len(p["tail"]) > 5:
                p["tail"].pop(0)
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["vy"] += 0.12   # trọng lực
            p["vx"] *= 0.98
            p["life"] -= 1
            if p["life"] > 0:
                alive.append(p)
        self.particles = alive
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Sao nền
        for sx, sy, alpha in self.stars:
            c = QColor(255, 255, 255, int(alpha * 180))
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(c))
            p.drawEllipse(int(sx), int(sy), 2, 2)

        # Pháo hoa
        for pt in self.particles:
            ratio = pt["life"] / pt["max"]
            c = QColor(pt["color"])
            c.setAlphaF(ratio * 0.9)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(c))
            size = pt["size"] * ratio
            p.drawEllipse(int(pt["x"] - size/2), int(pt["y"] - size/2),
                          int(size), int(size))
        p.end()


# ── Dialog chính ─────────────────────────────────────────────────────────────
class PaymentSuccessDialog(QDialog):
    def __init__(
        self,
        customer="Nguyễn Văn A",
        car="Toyota Corolla Altis",
        amount="679.000.000 đ",
        order_id="DH008",
        method="Chuyển khoản ngân hàng",
        parent=None
    ):
        super().__init__(parent)
        self.customer = customer
        self.car      = car
        self.amount   = amount
        self.order_id = order_id
        self.method   = method

        self.setWindowTitle("Thanh toán thành công")
        self.setFixedSize(720, 620)
        self.setStyleSheet(self._css())
        self._build()

        # Pháo hoa
        self.fw = FireworksWidget(self)
        self.fw.setGeometry(0, 0, 720, 620)
        self.fw.lower()

    # ── CSS ──────────────────────────────────────────────────────────────────
    def _css(self):
        return """
        QDialog {
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 #020b1a, stop:0.5 #040f22, stop:1 #020b1a);
        }
        QLabel { color: white; background: transparent; font-family: 'Segoe UI'; }

        QFrame#mainCard {
            background: rgba(4,12,30,0.93);
            border: 1.5px solid #1e3a5f;
            border-radius: 28px;
        }
        QFrame#infoCard {
            background: rgba(8,18,40,0.97);
            border: 2px solid #2a4a8a;
            border-radius: 20px;
        }
        QFrame#giftCard {
            background: rgba(8,18,40,0.95);
            border: 1.5px solid #1e3a6a;
            border-radius: 18px;
        }

        QLabel#title {
            font-size: 28px;
            font-weight: 900;
            color: #22c55e;
            letter-spacing: 2px;
        }
        QLabel#sub {
            font-size: 12px;
            color: #94a3b8;
        }
        QLabel#orderVal {
            font-size: 16px;
            font-weight: 900;
            color: #a78bfa;
        }
        QLabel#fieldLbl {
            font-size: 10px;
            font-weight: 700;
            color: #64748b;
            letter-spacing: 1px;
        }
        QLabel#fieldVal {
            font-size: 13px;
            font-weight: 700;
            color: #e2e8f0;
        }
        QLabel#moneyVal {
            font-size: 16px;
            font-weight: 900;
            color: #22c55e;
        }
        QLabel#moneyWord {
            font-size: 10px;
            color: #64748b;
            font-style: italic;
        }
        QLabel#statusVal {
            font-size: 13px;
            font-weight: 700;
            color: #22c55e;
        }
        QLabel#giftText {
            font-size: 12px;
            font-weight: 700;
            color: #e2e8f0;
        }
        QPushButton#btnClose {
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 #16a34a, stop:1 #22c55e);
            border: none;
            border-radius: 12px;
            color: white;
            font-size: 15px;
            font-weight: 900;
            padding: 12px;
            letter-spacing: 2px;
        }
        QPushButton#btnClose:hover {
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 #22c55e, stop:1 #4ade80);
        }
        """

    # ── Build UI ──────────────────────────────────────────────────────────────
    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)

        card = QFrame(); card.setObjectName("mainCard")
        lv   = QVBoxLayout(card)
        lv.setContentsMargins(24, 16, 24, 16)
        lv.setSpacing(10)

        # ── Tiêu đề (đã gộp icon thành công ✅ ngay trong dòng chữ,
        # bỏ khối icon tròn riêng phía trên để tiết kiệm khoảng không gian) ──
        title = QLabel("✅  THANH TOÁN THÀNH CÔNG")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lv.addWidget(title)

        sub = QLabel("Cảm ơn quý khách đã mua xe tại AutoViet")
        sub.setObjectName("sub")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lv.addWidget(sub)

        # ── Mã đơn hàng ────────────────────────────────────────────────────
        order_row = QHBoxLayout()
        order_row.addStretch()
        badge_w = QWidget()
        badge_w.setStyleSheet("""
            background: rgba(30,20,60,0.6);
            border: 2px dashed #7c3aed;
            border-radius: 12px;
            padding: 0px;
        """)
        badge_lv = QHBoxLayout(badge_w)
        badge_lv.setContentsMargins(20,8,20,8); badge_lv.setSpacing(12)
        icon_lbl = QLabel("📄")
        icon_lbl.setStyleSheet("font-size:16px;")
        ma_lbl = QLabel("MÃ ĐƠN HÀNG")
        ma_lbl.setStyleSheet("font-size:14px;font-weight:700;color:#94a3b8;")
        val_lbl = QLabel(self.order_id)
        val_lbl.setObjectName("orderVal")
        badge_lv.addWidget(icon_lbl); badge_lv.addWidget(ma_lbl); badge_lv.addWidget(val_lbl)
        order_row.addWidget(badge_w)
        order_row.addStretch()
        lv.addLayout(order_row)

        # ── Info card ──────────────────────────────────────────────────────
        info = QFrame(); info.setObjectName("infoCard")
        info_h = QHBoxLayout(info)
        info_h.setContentsMargins(20,16,20,16)
        info_h.setSpacing(16)

        now = datetime.now().strftime("%d/%m/%Y - %H:%M")

        # Chuyển số tiền thành chữ đọc
        try:
            so = int(self.amount.replace(".","").replace("đ","").replace(" ","").strip())
            so_chu = f"( {self._so_thanh_chu(so)} )"
        except Exception:
            so_chu = ""

        # Cột trái — dùng QVBoxLayout riêng, không chung layout với cột phải
        # (tránh hoàn toàn lỗi đè ô từng gặp khi dùng QGridLayout)
        left_col = QVBoxLayout()
        left_col.setSpacing(12)
        left_col.addWidget(self._block("👤","#7c3aed","KHÁCH HÀNG",     self.customer))
        left_col.addWidget(self._block("🚗","#1d4ed8","XE ĐÃ MUA",      self.car))
        left_col.addWidget(self._block("💰","#15803d","SỐ TIỀN",        self.amount,
                                        sub_val=so_chu, money=True))

        # Đường kẻ giữa 2 cột
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setStyleSheet("background:#1e3a6a; max-width:1px;")

        # Cột phải — cũng là QVBoxLayout riêng, độc lập hoàn toàn với cột trái
        right_col = QVBoxLayout()
        right_col.setSpacing(12)
        right_col.addWidget(self._block("📅","#b45309","NGÀY THANH TOÁN", now))
        right_col.addWidget(self._block("💳","#1e40af","PHƯƠNG THỨC",    self.method))
        right_col.addWidget(self._block("🛡","#166534","TRẠNG THÁI",     "Đã thanh toán",
                                         status=True))

        info_h.addLayout(left_col, 1)
        info_h.addWidget(sep)
        info_h.addLayout(right_col, 1)

        lv.addWidget(info)


        # ── QR Code ───────────────────────────────────────────────────────
        try:
            from qr_utils import tao_qr_don_hang, qr_to_pixmap
            qr_path = tao_qr_don_hang({
                "ma_don": self.order_id,
                "ten_xe": self.car,
                "ten_kh": self.customer,
                "gia_ban_thuc": self.amount,
                "trang_thai": "Đã thanh toán",
                "ngay_dat": datetime.now().strftime("%Y-%m-%d"),
                "ten_nv": "",
            })
            qr_row = QHBoxLayout()
            qr_row.addStretch()

            qr_card = QWidget()
            qr_card.setStyleSheet("""
                        background:rgba(8,18,40,0.97);
                        border:2px solid #2563eb;
                        border-radius:16px;
                        padding:8px;
                    """)
            qr_card_lv = QHBoxLayout(qr_card)
            qr_card_lv.setContentsMargins(12, 10, 12, 10)
            qr_card_lv.setSpacing(14)

            # Ảnh QR
            qr_lbl = QLabel()
            qr_lbl.setPixmap(qr_to_pixmap(qr_path, 100))
            qr_lbl.setStyleSheet(
                "background:#ffffff;border-radius:8px;padding:6px;")
            qr_card_lv.addWidget(qr_lbl)

            # Chữ hướng dẫn
            hint_lv = QVBoxLayout();
            hint_lv.setSpacing(4)
            h1 = QLabel("📱 Quét mã QR")
            h1.setStyleSheet("font-size:13px;font-weight:800;color:#60a5fa;")
            h2 = QLabel("Lưu thông tin đơn hàng\nvào điện thoại của bạn")
            h2.setStyleSheet("font-size:11px;color:#94a3b8;")
            h3 = QLabel(f"Mã: {self.order_id}")
            h3.setStyleSheet("font-size:12px;font-weight:700;color:#a78bfa;")
            hint_lv.addWidget(h1)
            hint_lv.addWidget(h2)
            hint_lv.addWidget(h3)
            qr_card_lv.addLayout(hint_lv)

            qr_row.addWidget(qr_card)
            qr_row.addStretch()
            lv.addLayout(qr_row)
        except Exception as e:
            print(f"QR error: {e}")

        # ── Nút đóng ──────────────────────────────────────────────────────
        btn = QPushButton("✔  ĐÓNG")
        btn.setObjectName("btnClose")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(self.accept)
        lv.addWidget(btn)

        root.addWidget(card)

    # ── Block thông tin có icon tròn ─────────────────────────────────────────
    def _block(self, icon, icon_bg, label, value, sub_val="", money=False, status=False):
        w  = QWidget(); w.setStyleSheet("background:transparent;")
        hl = QHBoxLayout(w); hl.setContentsMargins(0,0,0,0); hl.setSpacing(12)

        # Icon tròn
        ic = QLabel(icon)
        ic.setFixedSize(36,36)
        ic.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ic.setStyleSheet(f"""
            background: {icon_bg};
            border-radius: 18px;
            font-size: 16px;
        """)

        # Text
        txt_w = QWidget(); txt_w.setStyleSheet("background:transparent;")
        tv    = QVBoxLayout(txt_w); tv.setContentsMargins(0,0,0,0); tv.setSpacing(2)

        lbl = QLabel(label); lbl.setObjectName("fieldLbl")

        val = QLabel(value)
        if money:
            val.setObjectName("moneyVal")
        elif status:
            val.setObjectName("statusVal")
        else:
            val.setObjectName("fieldVal")

        tv.addWidget(lbl)
        tv.addWidget(val)

        if sub_val:
            sv = QLabel(sub_val); sv.setObjectName("moneyWord")
            tv.addWidget(sv)

        hl.addWidget(ic)
        hl.addWidget(txt_w, 1)
        return w

    # ── Đọc số thành chữ (đơn giản) ─────────────────────────────────────────
    def _so_thanh_chu(self, n: int) -> str:
        don_vi = ["","một","hai","ba","bốn","năm","sáu","bảy","tám","chín"]
        hang   = ["","nghìn","triệu","tỷ"]
        if n == 0: return "không"
        parts = []; i = 0
        while n:
            r = n % 1000; n //= 1000
            if r: parts.append((r, hang[i]))
            i += 1
        parts.reverse()
        out = []
        for r, h in parts:
            t = r // 100; r2 = r % 100; ch = r2 // 10; dv = r2 % 10
            s = ""
            if t: s += don_vi[t] + " trăm "
            if ch == 1: s += "mười "
            elif ch > 1: s += don_vi[ch] + " mươi "
            if dv == 1 and ch > 1: s += "mốt "
            elif dv == 5 and ch > 0: s += "lăm "
            elif dv: s += don_vi[dv] + " "
            out.append(s.strip() + (" " + h if h else ""))
        return " ".join(out).strip().capitalize() + " đồng"