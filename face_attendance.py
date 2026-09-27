"""
face_attendance.py — Nhan dien khuon mat cham cong
Su dung QThread de tranh crash voi PyQt6 tren Windows
"""
import cv2, os, numpy as np, pickle, time
from datetime import datetime, date
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QMessageBox, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap

FACE_DIR   = os.path.join(os.path.dirname(os.path.abspath(__file__)), "face_data")
MODEL_PATH = os.path.join(FACE_DIR, "face_model.yml")
LABEL_PATH = os.path.join(FACE_DIR, "labels.pkl")
os.makedirs(FACE_DIR, exist_ok=True)

CASCADE = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

def _load_labels():
    if os.path.exists(LABEL_PATH):
        with open(LABEL_PATH, "rb") as f:
            return pickle.load(f)
    return {}


def _save_labels(d):
    with open(LABEL_PATH, "wb") as f:
        pickle.dump(d, f)


def has_face_model(nv_id):
    return nv_id in _load_labels().keys()


# ── Camera Worker Thread ──────────────────────────────────────
class CameraThread(QThread):
    frame_ready   = pyqtSignal(np.ndarray)
    face_match    = pyqtSignal()
    face_nomatch  = pyqtSignal()
    no_face       = pyqtSignal()
    register_done = pyqtSignal()
    error_msg     = pyqtSignal(str)

    def __init__(self, mode="register", nv_id=None):
        super().__init__()
        self.mode     = mode
        self.nv_id    = nv_id
        self._running = True
        self.faces    = []
        self.labels   = []
        self.count    = 0

    def run(self):
        try:
            cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            if not cap.isOpened():
                self.error_msg.emit("Khong mo duoc camera!")
                return
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            cap.set(cv2.CAP_PROP_FPS, 15)

            while self._running:
                ret, frame = cap.read()
                if not ret:
                    time.sleep(0.05); continue

                gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                dets  = CASCADE.detectMultiScale(gray, 1.3, 5, minSize=(80,80))

                if self.mode == "register":
                    for (x,y,w,h) in dets:
                        roi = cv2.resize(gray[y:y+h, x:x+w], (200,200))
                        if self.count < 40:
                            self.faces.append(roi)
                            self.labels.append(self.nv_id)
                            self.count += 1
                        cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
                        cv2.putText(frame,f"{self.count}/40",(x,y-10),
                            cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,255,0),2)
                    self.frame_ready.emit(frame.copy())
                    if self.count >= 40:
                        self._running = False
                        self.register_done.emit()

                elif self.mode == "recognize":
                    found = False
                    for (x,y,w,h) in dets:
                        found = True
                        roi = cv2.resize(gray[y:y+h, x:x+w], (200,200))
                        try:
                            rec = cv2.face.LBPHFaceRecognizer_create()
                            rec.read(MODEL_PATH)
                            label, conf = rec.predict(roi)
                            if conf < 70 and label == self.nv_id:
                                cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
                                cv2.putText(frame,f"OK {int(conf)}",(x,y-10),
                                    cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,255,0),2)
                                self.face_match.emit()
                            else:
                                cv2.rectangle(frame,(x,y),(x+w,y+h),(0,0,255),2)
                                cv2.putText(frame,f"Khong khop {int(conf)}",(x,y-10),
                                    cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2)
                                self.face_nomatch.emit()
                        except Exception:
                            cv2.rectangle(frame,(x,y),(x+w,y+h),(128,128,128),2)
                    if not found:
                        self.no_face.emit()
                    self.frame_ready.emit(frame.copy())

                time.sleep(0.05)
            cap.release()
        except Exception as e:
            self.error_msg.emit(str(e))

    def stop(self):
        self._running = False
        self.wait(3000)


