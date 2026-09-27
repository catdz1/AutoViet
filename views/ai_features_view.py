"""
views/ai_features_view.py — Dự báo doanh thu AI + Tìm ảnh xe
Fixed: Tìm ảnh dùng Unsplash + Wikipedia + fallback
"""
import sys, os, json, urllib.request, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTabWidget, QFrame, QScrollArea, QProgressBar,
    QLineEdit, QMessageBox, QComboBox, QGridLayout
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QColor, QPixmap
from database import get_conn
import matplotlib
matplotlib.use("QtAgg")
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from datetime import datetime

STYLE = """
QWidget{font-family:'Segoe UI',Arial;}
QTabWidget::pane{border:none;}
QTabBar::tab{padding:10px 20px;font-size:12px;font-weight:600;
    color:#64748b;background:#1a1d28;border:none;border-bottom:2px solid transparent;}
QTabBar::tab:selected{color:#a78bfa;border-bottom:2px solid #7c3aed;}
QTabBar::tab:hover{color:#c8d0e0;background:#252a42;}
QPushButton#btn_predict{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,
    stop:0 #6d28d9,stop:1 #7c3aed);color:white;border:none;border-radius:10px;
    font-size:14px;font-weight:700;padding:12px 24px;}
QPushButton#btn_predict:hover{background:#7c3aed;}
QPushButton#btn_find_img{background:#1e3a5f;color:#60a5fa;border:1px solid #1e3a5f;
    border-radius:10px;font-size:13px;font-weight:600;padding:10px 20px;}
QPushButton#btn_find_img:hover{background:#1d4ed8;color:white;}
QPushButton#btn_apply_img{background:#052e16;color:#86efac;border:1px solid #166534;
    border-radius:8px;font-size:12px;padding:8px 16px;font-weight:600;}
QLineEdit{background:#1e2236;color:#e2e8f0;border:1px solid #2c3050;
    border-radius:8px;padding:9px 12px;font-size:13px;}
QLineEdit:focus{border-color:#7c3aed;}
QComboBox{background:#1e2236;color:#9ca3af;border:1px solid #2c3050;
    border-radius:8px;padding:8px 12px;font-size:12px;}
QWidget#result_card{background:#1a1d28;border-radius:12px;border:1px solid #252840;}
QWidget#img_card{background:#13151c;border-radius:10px;border:1px solid #252840;}
QWidget#img_card:hover{border-color:#7c3aed;}
QProgressBar{background:#1e2236;border-radius:6px;height:6px;}
QProgressBar::chunk{background:#7c3aed;border-radius:6px;}
"""


class ForecastWorker(QThread):
    result_ready = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, history_data):
        super().__init__()
        self.history_data = history_data

    def run(self):
        try:
            import numpy as np
            data = self.history_data
            if len(data) < 2:
                avg = sum(d["dt"] for d in data) / len(data) if data else 0
                self.result_ready.emit({
                    "method":"Trung bình đơn giản","du_bao":avg,
                    "do_tin_cay":60,"xu_huong":"ổn định",
                    "tang_truong":0,"slope":0,
                    "note":"Cần thêm dữ liệu để dự báo chính xác hơn"
                }); return

            x = np.array([d["thang"] for d in data])
            y = np.array([d["dt"] for d in data])
            n = len(x)
            slope = (n*np.sum(x*y)-np.sum(x)*np.sum(y))/(n*np.sum(x**2)-np.sum(x)**2)
            intercept = (np.sum(y)-slope*np.sum(x))/n
            next_m = max(x)+1
            du_bao = max(0, slope*next_m+intercept)
            y_pred = slope*x+intercept
            ss_res = np.sum((y-y_pred)**2)
            ss_tot = np.sum((y-np.mean(y))**2)
            r2 = 1-(ss_res/ss_tot) if ss_tot>0 else 0
            do_tin_cay = min(95,max(50,int(r2*100)))
            if slope>1e7: xu="📈 Tăng mạnh"
            elif slope>0: xu="📈 Tăng nhẹ"
            elif slope>-1e7: xu="📉 Giảm nhẹ"
            else: xu="📉 Giảm mạnh"
            last_dt = data[-1]["dt"] if data else 0
            tang = ((du_bao-last_dt)/last_dt*100) if last_dt>0 else 0
            self.result_ready.emit({
                "method":"Linear Regression (AI)","du_bao":du_bao,
                "do_tin_cay":do_tin_cay,"xu_huong":xu,"tang_truong":tang,
                "slope":slope,"note":f"Dựa trên {len(data)} tháng dữ liệu"
            })
        except Exception as e:
            self.error.emit(str(e))


