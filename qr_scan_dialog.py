"""
qr_scan_dialog.py -- Dialog quet QR Code don hang
Dat o thu muc goc: ngo_quoc_tuan/

Su dung:
    from qr_scan_dialog import QuetQRDialog
    dlg = QuetQRDialog(self)
    dlg.exec()

Can cai: pip install opencv-python pyzbar qrcode[pil]
"""
import cv2
import numpy as np
from pyzbar import pyzbar

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QWidget, QFrame, QComboBox, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QImage, QPixmap, QFont, QColor


# ════════════════════════════════════════════════════════════════
# THREAD CAMERA + QUET QR
# ════════════════════════════════════════════════════════════════
class QRScanThread(QThread):
    frame_ready  = pyqtSignal(QImage)          # Moi frame de hien thi
    qr_detected  = pyqtSignal(str)             # Tim thay QR -> tra ve noi dung
    no_qr        = pyqtSignal()                # Khong co QR trong frame

    def __init__(self, cam_index=0):
        super().__init__()
        self.cam_index = cam_index
        self._running  = True
        self._paused   = False

    def run(self):
        cap = cv2.VideoCapture(self.cam_index, cv2.CAP_DSHOW)

        # Tang chat luong camera de quet QR tot hon
        cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        cap.set(cv2.CAP_PROP_AUTOFOCUS,    1)     # Tu dong lay net
        cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.75) # Tu dong chong sang

        found_count = 0   # Phat hien lien tiep N lan moi bao

        while self._running:
            if self._paused:
                self.msleep(100)
                continue

            ok, frame = cap.read()
            if not ok:
                self.msleep(50)
                continue

            # ── Tien xu ly anh de quet QR tot hon ────────────────────
            gray     = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Lam sac net
            kernel   = np.array([[0,-1,0],[-1,5,-1],[0,-1,0]])
            sharpened= cv2.filter2D(gray, -1, kernel)

            # Tang tuong phan
            clahe    = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8,8))
            enhanced = clahe.apply(sharpened)

            # ── Quet QR bang pyzbar ───────────────────────────────────
            decoded = pyzbar.decode(enhanced)

            if not decoded:
                # Thu them voi anh goc
                decoded = pyzbar.decode(frame)

            if decoded:
                data = decoded[0].data.decode("utf-8", errors="ignore")
                found_count += 1

                # Ve khung xanh quanh QR
                pts = decoded[0].polygon
                if pts:
                    pts_np = np.array([[p.x, p.y] for p in pts], np.int32)
                    cv2.polylines(frame, [pts_np], True, (0, 255, 80), 3)
                    x, y, w, h = decoded[0].rect
                    cv2.putText(frame, "QR FOUND!", (x, y-12),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,80), 2)

                # Phat hien lien tiep >= 2 lan moi bao (tranh false positive)
                if found_count >= 2:
                    self._emit_frame(frame)
                    self.qr_detected.emit(data)
                    self._paused = True
                    found_count  = 0
                    continue
            else:
                found_count = 0
                self.no_qr.emit()

            # Ve khung huong dan o giua
            h_f, w_f = frame.shape[:2]
            cx, cy   = w_f // 2, h_f // 2
            size     = min(w_f, h_f) // 3
            cv2.rectangle(frame,
                          (cx - size, cy - size),
                          (cx + size, cy + size),
                          (41, 128, 255), 2)
            # 4 goc vang
            for dx, dy in [(1,1),(-1,1),(1,-1),(-1,-1)]:
                sx, sy = cx + dx*size, cy + dy*size
                ex1    = sx - dx*40
                ey2    = sy - dy*40
                cv2.line(frame, (sx,sy), (ex1,sy), (255,200,0), 3)
                cv2.line(frame, (sx,sy), (sx,ey2), (255,200,0), 3)

            self._emit_frame(frame)

        cap.release()

    def _emit_frame(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        img = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
        self.frame_ready.emit(img)

    def resume(self):
        self._paused = False

    def stop(self):
        self._running = False
        self.wait(3000)


# ════════════════════════════════════════════════════════════════
# DIALOG QUET QR
# ════════════════════════════════════════════════════════════════
class QuetQRDialog(QDialog):
    """
    Dialog quet QR Code don hang bang camera laptop.
    Hien thi noi dung tim duoc va tim don hang trong DB.
    """
    def __init__(self, parent=None, cam_index=0):
        super().__init__(parent)
        self.cam_index  = cam_index
        self.setWindowTitle("📷  Quét mã QR đơn hàng")
        self.setFixedSize(720, 600)
        self.setModal(True)
        self.setStyleSheet("""
            QDialog {
                background: #0a0e1a;
            }
            QLabel {
                background: transparent;
                color: #e2e8f0;
                font-family: 'Segoe UI', Arial;
            }
            QPushButton {
                font-family: 'Segoe UI', Arial;
                font-size: 13px;
                font-weight: 700;
                border-radius: 10px;
                padding: 10px 20px;
            }
            QPushButton#btn_close {
                background: #1e293b;
                color: #94a3b8;
                border: 1px solid #334155;
            }
            QPushButton#btn_close:hover { background: #334155; }
            QPushButton#btn_retry {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #1d4ed8, stop:1 #2563eb);
                color: white; border: none;
            }
            QPushButton#btn_retry:hover { background: #2563eb; }
            QComboBox {
                background: #1e293b; color: #e2e8f0;
                border: 1px solid #334155; border-radius: 8px;
                padding: 6px 12px; font-size: 12px;
            }
        """)
        self._thread = None
        self._build()
        self._start_scan()

    # ── Build UI ──────────────────────────────────────────────────────────
    def _build(self):
        lv = QVBoxLayout(self)
        lv.setContentsMargins(16, 14, 16, 14)
        lv.setSpacing(10)

        # Header
        hdr = QLabel("📷  Quét mã QR đơn hàng")
        hdr.setStyleSheet("font-size:17px;font-weight:900;color:#60a5fa;")
        hdr.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lv.addWidget(hdr)

        sub = QLabel("Hướng camera vào mã QR trên điện thoại hoặc tờ giấy")
        sub.setStyleSheet("font-size:12px;color:#64748b;")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lv.addWidget(sub)

        # Camera chon
        cam_row = QHBoxLayout()
        cam_lbl = QLabel("Camera:")
        cam_lbl.setStyleSheet("font-size:12px;color:#94a3b8;")
        self.sel_cam = QComboBox()
        for i in range(3):
            self.sel_cam.addItem(f"Camera {i}", i)
        self.sel_cam.currentIndexChanged.connect(self._switch_cam)
        cam_row.addStretch()
        cam_row.addWidget(cam_lbl)
        cam_row.addWidget(self.sel_cam)
        lv.addLayout(cam_row)

        # Preview camera
        self.lbl_cam = QLabel()
        self.lbl_cam.setFixedSize(680, 400)
        self.lbl_cam.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_cam.setStyleSheet("""
            background: #0f172a;
            border: 2px solid #1e40af;
            border-radius: 14px;
            color: #475569;
            font-size: 14px;
        """)
        self.lbl_cam.setText("⏳ Đang khởi động camera...")
        lv.addWidget(self.lbl_cam)

        # Status
        self.lbl_status = QLabel("🔵  Đang tìm mã QR...")
        self.lbl_status.setStyleSheet("font-size:13px;color:#60a5fa;font-weight:700;")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lv.addWidget(self.lbl_status)

        # Buttons
        brow = QHBoxLayout(); brow.setSpacing(10)
        self.btn_retry = QPushButton("🔄  Quét lại")
        self.btn_retry.setObjectName("btn_retry")
        self.btn_retry.clicked.connect(self._retry)
        self.btn_retry.setVisible(False)

        btn_close = QPushButton("✖  Đóng")
        btn_close.setObjectName("btn_close")
        btn_close.clicked.connect(self._close)

        brow.addStretch()
        brow.addWidget(self.btn_retry)
        brow.addWidget(btn_close)
        lv.addLayout(brow)

    # ── Camera control ────────────────────────────────────────────────────
    def _start_scan(self):
        self._stop_thread()
        self.lbl_status.setText("🔵  Đang tìm mã QR...")
        self.lbl_status.setStyleSheet("font-size:13px;color:#60a5fa;font-weight:700;")
        self.btn_retry.setVisible(False)

        self._thread = QRScanThread(cam_index=self.cam_index)
        self._thread.frame_ready.connect(self._show_frame)
        self._thread.qr_detected.connect(self._on_qr_found)
        self._thread.no_qr.connect(self._on_no_qr)
        self._thread.start()

    def _stop_thread(self):
        if self._thread and self._thread.isRunning():
            self._thread.stop()
        self._thread = None

    def _switch_cam(self, idx):
        self.cam_index = self.sel_cam.currentData()
        self._start_scan()

    def _retry(self):
        self.lbl_cam.setText("⏳ Đang khởi động camera...")
        self._start_scan()

    # ── Slots ─────────────────────────────────────────────────────────────
    def _show_frame(self, img: QImage):
        px = QPixmap.fromImage(img).scaled(
            680, 400,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.lbl_cam.setPixmap(px)

    _qr_done = False  # Tranh bao nhieu lan

    def _on_qr_found(self, content: str):
        if self._qr_done:
            return
        self._qr_done = True

        self.lbl_status.setText("✅  Quét thành công!")
        self.lbl_status.setStyleSheet("font-size:14px;color:#4ade80;font-weight:800;")
        self.btn_retry.setVisible(True)

        # Phan tich noi dung QR
        self._show_qr_result(content)

    def _on_no_qr(self):
        pass  # Khong lam gi de khoi giat giao dien

    def _show_qr_result(self, content: str):
        """Hien ket qua QR va tim don hang trong DB."""
        from database import get_conn

        # Trich ma don hang tu noi dung QR
        ma_don = None
        for line in content.splitlines():
            if "Don hang" in line or "don hang" in line:
                parts = line.split(":")
                if len(parts) >= 2:
                    ma_don = parts[1].strip()
                    break

        # Tim trong DB
        don = None
        if ma_don:
            conn = get_conn()
            don = conn.execute("""
                SELECT dh.ma_don, x.hang_xe||' '||x.dong_xe as ten_xe,
                       kh.ho_ten as ten_kh, dh.gia_ban_thuc,
                       dh.trang_thai, dh.ngay_dat
                FROM don_hang dh
                JOIN xe x ON dh.xe_id = x.id
                JOIN khach_hang kh ON dh.kh_id = kh.id
                WHERE dh.ma_don = ?
            """, (ma_don,)).fetchone()
            conn.close()

        # Hien dialog ket qua
        dlg = QDialog(self)
        dlg.setWindowTitle("🎯  Kết quả quét QR")
        dlg.setFixedWidth(440)
        dlg.setStyleSheet("""
            QDialog { background: #0f172a; }
            QLabel { background: transparent; color: #e2e8f0;
                     font-family: 'Segoe UI'; }
        """)
        lv = QVBoxLayout(dlg)
        lv.setContentsMargins(24, 20, 24, 20)
        lv.setSpacing(12)

        if don:
            # Tim thay don hang
            icon = QLabel("✅")
            icon.setStyleSheet("font-size:40px;")
            icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lv.addWidget(icon)

            t = QLabel("Tìm thấy đơn hàng!")
            t.setStyleSheet("font-size:16px;font-weight:900;color:#4ade80;")
            t.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lv.addWidget(t)

            sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine)
            sep.setStyleSheet("background:#1e293b;max-height:1px;")
            lv.addWidget(sep)

            fields = [
                ("Mã đơn",     don[0],                 "#60a5fa"),
                ("Xe mua",     don[1],                 "#e2e8f0"),
                ("Khách hàng", don[2],                 "#e2e8f0"),
                ("Giá bán",    f"{int(don[3]):,} ₫",   "#4ade80"),
                ("Trạng thái", don[4],                 "#fbbf24"),
                ("Ngày đặt",   don[5],                 "#94a3b8"),
            ]
            for key, val, color in fields:
                row_w = QHBoxLayout()
                k = QLabel(key + ":")
                k.setStyleSheet("font-size:12px;color:#64748b;font-weight:700;min-width:100px;")
                v = QLabel(val or "—")
                v.setStyleSheet(f"font-size:13px;color:{color};font-weight:700;")
                v.setWordWrap(True)
                row_w.addWidget(k)
                row_w.addWidget(v, 1)
                lv.addLayout(row_w)

        else:
            # Khong tim thay don hang -- hien noi dung QR thu
            icon = QLabel("⚠️")
            icon.setStyleSheet("font-size:36px;")
            icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lv.addWidget(icon)

            t = QLabel("Không tìm thấy đơn hàng")
            t.setStyleSheet("font-size:15px;font-weight:800;color:#fbbf24;")
            t.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lv.addWidget(t)

            lbl_raw = QLabel("Nội dung QR:")
            lbl_raw.setStyleSheet("font-size:11px;color:#64748b;")
            lv.addWidget(lbl_raw)

            content_lbl = QLabel(content[:300])
            content_lbl.setStyleSheet("""
                font-size:11px; color:#94a3b8;
                background:#1e293b; border-radius:8px;
                padding:10px; font-family:'Courier New';
            """)
            content_lbl.setWordWrap(True)
            lv.addWidget(content_lbl)

        # Nut dong
        brow = QHBoxLayout(); brow.addStretch()
        btn_ok = QPushButton("✔  Đóng")
        btn_ok.setStyleSheet("""
            QPushButton {
                background: #2563eb; color: white; border: none;
                border-radius: 10px; padding: 10px 28px;
                font-size: 13px; font-weight: 800;
            }
            QPushButton:hover { background: #1d4ed8; }
        """)
        btn_ok.clicked.connect(dlg.accept)
        brow.addWidget(btn_ok)
        lv.addLayout(brow)

        dlg.exec()

        # Cho phep quet lai
        self._qr_done = False
        self._retry()

    # ── Dong dialog ──────────────────────────────────────────────────────
    def _close(self):
        self._stop_thread()
        self.accept()

    def closeEvent(self, e):
        self._stop_thread()
        super().closeEvent(e)