# ══════════════════════════════════════════════════════════════
# DIALOG DANG KY KHUON MAT
# ══════════════════════════════════════════════════════════════
class FaceRegisterDialog(QDialog):
    def __init__(self, parent=None, nv_id=None, ho_ten=""):
        super().__init__(parent)
        self.nv_id  = nv_id
        self.ho_ten = ho_ten
        self._thread = None
        self.setWindowTitle("Dang ky khuon mat")
        self.setMinimumSize(580, 520)
        self.setStyleSheet("""
            QDialog{background:#0f1117;}
            QLabel{background:transparent;color:#e2e8f0;}
            QPushButton#s{background:#6d28d9;color:white;border:none;
                border-radius:10px;font-size:14px;font-weight:700;padding:12px 28px;}
            QPushButton#s:hover{background:#7c3aed;}
            QPushButton#s:disabled{background:#2c1f6e;color:#64748b;}
            QPushButton#c{background:#1e2236;color:#9ca3af;
                border:1px solid #2c3050;border-radius:10px;font-size:13px;padding:11px 24px;}
        """)
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20,16,20,20); root.setSpacing(14)

        t = QLabel(f"📸  Dang ky khuon mat — {self.ho_ten}")
        t.setStyleSheet("font-size:16px;font-weight:800;color:#a78bfa;")
        t.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(t)

        sub = QLabel("He thong se chup 40 anh khuon mat de nhan dien khi cham cong")
        sub.setStyleSheet("font-size:12px;color:#64748b;")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(sub)

        self.cam = QLabel("📷  Nhan nut de mo camera")
        self.cam.setFixedSize(540, 320)
        self.cam.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cam.setStyleSheet(
            "background:#13151c;border:2px solid #252840;"
            "border-radius:12px;color:#4a5568;font-size:14px;")
        root.addWidget(self.cam, alignment=Qt.AlignmentFlag.AlignCenter)

        self.pb = QProgressBar()
        self.pb.setRange(0,40); self.pb.setValue(0); self.pb.setFixedHeight(18)
        self.pb.setStyleSheet("""
            QProgressBar{background:#13151c;border-radius:9px;color:white;
                font-size:11px;font-weight:700;}
            QProgressBar::chunk{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 #6d28d9,stop:1 #4ade80);border-radius:9px;}
        """)
        root.addWidget(self.pb)

        self.st = QLabel("San sang dang ky")
        self.st.setStyleSheet("font-size:12px;color:#64748b;")
        self.st.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self.st)

        bh = QHBoxLayout(); bh.setSpacing(10)
        self.btn = QPushButton("📷  Bat dau quet khuon mat")
        self.btn.setObjectName("s")
        self.btn.clicked.connect(self._start)
        b2 = QPushButton("Bo qua")
        b2.setObjectName("c")
        b2.clicked.connect(self._cancel)
        bh.addWidget(self.btn,2); bh.addWidget(b2,1)
        root.addLayout(bh)

    def _start(self):
        self.btn.setEnabled(False)
        self.btn.setText("Dang quet...")
        self.st.setText("Nhin thang vao camera...")
        self.st.setStyleSheet("font-size:12px;color:#fbbf24;font-weight:600;")

        self._thread = CameraThread("register", self.nv_id)
        self._thread.frame_ready.connect(self._show)
        self._thread.register_done.connect(self._save)
        self._thread.error_msg.connect(self._err)
        self._thread.start()

    def _show(self, frame):
        n = self._thread.count if self._thread else 0
        self.pb.setValue(n)
        self.st.setText(f"Dang chup... {n}/40")
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h,w,c = rgb.shape
        img = QImage(rgb.data, w, h, w*c, QImage.Format.Format_RGB888)
        self.cam.setPixmap(QPixmap.fromImage(img).scaled(
            540,320,Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation))

    def _save(self):
        try:
            faces  = self._thread.faces
            labels = self._thread.labels

            nv_dir = os.path.join(FACE_DIR, f"nv_{self.nv_id}")
            os.makedirs(nv_dir, exist_ok=True)
            for i,f in enumerate(faces):
                cv2.imwrite(os.path.join(nv_dir,f"face_{i}.jpg"), f)

            all_f, all_l = [], []
            ld = _load_labels()
            for nid in ld.keys():
                d = os.path.join(FACE_DIR, f"nv_{nid}")
                if os.path.exists(d):
                    for fn in os.listdir(d):
                        img = cv2.imread(os.path.join(d,fn), cv2.IMREAD_GRAYSCALE)
                        if img is not None:
                            all_f.append(cv2.resize(img,(200,200)))
                            all_l.append(nid)

            all_f += faces; all_l += labels
            rec = cv2.face.LBPHFaceRecognizer_create()
            rec.train(all_f, np.array(all_l))
            rec.save(MODEL_PATH)
            ld[self.nv_id] = self.ho_ten
            _save_labels(ld)

            self.cam.setText("✅  Dang ky thanh cong!")
            self.cam.setStyleSheet(
                "background:#052e16;border:2px solid #4ade80;"
                "border-radius:12px;color:#4ade80;font-size:18px;font-weight:700;")
            self.pb.setValue(40)
            self.st.setText("✅ Da luu khuon mat!")
            self.st.setStyleSheet("font-size:13px;color:#4ade80;font-weight:700;")
            QMessageBox.information(self,"✅ Thanh cong!",
                f"Da dang ky khuon mat cho {self.ho_ten}!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self,"Loi",str(e))
            self.btn.setEnabled(True)
            self.btn.setText("📷  Bat dau quet khuon mat")

    def _err(self, msg):
        QMessageBox.critical(self,"Loi Camera",msg)
        self.btn.setEnabled(True)
        self.btn.setText("📷  Bat dau quet khuon mat")

    def _cancel(self):
        if self._thread: self._thread.stop()
        self.reject()

    def closeEvent(self, e):
        if self._thread: self._thread.stop()
        super().closeEvent(e)


# ══════════════════════════════════════════════════════════════
# DIALOG CHAM CONG BANG KHUON MAT
# ══════════════════════════════════════════════════════════════
class FaceChamCongDialog(QDialog):
    cham_cong_success = pyqtSignal(int, str)

    def __init__(self, parent=None, nv_id=None, ho_ten=""):
        super().__init__(parent)
        self.nv_id   = nv_id
        self.ho_ten  = ho_ten
        self._thread = None
        self._count  = 0
        self._done   = False
        self.setWindowTitle("Cham cong khuon mat")
        self.setMinimumSize(560, 460)
        self.setStyleSheet("""
            QDialog{background:#0f1117;}
            QLabel{background:transparent;color:#e2e8f0;}
            QPushButton#s{background:#059669;color:white;border:none;
                border-radius:10px;font-size:14px;font-weight:700;padding:12px 28px;}
            QPushButton#s:hover{background:#10b981;}
            QPushButton#c{background:#1e2236;color:#9ca3af;
                border:1px solid #2c3050;border-radius:10px;font-size:13px;padding:11px 24px;}
        """)
        self._build()
        QTimer.singleShot(300, self._start)

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20,16,20,20); root.setSpacing(14)

        t = QLabel("🎥  Cham cong bang khuon mat")
        t.setStyleSheet("font-size:16px;font-weight:800;color:#4ade80;")
        t.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(t)

        sub = QLabel("Nhin thang vao camera de he thong nhan dien")
        sub.setStyleSheet("font-size:12px;color:#64748b;")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(sub)

        self.cam = QLabel("Dang mo camera...")
        self.cam.setFixedSize(520, 300)
        self.cam.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cam.setStyleSheet(
            "background:#13151c;border:2px solid #252840;"
            "border-radius:12px;color:#4a5568;font-size:14px;")
        root.addWidget(self.cam, alignment=Qt.AlignmentFlag.AlignCenter)

        self.st = QLabel("🔍 Dang khoi dong camera...")
        self.st.setStyleSheet("font-size:14px;color:#fbbf24;font-weight:600;")
        self.st.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self.st)

        bh = QHBoxLayout(); bh.setSpacing(10)
        self.btn = QPushButton("🔄  Quet lai")
        self.btn.setObjectName("s")
        self.btn.clicked.connect(self._restart)
        self.btn.setEnabled(False)
        b2 = QPushButton("Huy")
        b2.setObjectName("c")
        b2.clicked.connect(self._cancel)
        bh.addWidget(self.btn,2); bh.addWidget(b2,1)
        root.addLayout(bh)

    def _start(self):
        if not os.path.exists(MODEL_PATH):
            QMessageBox.warning(self,"Chua dang ky",
                "Chua co du lieu khuon mat!"); return

        self._count = 0
        self._done  = False
        self.btn.setEnabled(False)

        self._thread = CameraThread("recognize", self.nv_id)
        self._thread.frame_ready.connect(self._show)
        self._thread.face_match.connect(self._match)
        self._thread.face_nomatch.connect(self._nomatch)
        self._thread.no_face.connect(self._noface)
        self._thread.error_msg.connect(self._err)
        self._thread.start()

    def _restart(self):
        if self._thread: self._thread.stop()
        self._start()

    def _show(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h,w,c = rgb.shape
        img = QImage(rgb.data, w, h, w*c, QImage.Format.Format_RGB888)
        self.cam.setPixmap(QPixmap.fromImage(img).scaled(
            520,300,Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation))

    def _match(self):
        if self._done: return
        self._count += 1
        self.st.setText(f"✅ Nhan dien duoc! {self._count}/5")
        self.st.setStyleSheet("font-size:14px;color:#4ade80;font-weight:700;")
        if self._count >= 5:
            self._done = True
            if self._thread: self._thread.stop()
            self.cam.setText(f"✅  Cham cong thanh cong!\n{self.ho_ten}")
            self.cam.setStyleSheet(
                "background:#052e16;border:2px solid #4ade80;"
                "border-radius:12px;color:#4ade80;font-size:20px;font-weight:800;")
            self.st.setText(f"✅ Khuon mat khop! {time.strftime('%H:%M:%S')}")
            self.cham_cong_success.emit(self.nv_id, self.ho_ten)
            QTimer.singleShot(1500, self.accept)

    def _nomatch(self):
        if not self._done:
            self._count = 0
            self.st.setText("❌ Khuon mat khong khop! Nhin thang vao camera...")
            self.st.setStyleSheet("font-size:13px;color:#f87171;font-weight:700;")
            self.btn.setEnabled(True)

    def _noface(self):
        if not self._done:
            self.st.setText("🔍 Chua phat hien khuon mat...")
            self.st.setStyleSheet("font-size:13px;color:#fbbf24;font-weight:600;")

    def _err(self, msg):
        QMessageBox.critical(self,"Loi Camera",msg)
        self.btn.setEnabled(True)

    def _cancel(self):
        if self._thread: self._thread.stop()
        self.reject()

    def closeEvent(self, e):
        if self._thread: self._thread.stop()
        super().closeEvent(e)