class ImageSearchWorker(QThread):
    """Tìm ảnh xe từ nhiều nguồn"""
    images_ready = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, query, local_paths=None):
        super().__init__()
        self.query = query
        self.local_paths = local_paths or []  # Ảnh đã có trong DB

    def run(self):
        images = []

        # 1. Ảnh từ DB (đã có sẵn)
        for path in self.local_paths:
            if path and os.path.exists(path):
                images.append({
                    "url": None,
                    "local_path": path,
                    "title": "Ảnh hiện tại trong hệ thống",
                    "source": "local"
                })

        # 2. Tìm từ Unsplash (free, không cần key)
        try:
            q = urllib.parse.quote(f"{self.query} car")
            url = f"https://source.unsplash.com/800x500/?{q}"
            # Unsplash redirect → lấy URL thực
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            req.get_method = lambda: 'HEAD'
            with urllib.request.urlopen(req, timeout=8) as r:
                final_url = r.url
                if "unsplash.com/photos" in final_url or "images.unsplash" in final_url:
                    images.append({
                        "url": final_url,
                        "local_path": None,
                        "title": f"{self.query} - Unsplash",
                        "source": "unsplash"
                    })
        except Exception: pass

        # 3. Thêm nhiều ảnh Unsplash với từ khóa khác
        keywords = [
            f"{self.query} automobile",
            f"{self.query} vehicle",
            f"{self.query} sedan",
        ]
        for kw in keywords:
            try:
                q = urllib.parse.quote(kw)
                url = f"https://source.unsplash.com/featured/800x500/?{q}"
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                req.get_method = lambda: 'HEAD'
                with urllib.request.urlopen(req, timeout=6) as r:
                    final_url = r.url
                    if final_url not in [img.get("url") for img in images]:
                        images.append({
                            "url": final_url,
                            "local_path": None,
                            "title": f"{kw}",
                            "source": "unsplash"
                        })
            except Exception: pass

        # 4. Wikipedia thumbnail
        try:
            brand = self.query.split()[0]  # Lấy tên hãng
            wiki_q = urllib.parse.quote(f"{self.query}")
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{wiki_q}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=6) as r:
                data = json.loads(r.read())
                thumb = data.get("thumbnail", {}).get("source")
                if thumb:
                    images.append({
                        "url": thumb,
                        "local_path": None,
                        "title": f"Wikipedia: {self.query}",
                        "source": "wikipedia"
                    })
        except Exception: pass

        self.images_ready.emit(images)


