"""
views/chatbot_view.py — Chatbot dùng Cohere API (Miễn phí, ổn định)
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QScrollArea, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from database import get_conn

STYLE = """
QWidget{font-family:'Segoe UI',Arial;}
QWidget#chat_bg{background:#f0f4f8;}
QLineEdit#chat_input{
    background:#ffffff;color:#00274c;
    border:1px solid #dbeafe;border-radius:12px;
    padding:12px 16px;font-size:14px;font-weight:500;}
QLineEdit#chat_input:focus{border-color:#2563eb;}
QPushButton#btn_send{
    background:#2563eb;color:white;border:none;
    border-radius:12px;font-size:16px;font-weight:700;padding:12px 20px;}
QPushButton#btn_send:hover{background:#1d4ed8;}
QPushButton#btn_key{
    background:#eff6ff;color:#1e40af;border:1px solid #bfdbfe;
    border-radius:8px;font-size:12px;font-weight:600;padding:6px 14px;}
QPushButton#btn_key:hover{background:#2563eb;color:white;}
QPushButton#btn_clear{
    background:#fee2e2;color:#991b1b;border:1px solid #fecaca;
    border-radius:8px;font-size:12px;font-weight:600;padding:6px 14px;}
QPushButton#btn_clear:hover{background:#dc2626;color:white;}
QPushButton#btn_suggest{
    background:#ffffff;color:#1e40af;border:1px solid #bfdbfe;
    border-radius:20px;font-size:12px;font-weight:600;padding:6px 14px;}
