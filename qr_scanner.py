import cv2
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap


class QRScannerDialog(QDialog):
    """Dialog quet QR code bang camera laptop"""
    don_hang_found = pyqtSignal(str)  # emit ma_don khi quet duoc

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Quet QR Code don hang")
        self.setMinimumSize(660, 540)
        self.setStyleSheet("""
            QDialog { background:#0f1f35; }
            QLabel  { background:transparent; color:#ffffff; }
            QPushButton {
                background:#2563eb; color:white; border:none;
                border-radius:8px; padding:10px 20px;
                font-size:13px; font-weight:700;
            }
            QPushButton:hover { background:#1d4ed8; }
            QPushButton#btn_close {
                background:#374151; color:#9ca3af;
            }
            QPushButton#btn_close:hover { background:#4b5563; color:#ffffff; }
        """)
        self._cap      = None
        self._timer    = QTimer(self)
        self._found    = False
        self._detector = cv2.QRCodeDetector()
        self._build()
        QTimer.singleShot(300, self._start_camera)

    # ── UI ────────────────────────────────────────────────────────────
    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(10)

        title = QLabel("Quet ma QR don hang")
        title.setStyleSheet("font-size:16px;font-weight:800;color:#60a5fa;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(title)

        hint = QLabel("Huong camera vao ma QR tren dien thoai hoac to giay")
        hint.setStyleSheet("font-size:12px;color:#94a3b8;")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(hint)

        self.cam_lbl = QLabel("Dang khoi dong camera...")
        self.cam_lbl.setFixedSize(600, 400)
        self.cam_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cam_lbl.setStyleSheet(
            "background:#13151c;border:2px solid #2563eb;"
            "border-radius:12px;color:#4a5568;font-size:14px;")
        root.addWidget(self.cam_lbl, alignment=Qt.AlignmentFlag.AlignCenter)

        self.status_lbl = QLabel("Dang tim ma QR...")
        self.status_lbl.setStyleSheet(
            "font-size:13px;color:#fbbf24;font-weight:600;")
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self.status_lbl)

        bh = QHBoxLayout(); bh.addStretch()
        btn_close = QPushButton("Dong")
        btn_close.setObjectName("btn_close")
        btn_close.clicked.connect(self._stop_and_close)
        bh.addWidget(btn_close)
        root.addLayout(bh)

    # ── Camera ───────────────────────────────────────────────────────
    def _start_camera(self):
        for idx in range(3):
            cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
            if cap.isOpened():
                self._cap = cap
                break
        if not self._cap or not self._cap.isOpened():
            self.status_lbl.setText("Khong mo duoc camera!")
            self.status_lbl.setStyleSheet(
                "font-size:13px;color:#f87171;font-weight:600;")
            return
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1280)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self._cap.set(cv2.CAP_PROP_AUTOFOCUS,    1)
        self._timer.timeout.connect(self._read_frame)
        self._timer.start(40)

    def _read_frame(self):
        if not self._cap or self._found:
            return
        ret, frame = self._cap.read()
        if not ret:
            return

        data, pts, _ = self._detector.detectAndDecode(frame)

        if data:
            if pts is not None:
                pts_int = pts.astype(int)
                for i in range(4):
                    cv2.line(frame,
                             tuple(pts_int[0][i]),
                             tuple(pts_int[0][(i + 1) % 4]),
                             (0, 255, 80), 3)
            self._on_found(data)
        else:
            # Ve khung huong dan giua man hinh
            h, w = frame.shape[:2]
            cx, cy   = w // 2, h // 2
            size     = min(w, h) // 3
            cl       = corner_len = size // 3
            cv2.rectangle(frame, (cx-size, cy-size), (cx+size, cy+size),
                          (41, 128, 255), 2)
            for dx, dy in [(1,1),(-1,1),(1,-1),(-1,-1)]:
                sx, sy = cx + dx*size, cy + dy*size
                cv2.line(frame, (sx,sy), (sx - dx*cl, sy), (255,200,0), 3)
                cv2.line(frame, (sx,sy), (sx, sy - dy*cl), (255,200,0), 3)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, c = rgb.shape
        img = QImage(rgb.data, w, h, w*c, QImage.Format.Format_RGB888)
        self.cam_lbl.setPixmap(
            QPixmap.fromImage(img).scaled(
                600, 400,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.FastTransformation))

    # ── Xu ly QR tim duoc ────────────────────────────────────────────
    def _on_found(self, data: str):
        self._found = True
        self._timer.stop()

        ma_don = self._extract_ma_don(data.strip())

        if ma_don:
            self.status_lbl.setText(f"Tim thay don: {ma_don}")
            self.status_lbl.setStyleSheet(
                "font-size:14px;color:#4ade80;font-weight:800;")
            self.don_hang_found.emit(ma_don)
            QTimer.singleShot(1000, self._stop_and_close)
        else:
            self.status_lbl.setText("QR nay khong phai don hang AutoViet!")
            self.status_lbl.setStyleSheet(
                "font-size:13px;color:#f87171;font-weight:600;")
            self._found = False
            self._timer.start(40)

    def _extract_ma_don(self, data: str) -> str:
        """
        Ho tro cac dinh dang QR:
        1. AUTOVIET:DH037        <- format hien tai cua qr_utils.py
        2. Text nhieu dong co "Don: DH037"
        3. JSON {"ma_don":"DH037"}
        4. Fallback: bat ki token DH...
        """
        # Format 1: AUTOVIET:DH037  <-- CHINH
        if data.startswith("AUTOVIET:"):
            ma = data[len("AUTOVIET:"):].strip()
            if ma:
                return ma

        # Format 2: text nhieu dong
        if "AUTOVIET" in data:
            for line in data.splitlines():
                line = line.strip()
                low = line.lower()
                if low.startswith("don:") or low.startswith("don hang:"):
                    parts = line.split(":", 1)
                    if len(parts) == 2:
                        ma = parts[1].strip()
                        if ma:
                            return ma

        # Format 3: JSON
        if data.startswith("{"):
            try:
                import json
                obj = json.loads(data)
                ma = str(obj.get("ma_don", "")).strip()
                if ma:
                    return ma
            except Exception:
                pass

        # Fallback: token bat dau DH
        for token in data.split():
            if token.upper().startswith("DH") and len(token) >= 4:
                return token.upper()

        return ""

    # ── Dong ─────────────────────────────────────────────────────────
    def _stop_and_close(self):
        self._timer.stop()
        if self._cap:
            self._cap.release()
            self._cap = None
        self.accept()

    def closeEvent(self, e):
        self._timer.stop()
        if self._cap:
            self._cap.release()
            self._cap = None
        super().closeEvent(e)