class AIFeaturesView(QWidget):
    def __init__(self, current_user=None):
        super().__init__()
        self.setObjectName("page_ai")
        self.setStyleSheet(STYLE)
        self.current_user = current_user or {}
        self._xe_ids = {}
        self._build()
    def _build(self):
        root = QVBoxLayout(self); root.setContentsMargins(0,0,0,0); root.setSpacing(0)
        # Header
        hdr = QWidget(); hdr.setStyleSheet("background:#ffffff;border-bottom:2px solid #e2e8f0;")
        hl = QHBoxLayout(hdr); hl.setContentsMargins(20,14,20,14)
        title = QLabel("🤖  Tính năng AI — Trí tuệ nhân tạo")
        title.setStyleSheet("font-size:17px;font-weight:700;color:#0f172a;background:transparent;")
        sub = QLabel("Dự báo doanh thu & Tìm ảnh xe tự động")
        sub.setStyleSheet("font-size:12px;color:#64748b;font-weight:500;background:transparent;")
        hl.addWidget(title); hl.addStretch(); hl.addWidget(sub)
        root.addWidget(hdr)
        tabs = QTabWidget(); tabs.setStyleSheet(STYLE)
        tabs.addTab(self._build_forecast_tab(), "📊  Dự báo doanh thu AI")
        tabs.addTab(self._build_image_tab(),    "🖼️  Tìm ảnh xe tự động")
        root.addWidget(tabs)
    def _build_forecast_tab(self):
        w = QWidget(); lv = QVBoxLayout(w)
        lv.setContentsMargins(20,16,20,16); lv.setSpacing(14)
        hr = QHBoxLayout()
        t = QLabel("📊  Dự báo doanh thu tháng tới bằng AI")
        t.setStyleSheet("font-size:14px;font-weight:700;color:#0f172a;background:transparent;")
        self.cmb_year = QComboBox()
        cur_y = datetime.now().year
        for y in range(cur_y, cur_y-3, -1): self.cmb_year.addItem(str(y), y)
        self.btn_predict = QPushButton("🤖  Dự báo ngay")
        self.btn_predict.setObjectName("btn_predict")
        self.btn_predict.clicked.connect(self._run_forecast)
        hr.addWidget(t); hr.addStretch()
        hr.addWidget(QLabel("Năm:")); hr.addWidget(self.cmb_year)
        hr.addWidget(self.btn_predict)
        lv.addLayout(hr)
        # Cards
        ch = QHBoxLayout(); ch.setSpacing(10)
        self.fc_du_bao   = self._card("🎯","DỰ BÁO THÁNG TỚI","—","#a78bfa")
        self.fc_tin_cay  = self._card("📊","ĐỘ TIN CẬY","—","#60a5fa")
        self.fc_xu_huong = self._card("📈","XU HƯỚNG","—","#4ade80")
        self.fc_tang     = self._card("💹","TĂNG TRƯỞNG","—","#f59e0b")
        for c in [self.fc_du_bao,self.fc_tin_cay,self.fc_xu_huong,self.fc_tang]:
            ch.addWidget(c)
        lv.addLayout(ch)

        self.fc_loading = QProgressBar()
        self.fc_loading.setRange(0,0); self.fc_loading.hide()
        lv.addWidget(self.fc_loading)

        self.fc_fig = Figure(facecolor="#ffffff", figsize=(10,3.5))
        self.fc_canvas = FigureCanvasQTAgg(self.fc_fig)
        self.fc_canvas.setStyleSheet("border-radius:12px;border:1px solid #e2e8f0;")
        self.fc_canvas.setMinimumHeight(300)
        lv.addWidget(self.fc_canvas)

        self.fc_note = QLabel("ℹ️  Nhấn 'Dự báo ngay' để AI phân tích dữ liệu lịch sử")
        self.fc_note.setStyleSheet("color:#475569;font-size:12px;background:transparent;font-style:italic;")
        lv.addWidget(self.fc_note)
        return w

    def _card(self, icon, label, val, color):
        w = QWidget(); w.setObjectName("result_card")
        w.setStyleSheet(f"QWidget#result_card{{background:#ffffff;border-radius:12px;"
                        f"border:1px solid #e2e8f0;border-top:4px solid {color};}}")
        lv = QVBoxLayout(w); lv.setContentsMargins(16,12,16,12); lv.setSpacing(3)
        li = QLabel(icon); li.setStyleSheet("font-size:18px;background:transparent;")
        ll = QLabel(label);
        ll.setStyleSheet("font-size:11px;color:#0f172a;font-weight:900;"
                         "letter-spacing:0.5px;background:transparent;text-align:center;")
        vl = QLabel(val); vl.setStyleSheet(f"font-size:20px;font-weight:800;color:{color};"
                                           "background:transparent;")
        lv.addWidget(li); lv.addWidget(ll); lv.addWidget(vl)
        w._val = vl; return w

    def _run_forecast(self):
        year = self.cmb_year.currentData()
        conn = get_conn()
        history = []
        for m in range(1,13):
            dt = conn.execute("""
                SELECT COALESCE(SUM(gia_ban_thuc),0) FROM don_hang
                WHERE trang_thai IN ('Đã thanh toán','Đã giao xe')
                AND strftime('%Y-%m',ngay_dat)=?
            """, (f"{year}-{m:02d}",)).fetchone()[0]
            if dt > 0: history.append({"thang":m,"dt":dt})
        conn.close()

        if not history:
            QMessageBox.warning(self,"","Chưa có dữ liệu doanh thu để dự báo!"); return

        self.btn_predict.setEnabled(False); self.fc_loading.show()
        self.fc_note.setText("🤖 AI đang phân tích dữ liệu...")

        self._fc_worker = ForecastWorker(history)
        self._fc_worker.result_ready.connect(lambda r: self._show_forecast(r, history, year))
        self._fc_worker.error.connect(lambda e: (
            self.fc_note.setText(f"❌ {e}"),
            self.btn_predict.setEnabled(True),
            self.fc_loading.hide()))
        self._fc_worker.start()

    def _show_forecast(self, result, history, year):
        self.fc_loading.hide(); self.btn_predict.setEnabled(True)
        import numpy as np
        du_bao = result["du_bao"]
        do_tc  = result.get("do_tin_cay",0)
        xu     = result.get("xu_huong","—")
        tang   = result.get("tang_truong",0)

        self.fc_du_bao._val.setText(f"{du_bao/1e9:.3f} tỷ")
        self.fc_tin_cay._val.setText(f"{do_tc}%")
        self.fc_xu_huong._val.setText(xu)
        self.fc_tang._val.setText(f"{'+' if tang>=0 else ''}{tang:.1f}%")
        self.fc_tang._val.setStyleSheet(
            f"font-size:17px;font-weight:700;background:transparent;"
            f"color:{'#4ade80' if tang>=0 else '#f87171'};")
        self.fc_note.setText(f"✅ {result['note']} | {result['method']}")

        self.fc_fig.clear()
        ax = self.fc_fig.add_subplot(111)
        ax.set_facecolor("#f8fafc"); self.fc_fig.set_facecolor("#ffffff")
        x_hist = [d["thang"] for d in history]
        y_hist = [d["dt"]/1e9 for d in history]
        next_m = max(x_hist)+1
        ax.bar(x_hist, y_hist, color="#3d2a8a", width=0.6, label="Thực tế", zorder=3)
        ax.plot(x_hist, y_hist, "o-", color="#7c3aed", linewidth=2, markersize=6, zorder=4)
        ax.bar([next_m],[du_bao/1e9], color="#4ade80", width=0.6,
               label=f"Dự báo T{next_m}", alpha=0.8, zorder=3)
        ax.text(next_m, du_bao/1e9+0.01, f"{du_bao/1e9:.2f}",
                ha="center", color="#4ade80", fontsize=10, fontweight="bold")
        if len(x_hist) > 1:
            slope = result.get("slope",0)
            x_all = x_hist+[next_m]
            y0 = y_hist[0]-slope/1e9*x_hist[0]
            ax.plot(x_all,[slope/1e9*xi+y0 for xi in x_all],
                    "--", color="#f59e0b", linewidth=1.5, alpha=0.7, label="Xu hướng")
        ax.set_xticks(x_hist+[next_m])
        ax.set_xticklabels([f"T{i}" for i in x_hist]+[f"T{next_m}★"],
                           color="#64748b", fontsize=8)
        ax.tick_params(colors="#64748b"); ax.spines[:].set_visible(False)
        ax.yaxis.set_visible(False)
        ax.legend(loc="upper left", facecolor="#ffffff", edgecolor="#e2e8f0",
                  labelcolor="#94a3b8", fontsize=9)
        self.fc_fig.text(0.5,0.96,f"Dự báo doanh thu {year} (tỷ ₫) — AI Prediction",
                         ha="center",color="#94a3b8",fontsize=10,fontweight="bold")
        self.fc_canvas.draw()

    def _build_image_tab(self):
        w = QWidget(); lv = QVBoxLayout(w)
        lv.setContentsMargins(20,16,20,16); lv.setSpacing(14)

        t = QLabel("🖼️  Tìm ảnh xe tự động từ Internet")
        t.setStyleSheet("font-size:14px;font-weight:700;color:#e2e8f0;background:transparent;")
        lv.addWidget(t)

        sr = QHBoxLayout(); sr.setSpacing(10)

        # Chọn xe từ DB
        self.cmb_xe = QComboBox()
        self.cmb_xe.addItem("-- Chọn xe cần tìm ảnh --", "")
        conn = get_conn()
        xe_rows = conn.execute("SELECT id,hang_xe,dong_xe,anh_url FROM xe ORDER BY id DESC").fetchall()
        for r in xe_rows:
            self.cmb_xe.addItem(f"{r[1]} {r[2]}", r[0])
            self._xe_ids[r[0]] = {
                "name": f"{r[1]} {r[2]}",
                "anh_url": r[3] or ""
            }
        conn.close()
        self.cmb_xe.currentIndexChanged.connect(self._on_xe_select)
        self.cmb_xe.setMinimumWidth(220)

        self.img_inp = QLineEdit()
        self.img_inp.setPlaceholderText("Hoặc nhập tên xe... VD: Toyota Camry 2024")
        self.img_inp.returnPressed.connect(self._find_images)

        self.btn_find = QPushButton("🔍  Tìm ảnh"); self.btn_find.setObjectName("btn_find_img")
        self.btn_find.clicked.connect(self._find_images)

        sr.addWidget(self.cmb_xe,1); sr.addWidget(self.img_inp,2); sr.addWidget(self.btn_find)
        lv.addLayout(sr)

        self.img_loading = QProgressBar()
        self.img_loading.setRange(0,0); self.img_loading.hide()
        lv.addWidget(self.img_loading)

        self.img_status = QLabel("🔍  Chọn xe từ danh sách hoặc nhập tên rồi nhấn 'Tìm ảnh'")
        self.img_status.setStyleSheet("color:#475569;font-size:12px;font-weight:500;background:transparent;")
        lv.addWidget(self.img_status)

        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.img_container = QWidget()
        self.img_grid = QGridLayout(self.img_container)
        self.img_grid.setContentsMargins(0,0,0,0); self.img_grid.setSpacing(12)
        scroll.setWidget(self.img_container)
        lv.addWidget(scroll,1)

        note = QLabel("💡 Tip: Chọn ảnh → nhấn '✅ Áp dụng' để đặt làm ảnh xe trong Showroom")
        note.setStyleSheet("color:#374151;font-size:11px;background:transparent;padding:4px;")
        lv.addWidget(note)
        return w

    def _on_xe_select(self, idx):
        xe_id = self.cmb_xe.currentData()
        if xe_id and xe_id in self._xe_ids:
            self.img_inp.setText(self._xe_ids[xe_id]["name"])

    def _find_images(self):
        q = self.img_inp.text().strip()
        if not q: QMessageBox.warning(self,"","Nhập tên xe hoặc chọn từ danh sách!"); return

        xe_id = self.cmb_xe.currentData()
        local_paths = []
        if xe_id and xe_id in self._xe_ids:
            local_paths = [self._xe_ids[xe_id]["anh_url"]]

        self.btn_find.setEnabled(False); self.img_loading.show()
        self.img_status.setText(f"🔍 Đang tìm ảnh cho '{q}'...")

        while self.img_grid.count():
            item = self.img_grid.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        self._img_worker = ImageSearchWorker(q, local_paths)
        self._img_worker.images_ready.connect(lambda imgs: self._show_images(imgs, q))
        self._img_worker.error.connect(self._on_img_error)
        self._img_worker.start()

    def _show_images(self, images, query):
        self.img_loading.hide(); self.btn_find.setEnabled(True)

        if not images:
            self.img_status.setText(
                f"⚠️ Không tìm thấy ảnh cho '{query}'.\n"
                f"Bạn có thể thêm ảnh thủ công trong Showroom xe → Chi tiết → Thêm/Đổi ảnh.")
            ph = QLabel(f"🚗\n{query}\n\nKhông tìm thấy ảnh tự động.\n"
                        f"Hãy tải ảnh thủ công trong Showroom xe.")
            ph.setAlignment(Qt.AlignmentFlag.AlignCenter)
            ph.setStyleSheet("color:#4a5568;font-size:13px;background:#1a1d28;"
                             "border-radius:12px;padding:40px;")
            self.img_grid.addWidget(ph,0,0,1,3); return

        self.img_status.setText(
            f"✅ Tìm thấy {len(images)} ảnh cho '{query}' — Click '✅ Áp dụng' để dùng")
        cols = 3
        for idx, img in enumerate(images):
            card = self._make_img_card(img, query)
            self.img_grid.addWidget(card, idx//cols, idx%cols)

    def _make_img_card(self, img_data, query):
        card = QWidget(); card.setObjectName("img_card")
        card.setFixedHeight(220)
        lv = QVBoxLayout(card); lv.setContentsMargins(8,8,8,8); lv.setSpacing(6)

        img_lbl = QLabel()
        img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        img_lbl.setFixedHeight(140)
        img_lbl.setStyleSheet("background:#1a1d28;border-radius:8px;color:#4a5568;font-size:12px;")

        source = img_data.get("source","")
        if source == "local":
            # Ảnh đã có trong hệ thống
            pix = QPixmap(img_data["local_path"])
            if not pix.isNull():
                pix = pix.scaled(280,140,Qt.AspectRatioMode.KeepAspectRatio,
                                  Qt.TransformationMode.SmoothTransformation)
                img_lbl.setPixmap(pix)
            badge = "📁 Ảnh hiện tại"
        else:
            img_lbl.setText("⏳ Đang tải...")
            if img_data.get("url"):
                self._load_img_async(img_lbl, img_data["url"])
            badge = "🌐 Tìm tự động"

        title = QLabel(img_data.get("title","")[:45])
        title.setStyleSheet("font-size:10px;color:#64748b;background:transparent;")
        title.setWordWrap(True)

        btn_row = QHBoxLayout(); btn_row.setSpacing(4)
        badge_lbl = QLabel(badge)
        badge_lbl.setStyleSheet("font-size:10px;color:#4a5568;background:transparent;")
        btn_apply = QPushButton("✅ Áp dụng"); btn_apply.setObjectName("btn_apply_img")
        btn_apply.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_apply.clicked.connect(
            lambda _, d=img_data, q=query: self._apply_image(d, q))
        btn_row.addWidget(badge_lbl); btn_row.addStretch(); btn_row.addWidget(btn_apply)

        lv.addWidget(img_lbl,1); lv.addWidget(title); lv.addLayout(btn_row)
        return card

    def _load_img_async(self, lbl, url):
        class ImgLoader(QThread):
            done = pyqtSignal(bytes)
            def __init__(self, url): super().__init__(); self.url=url
            def run(self):
                try:
                    req=urllib.request.Request(self.url,
                        headers={"User-Agent":"Mozilla/5.0"})
                    with urllib.request.urlopen(req,timeout=8) as r:
                        self.done.emit(r.read())
                except Exception: self.done.emit(b"")

        def set_img(data):
            if data:
                pix=QPixmap(); pix.loadFromData(data)
                if not pix.isNull():
                    pix=pix.scaled(280,140,Qt.AspectRatioMode.KeepAspectRatio,
                                   Qt.TransformationMode.SmoothTransformation)
                    lbl.setPixmap(pix); lbl.setText("")
                    return
            lbl.setText("❌ Không tải được")

        loader=ImgLoader(url); loader.done.connect(set_img); loader.start()
        if not hasattr(self,"_img_loaders"): self._img_loaders=[]
        self._img_loaders.append(loader)

    def _apply_image(self, img_data, query):
        xe_id = self.cmb_xe.currentData()
        if not xe_id:
            QMessageBox.warning(self,"","Chọn xe từ danh sách trước khi áp dụng!"); return

        xe_name = self._xe_ids.get(xe_id,{}).get("name","xe")

        if img_data.get("source") == "local":
            # Ảnh đã có sẵn → không cần làm gì
            QMessageBox.information(self,"ℹ️","Đây là ảnh đang dùng cho xe này!")
            return

        try:
            # Tải ảnh về máy
            save_dir = "xe_images"
            os.makedirs(save_dir, exist_ok=True)
            import time
            fname = f"{save_dir}/xe_{xe_id}_{int(time.time())}.jpg"

            url = img_data.get("url")
            if not url:
                QMessageBox.warning(self,"","Không có URL ảnh!"); return

            req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as r:
                with open(fname,"wb") as f: f.write(r.read())

            abs_path = os.path.abspath(fname)
            conn = get_conn()
            conn.execute("UPDATE xe SET anh_url=? WHERE id=?", (abs_path, xe_id))
            conn.commit(); conn.close()

            # Cập nhật local cache
            self._xe_ids[xe_id]["anh_url"] = abs_path

            QMessageBox.information(self,"✅ Thành công!",
                f"Đã cập nhật ảnh cho xe '{xe_name}'!\n\n"
                f"Vào Showroom xe để xem kết quả!")
        except Exception as e:
            QMessageBox.critical(self,"Lỗi",f"Không thể tải ảnh:\n{str(e)}")

    def _on_img_error(self, err):
        self.img_loading.hide(); self.btn_find.setEnabled(True)
        self.img_status.setText(f"❌ Lỗi: {err}")

    def refresh(self): pass