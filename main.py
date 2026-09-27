import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
def run_login(app):
    """Hiện màn hình đăng nhập, trả về user_info hoặc None"""
    from database import init_db, seed_data
    from auth import init_users_table
    init_db()
    # seed_data()   # ĐÃ TẮT — không tự động chèn lại dữ liệu mẫu (xe/khách hàng/đơn hàng...)
                     # mỗi khi khởi động. Muốn seed lại data mẫu thì bỏ comment dòng này.
    init_users_table()
    from views.login_view import LoginDialog
    dlg = LoginDialog()
 
    # Căn giữa màn hình
    screen = app.primaryScreen().geometry()
    dlg.move(
        (screen.width()  - dlg.width())  // 2,
        (screen.height() - dlg.height()) // 2,
    )
    if dlg.exec() and dlg.user_info:
        return dlg.user_info
    return None
def main():
    app = QApplication(sys.argv)
    app.setApplicationName("AutoViet")
    app.setFont(QFont("Segoe UI", 13))
    while True:
        # Hiện màn hình đăng nhập
        user = run_login(app)
        if not user:
            # Người dùng đóng cửa sổ → thoát hẳn
            break
        print(f"[✓] Đăng nhập: {user['ho_ten']} ({user['role']})")
        # Mở cửa sổ chính
        from views.main_window import MainWindow
        win = MainWindow(current_user=user)
        win.show()
        # Chạy app cho đến khi cửa sổ chính đóng
        # MainWindow sẽ set _should_logout=True nếu người dùng đăng xuất
        app.exec()
        # Kiểm tra có muốn đăng xuất không
        if getattr(win, "_should_logout", False):
            # Đăng xuất → vòng lặp while tiếp tục → hiện login lại
            print("[→] Đăng xuất — quay lại màn hình đăng nhập")
            continue
        else:
            # Đóng cửa sổ bình thường → thoát
            break
    sys.exit(0)
if __name__ == "__main__":
   main()
 