QPushButton#btn_suggest:hover{background:#eff6ff;border-color:#2563eb;}
"""

SUGGESTIONS = [
    "Xe dưới 500 triệu cho gia đình?",
    "So sánh Toyota và Honda?",
    "Xe SUV tiết kiệm xăng nhất?",
    "Xe nào phù hợp người mới lái?",
]

CONFIG_FILE = "api_config.txt"


def save_api_key(key: str):
    try:
        with open(CONFIG_FILE, "w") as f:
            f.write(f"COHERE_API_KEY={key.strip()}\n")
        os.environ["COHERE_API_KEY"] = key.strip()
    except Exception:
        os.environ["COHERE_API_KEY"] = key.strip()


def load_api_key() -> str:
    key = os.environ.get("COHERE_API_KEY", "")
    if key: return key
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("COHERE_API_KEY="):
                        key = line.split("=", 1)[1].strip()
                        if key:
                            os.environ["COHERE_API_KEY"] = key
                            return key
    except Exception: pass
    return ""


class CohereWorker(QThread):
    response_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, messages, xe_context, api_key):
        super().__init__()
        self.messages   = messages
        self.xe_context = xe_context
        self.api_key    = api_key

    def run(self):
        try:
            import urllib.request

            if not self.api_key:
                self.response_ready.emit(
                    "⚠️ Chưa có API Key!\n\n"
                    "Nhấn 🔑 API Key → nhập Cohere API Key\n"
                    "Lấy miễn phí tại: dashboard.cohere.com/api-keys")
                return

            system = (
                f"Bạn là trợ lý tư vấn xe hơi của đại lý AutoViet. "
                f"Tư vấn xe phù hợp theo nhu cầu và ngân sách. "
                f"Trả lời thân thiện, ngắn gọn bằng tiếng Việt.\n\n"
                f"XE HIỆN CÓ TẠI ĐẠI LÝ:\n{self.xe_context}"
            )

            # ✅ Định dạng messages chuẩn v2 (có system message)
            messages = [{"role": "system", "content": system}]
            for msg in self.messages:
                messages.append({
                    "role": msg["role"],        # "user" hoặc "assistant"
                    "content": msg["content"]
                })

            data = json.dumps({
                "model": "command-r-08-2024",  # ✅ model mới nhất
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 800,
            }).encode("utf-8")

            req = urllib.request.Request(
                "https://api.cohere.com/v2/chat",   # ✅ endpoint v2 đúng
                data=data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}",
                    "Accept": "application/json"
                }
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read())
                # ✅ v2 trả về cấu trúc khác v1
                text = result["message"]["content"][0]["text"]
                self.response_ready.emit(text)

        except Exception as e:
            err = str(e)
            if "401" in err or "403" in err:
                self.response_ready.emit(
                    "❌ API Key không hợp lệ!\n\n"
                    "Nhấn 🔑 API Key → nhập lại key từ:\n"
                    "dashboard.cohere.com/api-keys")
            elif "429" in err:
                self.response_ready.emit(
                    "⏳ Quá nhiều yêu cầu!\nChờ 1 phút rồi thử lại.")
            elif "timeout" in err.lower():
                self.error_occurred.emit("⏱ Timeout! Thử lại.")
            else:
                self.error_occurred.emit(f"Lỗi: {err[:80]}")


class ChatbotView(QWidget):
    def __init__(self, current_user=None):
        super().__init__()
        self.setObjectName("page_chatbot")
        self.setStyleSheet(STYLE)
        self.current_user = current_user or {}
        self._messages   = []
        self._api_key    = load_api_key()
        self._xe_context = self._get_xe_context()
        self._build()
        self._add_welcome()

    def _get_xe_context(self):
        conn = get_conn()
        rows = conn.execute(
            "SELECT hang_xe,dong_xe,nam_sx,gia_ban,mau_sac,trang_thai FROM xe ORDER BY gia_ban"
        ).fetchall()
        conn.close()
        return "\n".join(
            f"- {r[0]} {r[1]} ({r[2]}): {r[3]/1e9:.2f} tỷ | {r[4] or 'N/A'} | {r[5]}"
            for r in rows
        ) or "Chưa có xe"

    def _build(self):
        root = QVBoxLayout(self); root.setContentsMargins(0,0,0,0); root.setSpacing(0)

        hdr = QWidget(); hdr.setStyleSheet("background:#00274c;border-bottom:1px solid #1a3a6b;")
        hl  = QHBoxLayout(hdr); hl.setContentsMargins(20,12,20,12)
        col = QVBoxLayout(); col.setSpacing(1)
        t   = QLabel("🤖  Trợ lý tư vấn xe AutoViet AI")
        t.setStyleSheet("font-size:15px;font-weight:700;color:#ffffff;background:transparent;")
        s   = QLabel("Powered by Cohere AI — Miễn phí, ổn định")
        s.setStyleSheet("font-size:11px;color:rgba(255,255,255,0.6);background:transparent;")
        col.addWidget(t); col.addWidget(s)

        self.status_lbl = QLabel("● Online")
        self.status_lbl.setStyleSheet(
            "color:#4ade80;font-size:12px;font-weight:600;background:transparent;")

        btn_key = QPushButton("🔑 API Key"); btn_key.setObjectName("btn_key")
        btn_key.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_key.clicked.connect(self._set_api_key)
        btn_clr = QPushButton("🗑 Xoá"); btn_clr.setObjectName("btn_clear")
        btn_clr.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_clr.clicked.connect(self._clear)

        hl.addLayout(col,1); hl.addWidget(self.status_lbl)
        hl.addWidget(btn_key); hl.addWidget(btn_clr)
        root.addWidget(hdr)

        self.scroll = QScrollArea(); self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setStyleSheet("background:#f0f4f8;")
        cw = QWidget();
        cw.setObjectName("chat_bg");
        cw.setStyleSheet("background:#f0f4f8;")
        self.chat_lv = QVBoxLayout(cw)
        self.chat_lv.setContentsMargins(16,16,16,16); self.chat_lv.setSpacing(10)
        self.chat_lv.addStretch()
        self.scroll.setWidget(cw)
        root.addWidget(self.scroll,1)

        sg = QWidget(); sg.setStyleSheet("background:#eff6ff;border-top:1px solid #dbeafe;padding:6px 14px;")
        sh = QHBoxLayout(sg); sh.setContentsMargins(0,0,0,0); sh.setSpacing(6)
        sh.addWidget(self._lbl("💡","font-size:14px;"))
        for sug in SUGGESTIONS:
            b = QPushButton(sug); b.setObjectName("btn_suggest")
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.clicked.connect(lambda _,s=sug: self._send(s))
            sh.addWidget(b)
        sh.addStretch()
        root.addWidget(sg)

        iw = QWidget(); iw.setStyleSheet("background:#ffffff;border-top:1px solid #dbeafe;")
        il = QHBoxLayout(iw); il.setContentsMargins(16,10,16,10); il.setSpacing(10)
        self.inp = QLineEdit(); self.inp.setObjectName("chat_input")
        self.inp.setPlaceholderText("Nhập câu hỏi về xe...")
        self.inp.returnPressed.connect(self._on_send)
        self.btn_send = QPushButton("➤"); self.btn_send.setObjectName("btn_send")
        self.btn_send.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_send.clicked.connect(self._on_send)
        il.addWidget(self.inp,1); il.addWidget(self.btn_send)
        root.addWidget(iw)

    def _lbl(self, t, s=""):
        l = QLabel(t); l.setStyleSheet(s+"background:transparent;"); return l

    def _add_welcome(self):
        name = self.current_user.get("ho_ten","bạn")
        key_ok = "✅ Cohere API Key sẵn sàng!" if self._api_key else "⚠️ Chưa có API Key — Nhấn 🔑 để nhập"
        self._add_bot(
            f"Xin chào {name}! 👋\n\n"
            f"Tôi là trợ lý tư vấn xe AI của AutoViet.\n"
            f"Powered by Cohere AI — Miễn phí & ổn định!\n\n"
            f"🚗 Gợi ý xe phù hợp ngân sách\n"
            f"⚖️ So sánh các dòng xe\n"
            f"💰 Tư vấn giá cả, chi phí\n\n"
            f"Hiện có {len(self._xe_context.splitlines())} xe đang bán.\n\n"
            f"{key_ok}"
        )

    def _add_user(self, text):
        from datetime import datetime
        w = QWidget()
        w.setStyleSheet("background:qlineargradient(x1:0,y1:0,x2:1,y2:0,"
                        "stop:0 #6d28d9,stop:1 #7c3aed);border-radius:14px 14px 4px 14px;")
        lv = QVBoxLayout(w); lv.setContentsMargins(0,0,0,0); lv.setSpacing(0)
        lbl = QLabel(text)
        lbl.setStyleSheet("background:transparent;color:white;font-size:13px;padding:10px 14px;")
        lbl.setWordWrap(True)
        tlbl = QLabel(datetime.now().strftime("%H:%M"))
        tlbl.setStyleSheet("background:transparent;color:rgba(255,255,255,.4);font-size:10px;padding:0 14px 6px;")
        lv.addWidget(lbl); lv.addWidget(tlbl)
        row = QHBoxLayout(); row.addStretch(); row.addWidget(w)
        c = QWidget(); c.setStyleSheet("background:transparent;"); c.setLayout(row)
        self.chat_lv.insertWidget(self.chat_lv.count()-1, c)
        self._scroll()

    def _add_bot(self, text):
        from datetime import datetime
        text = text.replace("**","").replace("*","•")
        w = QWidget()
        w.setStyleSheet("background:#ffffff;border-radius:14px 14px 14px 4px;border:1px solid #dbeafe;")
        lv = QVBoxLayout(w); lv.setContentsMargins(0,0,0,0); lv.setSpacing(0)
        av_row = QHBoxLayout(); av_row.setContentsMargins(10,8,10,0)
        av = QLabel("🤖"); av.setStyleSheet("font-size:14px;background:transparent;")
        nm = QLabel("AutoViet AI")
        nm.setStyleSheet("font-size:11px;font-weight:700;color:#1e40af;background:transparent;")
        av_row.addWidget(av); av_row.addWidget(nm); av_row.addStretch()
        lv.addLayout(av_row)
        lbl = QLabel(text)

        lbl.setStyleSheet("background:transparent;color:#00274c;font-size:14px;font-weight:500;padding:6px 14px;")
        lbl.setWordWrap(True);
        lbl.setTextFormat(Qt.TextFormat.PlainText)
        tlbl = QLabel(datetime.now().strftime("%H:%M"))
        tlbl.setStyleSheet("background:transparent;color:#94a3b8;font-size:10px;padding:0 14px 6px;")
        lv.addWidget(lbl); lv.addWidget(tlbl)
        row = QHBoxLayout(); row.addWidget(w); row.addStretch()
        c = QWidget(); c.setStyleSheet("background:transparent;"); c.setLayout(row)
        self.chat_lv.insertWidget(self.chat_lv.count()-1, c)
        self._scroll()

    def _add_typing(self):
        self._typing = QWidget(); self._typing.setStyleSheet("background:transparent;")
        row = QHBoxLayout(self._typing)
        lbl = QLabel("🤖  AutoViet AI đang soạn...")
        lbl.setStyleSheet("background:#ffffff;border-radius:12px;color:#64748b;"
                          "border:1px solid #dbeafe;font-size:13px;padding:10px 16px;")
        row.addWidget(lbl); row.addStretch()
        self.chat_lv.insertWidget(self.chat_lv.count()-1, self._typing)
        self._scroll()

    def _rm_typing(self):
        if hasattr(self,"_typing") and self._typing:
            self._typing.deleteLater(); self._typing = None

    def _scroll(self):
        QTimer.singleShot(100, lambda:
            self.scroll.verticalScrollBar().setValue(
                self.scroll.verticalScrollBar().maximum()))

    def _on_send(self):
        t = self.inp.text().strip()
        if not t: return
        self.inp.clear(); self._send(t)

    def _send(self, text):
        self._api_key = load_api_key()
        self._add_user(text)
        self._messages.append({"role":"user","content":text})
        self.btn_send.setEnabled(False); self.inp.setEnabled(False)
        self.status_lbl.setText("● Đang xử lý...")
        self.status_lbl.setStyleSheet(
            "color:#f59e0b;font-size:12px;font-weight:600;background:transparent;")
        self._add_typing()

        self._worker = CohereWorker(self._messages[-10:], self._xe_context, self._api_key)
        self._worker.response_ready.connect(self._on_resp)
        self._worker.error_occurred.connect(self._on_err)
        self._worker.start()

    def _on_resp(self, text):
        self._rm_typing()
        self._add_bot(text)
        self._show_xe_image(text)
        self._messages.append({"role":"assistant","content":text})
        self.btn_send.setEnabled(True); self.inp.setEnabled(True); self.inp.setFocus()
        self.status_lbl.setText("● Online")
        self.status_lbl.setStyleSheet(
            "color:#4ade80;font-size:12px;font-weight:600;background:transparent;")

    def _on_err(self, err):
        self._rm_typing(); self._add_bot(f"❌ {err}")
        self.btn_send.setEnabled(True); self.inp.setEnabled(True)
        self.status_lbl.setText("● Online")
        self.status_lbl.setStyleSheet(
            "color:#4ade80;font-size:12px;font-weight:600;background:transparent;")

    def _set_api_key(self):
        from PyQt6.QtWidgets import QInputDialog
        k, ok = QInputDialog.getText(
            self, "🔑 Nhập Cohere API Key",
            "Dán API Key từ dashboard.cohere.com/api-keys:",
            QLineEdit.EchoMode.Password, self._api_key or "")
        if ok and k.strip():
            save_api_key(k.strip())
            self._api_key = k.strip()
            QMessageBox.information(self,"✅ Thành công!",
                "Đã lưu Cohere API Key!\nGõ câu hỏi để bắt đầu!")

    def _clear(self):
        self._messages.clear()
        while self.chat_lv.count() > 1:
            item = self.chat_lv.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        self._add_welcome()

    def _clear(self):
        self._messages.clear()
        while self.chat_lv.count() > 1:
            item = self.chat_lv.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        self._add_welcome()

    def _show_xe_image(self, text):  # ← thêm vào đây
        conn = get_conn()
        xe_rows = conn.execute(
            "SELECT hang_xe, dong_xe, anh_url FROM xe WHERE anh_url IS NOT NULL AND anh_url != ''"
        ).fetchall()
        conn.close()
        for xe in xe_rows:
            hang = xe[0].lower();
            dong = xe[1].lower()
            text_lower = text.lower()
            # SAU (đúng) ✅
            full = f"{hang} {dong}"
            if full in text_lower or (len(dong) >= 2 and dong in text_lower):
                anh_url = xe[2]
                if anh_url and os.path.exists(anh_url):
                    self._add_image_bot(xe[0], xe[1], anh_url)
                    break

    def _add_image_bot(self, hang, dong, anh_url):  # ← thêm vào đây
        from datetime import datetime
        from PyQt6.QtGui import QPixmap
        w = QWidget()
        w.setStyleSheet("background:#ffffff;border-radius:14px 14px 14px 4px;border:1px solid #dbeafe;")
        lv = QVBoxLayout(w);
        lv.setContentsMargins(10, 10, 10, 10);
        lv.setSpacing(6)
        hrow = QHBoxLayout()
        av = QLabel("🤖");
        av.setStyleSheet("font-size:14px;background:transparent;")
        nm = QLabel("AutoViet AI")
        nm.setStyleSheet("font-size:11px;font-weight:700;color:#a78bfa;background:transparent;")
        hrow.addWidget(av);
        hrow.addWidget(nm);
        hrow.addStretch()
        lv.addLayout(hrow)
        ten_lbl = QLabel(f"🚗  {hang} {dong}")
        ten_lbl.setStyleSheet("font-size:14px;font-weight:700;color:#00274c;background:transparent;")
        lv.addWidget(ten_lbl)
        img_lbl = QLabel()
        img_lbl.setFixedHeight(180)
        img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        img_lbl.setStyleSheet("background:#f0f4f8;border-radius:8px;border:0.5px solid #dbeafe;")
        px = QPixmap(anh_url)
        if not px.isNull():
            img_lbl.setPixmap(px.scaled(320, 180,
                                        Qt.AspectRatioMode.KeepAspectRatio,
                                        Qt.TransformationMode.SmoothTransformation))
        lv.addWidget(img_lbl)
        tlbl = QLabel(datetime.now().strftime("%H:%M"))
        tlbl.setStyleSheet("color:#94a3b8;font-size:10px;background:transparent;")
        lv.addWidget(tlbl)
        row = QHBoxLayout();
        row.addWidget(w);
        row.addStretch()
        c = QWidget();
        c.setStyleSheet("background:transparent;");
        c.setLayout(row)
        self.chat_lv.insertWidget(self.chat_lv.count() - 1, c)
        self._scroll()
    def refresh(self):
        self._api_key = load_api_key()
        self._xe_context = self._get_xe_context()
