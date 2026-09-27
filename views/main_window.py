"""
views/main_window.py — FINAL + AI Features
THAY THẾ views/main_window.py cũ
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QTreeWidget, QTreeWidgetItem, QStackedWidget,
    QMessageBox, QApplication
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction
from database import get_conn
from style import DARK


class MainWindow(QMainWindow):
    def __init__(self, current_user=None):
        super().__init__()
        self.current_user = current_user or {
            "ho_ten":"Người dùng","role":"nhanvien",
            "username":"guest","id":None,"nv_id":None}
        self.is_admin = self.current_user.get("role") == "admin"
        self._should_logout = False

        # Load API key
        try:
            if os.path.exists("api_config.txt"):
                with open("api_config.txt") as f:
                    for line in f:
                        if line.startswith("ANTHROPIC_API_KEY="):
                            key = line.split("=",1)[1].strip()
                            if key: os.environ["ANTHROPIC_API_KEY"] = key
        except Exception: pass

        self.setWindowTitle("AutoViet ")
        # Tự co giãn kích thước cửa sổ theo màn hình thực tế (tránh tràn màn hình laptop nhỏ/scaling cao)
        screen = QApplication.primaryScreen().availableGeometry()
        w = min(1400, int(screen.width() * 0.92))
        h = min(860, int(screen.height() * 0.88))
        min_w = min(1280, int(screen.width() * 0.85))
        min_h = min(720, int(screen.height() * 0.75))
        self.setMinimumSize(min_w, min_h)
        self.resize(w, h)
        self.setStyleSheet(DARK)

        self._build_ui()
        self._build_menu()
        self._build_statusbar()
        self._init_views()
        self._build_sidebar()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(1000)
        self._refresh_status()

        if self.is_admin: self._nav("Dashboard")
        else: self._nav("KPI của tôi")

    def _build_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        h = QHBoxLayout(central); h.setContentsMargins(0,0,0,0); h.setSpacing(0)

        self.sidebar = QWidget(); self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(200)
        sv = QVBoxLayout(self.sidebar); sv.setContentsMargins(0,0,0,0); sv.setSpacing(0)

        # Logo + Bell
        logo_w = QWidget(); logo_w.setStyleSheet("background:#0a1628;")
        lv2 = QVBoxLayout(logo_w); lv2.setContentsMargins(14,12,14,8); lv2.setSpacing(2)
        logo_row = QHBoxLayout()
        lbl_logo = QLabel("🚗  AutoViet")
        lbl_logo.setStyleSheet("font-size:15px;font-weight:700;color:#a78bfa;background:transparent;")
        try:
            from views.thong_bao_view import BellButton
            self.bell = BellButton(None, self.current_user)
            logo_row.addWidget(lbl_logo); logo_row.addStretch(); logo_row.addWidget(self.bell)
        except Exception: logo_row.addWidget(lbl_logo)
        lbl_sub = QLabel("Quản lý đại lý xe hơi")
        lbl_sub.setStyleSheet("font-size:10px;color:#374151;background:transparent;")
        lv2.addLayout(logo_row); lv2.addWidget(lbl_sub)
        sv.addWidget(logo_w)

        sep = QWidget(); sep.setFixedHeight(1); sep.setStyleSheet("background:rgba(255,255,255,0.08);")
        sv.addWidget(sep)

        self.tree = QTreeWidget(); self.tree.setHeaderHidden(True)
        self.tree.setStyleSheet("""
            QTreeWidget{background:#0f1f35;border:none;padding:4px 0;}
            QTreeWidget::item{height:38px;padding-left:0px;border-radius:8px;margin:2px 2px;}
            QTreeWidget::item:hover{background:#1e3a5f;color:#ffffff;}
            QTreeWidget::item:selected{background:#2563eb;color:#ffffff;font-weight:700;}
            QTreeWidget::branch{background:#0f1f35;}
        """)
        self.tree.itemClicked.connect(self._tree_click)
        sv.addWidget(self.tree,1)
        h.addWidget(self.sidebar)
        self.stack = QStackedWidget(); h.addWidget(self.stack,1)

    def _build_sidebar(self):
        tree = self.tree

        def sec(label):
            item = QTreeWidgetItem(tree)
            lbl = QLabel(f"  {label}")
            lbl.setStyleSheet("font-size:10px;font-weight:700;color:rgba(255,255,255,0.4);"
                              "letter-spacing:1.5px;"
                              "padding:10px 0px 4px 10px;background:transparent;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            tree.setItemWidget(item,0,lbl); item.setFlags(Qt.ItemFlag.NoItemFlags)

        def nav(text, icon=""):
            item = QTreeWidgetItem(tree)
            lbl = QLabel(f"  {icon}  {text}" if icon else f"  {text}")
            lbl.setStyleSheet("background:transparent;color:#ffffff;font-size:12px;font-weight:700;padding:4px 2px 4px 2px;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            tree.setItemWidget(item, 0, lbl);
            item.setData(0, Qt.ItemDataRole.UserRole, text)
            return item

        # Badge
        role_str = "👑 Admin" if self.is_admin else "👤 Nhân viên"
        badge_item = QTreeWidgetItem(tree)
        badge_lbl = QLabel(f"  {role_str}\n  {self.current_user['ho_ten']}")
        badge_lbl.setStyleSheet("background:rgba(109,40,217,.15);color:#a78bfa;"
                                "font-size:12px;font-weight:600;padding:8px 10px;"
                                "border-radius:8px;margin:4px 8px;")
        badge_lbl.setWordWrap(True)
        tree.setItemWidget(badge_item,0,badge_lbl)
        badge_item.setFlags(Qt.ItemFlag.NoItemFlags)

        sec("HỆ THỐNG")
        if self.is_admin:
            nav("Dashboard","📊")
        else:
            nav("KPI của tôi","🎯")

        sec("SHOWROOM")
        nav("Showroom xe","🏪")

        sec("QUẢN LÝ CỚ BẢN")
        nav("Danh sách xe","🚗")
        nav("Khách hàng","👥")
        nav("Đơn hàng","📋")
        nav("Dịch vụ","🔧")

        sec("QUẢN LÝ NHÂN VIÊN")
        if self.is_admin:
            nav("Nhân viên","🧑‍💼")
            nav("Tra lương nhân viên","💵")
            nav("Báo cáo NV","👥")

        sec("MỞ RỘNG")
        nav("Lịch bảo dưỡng", "📅")
        nav("Trả góp", "💳")
        nav("Chấm công", "⏰")  # ← bỏ điều kiện if

        # Cả admin và nhân viên đều thấy
        nav("Thanh toán", "💰")

        sec("AI — TRÍ TUỆ NHÂN TẠO")
        nav("Chatbot tư vấn","🤖")
        nav("AI Phân tích","📊")

        sec("BÁO CÁO")
        nav("Báo cáo","📈")

        if self.is_admin:
            sec("ADMIN")
            nav("Quản lý tài khoản","🔑")

        sec("TÀI KHOẢN")
        nav("Đổi mật khẩu","🔐")

    def _tree_click(self, item, col):
        name = item.data(0, Qt.ItemDataRole.UserRole)
        if name:
            self._nav(name)

    def _init_views(self):
        from views.dashboard_view import DashboardView
        from views.xe_view import XeView
        from views.xe_catalog_view import XeCatalogView
        from views.khach_hang_view import KhachHangView
        from views.don_hang_view import DonHangView
        from views.nhan_vien_view import NhanVienView
        from views.dich_vu_view_new import DichVuView
        from views.bao_cao_view import BaoCaoView

        self.views = {
            "Dashboard":    DashboardView(self.current_user),
            "Showroom xe":  XeCatalogView(),
            "Danh sách xe": XeView(),
            "Khách hàng":   KhachHangView(self.current_user),
            "Đơn hàng":     DonHangView(self.current_user),
            "Nhân viên":    NhanVienView(self.current_user),
            "Dịch vụ":      DichVuView(self.current_user),
            "Báo cáo":      BaoCaoView(self.current_user),
        }

        # NV Dashboard KPI
        if not self.is_admin:
            try:
                from views.dashboard_nv_view import DashboardNVView
                self.views["KPI của tôi"] = DashboardNVView(self.current_user)
            except Exception as e: print(f"DashboardNV: {e}")

        # Lịch bảo dưỡng
        try:
            from views.lich_baoduong_view import LichBaoDuongView
            self.views["Lịch bảo dưỡng"] = LichBaoDuongView(self.current_user)
        except Exception as e: print(f"LichBD: {e}")

        # Trả góp
        try:
            from views.tra_gop_view import TraGopView
            self.views["Trả góp"] = TraGopView(self.current_user)
        except Exception as e: print(f"TraGop: {e}")

        # Chấm công — cả Admin và NV đều load
        try:
            if self.is_admin:
                from views.tra_luong_view import TraLuongView
                self.views["Tra lương nhân viên"] = TraLuongView(self.current_user)
            from views.cham_cong_view import ChamCongView
            self.views["Chấm công"] = ChamCongView(self.current_user)
        except Exception as e:
            import traceback
            print(f"ChamCong ERROR: {e}")
            traceback.print_exc()

        # Thanh toán
        try:
            from views.thanh_toan_view import ThanhToanView
            self.views["Thanh toán"] = ThanhToanView(self.current_user)
        except Exception as e:
            print(f"ThanhToan: {e}")

        # Thanh Toán
        try:
            from views.thanh_toan_view import ThanhToanView
            self.views["Thanh toán"] = ThanhToanView(self.current_user)
        except Exception as e:
            print(f"ThanhToan: {e}")

        # AI Chatbot
        try:
            from views.chatbot_view import ChatbotView
            self.views["Chatbot tư vấn"] = ChatbotView(self.current_user)
        except Exception as e: print(f"Chatbot: {e}")

        # AI Features (Dự báo + Tìm ảnh)
        try:
            from views.ai_features_view import AIFeaturesView
            self.views["AI Phân tích"] = AIFeaturesView(self.current_user)
        except Exception as e: print(f"AIFeatures: {e}")

        if self.is_admin:
            try:
                from views.bao_cao_nhanvien_view import BaoCaoNhanVienView
                self.views["Báo cáo NV"] = BaoCaoNhanVienView()
            except Exception as e: print(f"BaoCaoNV: {e}")
            try:
                from views.user_mgmt_view import UserMgmtView
                self.views["Quản lý tài khoản"] = UserMgmtView()
            except Exception as e: print(f"UserMgmt: {e}")

        for v in self.views.values(): self.stack.addWidget(v)

    def _build_menu(self):
        mb = self.menuBar()
        def menu(t): return mb.addMenu(f"  {t}  ")
        def act(m,t,s=None):
            a=QAction(t,self)
            if s: a.triggered.connect(s)
            m.addAction(a); return a

        m_f=menu("Tệp")
        act(m_f,"💾 Sao lưu",self._backup)
        m_f.addSeparator()
        act(m_f,"🚪 Đăng xuất",self._logout)
        act(m_f,"❌ Thoát",self._quit)

        m_q=menu("Quản lý")
        for t,n in [("🏪 Showroom","Showroom xe"),("🚗 Danh sách xe","Danh sách xe"),
                    ("👥 Khách hàng","Khách hàng"),("📋 Đơn hàng","Đơn hàng"),
                    ("🔧 Dịch vụ","Dịch vụ"),("📅 Lịch bảo dưỡng","Lịch bảo dưỡng"),
                    ("💳 Trả góp","Trả góp")]:
            act(m_q,t,lambda _=False,n=n: self._nav(n))

        m_ai=menu("AI")
        act(m_ai,"🤖 Chatbot tư vấn xe",lambda: self._nav("Chatbot tư vấn"))
        act(m_ai,"📊 Dự báo doanh thu AI",lambda: self._nav("AI Phân tích"))
        act(m_ai,"🖼️ Tìm ảnh xe tự động",lambda: self._nav("AI Phân tích"))

        m_bc=menu("Báo cáo")
        act(m_bc,"📈 Báo cáo tổng hợp",lambda: self._nav("Báo cáo"))
        if self.is_admin:
            act(m_bc,"👥 Báo cáo NV",lambda: self._nav("Báo cáo NV"))

        m_ct=menu("Công cụ")
        act(m_ct,"🔍 Tìm kiếm toàn cục",self._global_search)
        act(m_ct,"🔄 Làm mới",self._refresh_all)
        act(m_ct,"🔐 Đổi mật khẩu",self._doi_matkhau)
        act(m_ct,"💾 Sao lưu DB",self._backup)

        menu("Trợ giúp").addAction(QAction("ℹ Giới thiệu",self,triggered=lambda:
            QMessageBox.information(self,"AutoViet v1.0",
                f"🚗 AutoViet — Hệ thống Quản lý Đại lý Xe Hơi\n\n"
                f"👤 {self.current_user['ho_ten']} | {'Admin' if self.is_admin else 'NV'}\n\n"
                f"🤖 AI: Claude API + Pandas ML\n"
                f"💻 Tech: Python + PyQt6 + SQLite")))

    def _global_search(self):
        from PyQt6.QtWidgets import QInputDialog
        q,ok=QInputDialog.getText(self,"🔍 Tìm kiếm toàn cục","Nhập từ khóa:")
        if not ok or not q.strip(): return
        q=q.strip(); conn=get_conn(); results=[]
        for r in conn.execute("SELECT 'XE' as type,ma_xe as code,hang_xe||' '||dong_xe as name FROM xe WHERE hang_xe LIKE ? OR dong_xe LIKE ? OR ma_xe LIKE ?",[f"%{q}%"]*3).fetchall(): results.append(dict(r))
        for r in conn.execute("SELECT 'KHÁCH HÀNG' as type,ma_kh as code,ho_ten as name FROM khach_hang WHERE ho_ten LIKE ? OR so_dt LIKE ? OR ma_kh LIKE ?",[f"%{q}%"]*3).fetchall(): results.append(dict(r))
        for r in conn.execute("SELECT 'ĐƠN HÀNG' as type,dh.ma_don as code,x.hang_xe||' '||x.dong_xe||' — '||kh.ho_ten as name FROM don_hang dh JOIN xe x ON dh.xe_id=x.id JOIN khach_hang kh ON dh.kh_id=kh.id WHERE dh.ma_don LIKE ? OR kh.ho_ten LIKE ?",[f"%{q}%"]*2).fetchall(): results.append(dict(r))
        conn.close()
        if not results: QMessageBox.information(self,"Kết quả",f"Không tìm thấy: '{q}'"); return
        msg=f"✅ Tìm thấy {len(results)} kết quả:\n\n"
        for r in results[:15]: msg+=f"[{r['type']}]  {r['code']} — {r['name']}\n"
        QMessageBox.information(self,f"🔍 {q}",msg)

    def _stop_all_view_timers(self):
        """Dừng mọi QTimer đang chạy ngầm bên trong các view con trước khi đóng/đăng xuất,
        tránh lỗi 'wrapped C/C++ object has been deleted' khi timer cũ vẫn kích hoạt
        sau khi cửa sổ đã bị huỷ."""
        for v in self.views.values():
            for attr in ("_timer", "_refresh_timer"):
                t = getattr(v, attr, None)
                if t is not None:
                    try: t.stop()
                    except Exception: pass

    def _logout(self):
        if QMessageBox.question(self,"Đăng xuất",f"Đăng xuất '{self.current_user['ho_ten']}'?",
            QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No
        )==QMessageBox.StandardButton.Yes:
            self._should_logout=True; self._timer.stop(); self._stop_all_view_timers(); self.close()

    def _quit(self):
        if QMessageBox.question(self,"Thoát","Thoát chương trình?",
            QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No
        )==QMessageBox.StandardButton.Yes:
            self._should_logout=False; self._timer.stop(); self._stop_all_view_timers(); self.close(); QApplication.quit()

    def _backup(self):
        import shutil; from database import DB_PATH
        dst=DB_PATH.replace(".db",f"_backup_{datetime.now().strftime('%Y%m%d_%H%M')}.db")
        shutil.copy2(DB_PATH,dst)
        QMessageBox.information(self,"✅ Sao lưu",f"Đã sao lưu!\n{dst}")

    def _doi_matkhau(self):
        try:
            print("[_doi_matkhau] Starting...")
            from views.doi_matkhau_view import DoiMatKhauView
            print("[_doi_matkhau] DoiMatKhauView imported successfully")

            view = DoiMatKhauView(is_admin=self.is_admin, user_id=self.current_user.get("id"))
            print(f"[_doi_matkhau] View created: {view}")

            self.views["_temp_doi_matkhau"] = view
            self.stack.addWidget(view)
            self.stack.setCurrentWidget(view)
            print("[_doi_matkhau] View displayed")
        except Exception as e:
            print(f"[_doi_matkhau] Error: {e}")
            import traceback
            traceback.print_exc()

    def _build_statusbar(self):
        sb=self.statusBar()
        self._lbl_stats=QLabel()
        role_str="Admin" if self.is_admin else "NV"
        self._lbl_user=QLabel(f"  {self.current_user['ho_ten']} [{role_str}]  ")
        self._lbl_clock=QLabel()
        sb.addWidget(self._lbl_stats)
        sb.addPermanentWidget(self._lbl_user)
        sb.addPermanentWidget(self._lbl_clock)

    def _refresh_status(self):
        conn=get_conn()
        t=conn.execute("SELECT COUNT(*) FROM xe").fetchone()[0]
        c=conn.execute("SELECT COUNT(*) FROM xe WHERE trang_thai='Còn hàng'").fetchone()[0]
        b=conn.execute("SELECT COUNT(*) FROM xe WHERE trang_thai='Đã bán'").fetchone()[0]
        bd=conn.execute("SELECT COUNT(*) FROM xe WHERE trang_thai='Bảo dưỡng'").fetchone()[0]
        conn.close()
        warn="  ⚠️ TỒN KHO THẤP!" if c<3 else ""
        self._lbl_stats.setText(f"  Tổng: {t} xe  |  Còn: {c}  |  Bán: {b}  |  BD: {bd}{warn}  ")
        self._lbl_stats.setStyleSheet("color:#f87171;font-weight:600;" if c<3 else "")

    def _tick(self): self._lbl_clock.setText(datetime.now().strftime("  %d/%m/%Y  %H:%M:%S  "))

    def _nav(self, name):
        print(f"NAV: {name} | views: {list(self.views.keys())}")  # ← thêm dòng này
        if name=="Đổi mật khẩu": self._doi_matkhau(); return
        v=self.views.get(name)
        if v:
            self.stack.setCurrentWidget(v)
            if hasattr(v,"refresh"): v.refresh()
            self._refresh_status()

    def _refresh_all(self):
        for v in self.views.values():
            if hasattr(v,"refresh"): v.refresh()
        self._refresh_status()