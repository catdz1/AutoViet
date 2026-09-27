"""
Cách dùng file .ui với PyQt6:
  - Đặt file .ui cùng thư mục với file .py này
  - Gọi class tương ứng từ file danh_sach_xe.py
"""

import os
from PyQt6.QtWidgets import QDialog, QMessageBox
from PyQt6 import uic


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# ════════════════════════════════════════════════════════════
#  DIALOG THÊM XE
# ════════════════════════════════════════════════════════════
class DialogThemXe(QDialog):
    def __init__(self, parent=None, db_connection=None):
        super().__init__(parent)
        self.conn = db_connection
        uic.loadUi(os.path.join(BASE_DIR, "dialog_them_xe.ui"), self)

        self._auto_generate_id()
        self.btnClose.clicked.connect(self.reject)
        self.btnHuy.clicked.connect(self.reject)
        self.btnLuu.clicked.connect(self._save)

    def _auto_generate_id(self):
        if self.conn:
            try:
                cur = self.conn.cursor()
                cur.execute("SELECT COUNT(*) FROM xe")
                count = cur.fetchone()[0]
                self.txtMaXe.setText(f"XE{count + 1:03d}")
            except Exception:
                self.txtMaXe.setText("XE???")
        else:
            self.txtMaXe.setText("XE009")

    def _save(self):
        if not self.txtTenXe.text().strip():
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập tên xe!")
            self.txtTenXe.setFocus()
            return
        if self.spnGiaBan.value() == 0:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập giá bán!")
            return

        self.xe_data = {
            "ma_xe":      self.txtMaXe.text(),
            "ten_xe":     self.txtTenXe.text().strip(),
            "hang_xe":    self.cmbHang.currentText(),
            "dong_xe":    self.txtDongXe.text().strip(),
            "nam_sx":     self.spnNamSX.value(),
            "mau_sac":    self.txtMauSac.text().strip(),
            "gia_nhap":   self.spnGiaNhap.value(),
            "gia_ban":    self.spnGiaBan.value(),
            "so_khung":   self.txtSoKhung.text().strip(),
            "so_may":     self.txtSoMay.text().strip(),
            "trang_thai": self.cmbTrangThai.currentText(),
            "mo_ta":      self.txtMoTa.toPlainText().strip(),
        }

        if self.conn:
            try:
                cur = self.conn.cursor()
                cur.execute("""
                    INSERT INTO xe (ma_xe, ten_xe, hang_xe, dong_xe, nam_sx, mau_sac,
                                   gia_nhap, gia_ban, so_khung, so_may, trang_thai, mo_ta)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, tuple(self.xe_data.values()))
                self.conn.commit()
            except Exception as e:
                QMessageBox.critical(self, "Lỗi DB", str(e))
                return

        self.accept()


# ════════════════════════════════════════════════════════════
#  DIALOG SỬA XE
# ════════════════════════════════════════════════════════════
class DialogSuaXe(QDialog):
    def __init__(self, parent=None, db_connection=None, xe_data: dict = None):
        super().__init__(parent)
        self.conn = db_connection
        self.xe_data = xe_data or {}
        uic.loadUi(os.path.join(BASE_DIR, "dialog_sua_xe.ui"), self)

        self._load_data()
        self.btnClose.clicked.connect(self.reject)
        self.btnHuy.clicked.connect(self.reject)
        self.btnCapNhat.clicked.connect(self._save)

    def _load_data(self):
        d = self.xe_data
        self.txtMaXe.setText(str(d.get("ma_xe", "")))
        self.txtTenXe.setText(str(d.get("ten_xe", "")))

        hang = d.get("hang_xe", "")
        idx = self.cmbHang.findText(hang)
        self.cmbHang.setCurrentIndex(idx if idx >= 0 else 0)

        self.txtDongXe.setText(str(d.get("dong_xe", "")))
        self.spnNamSX.setValue(int(d.get("nam_sx", 2024)))
        self.txtMauSac.setText(str(d.get("mau_sac", "")))
        self.spnGiaNhap.setValue(float(d.get("gia_nhap", 0)))
        self.spnGiaBan.setValue(float(d.get("gia_ban", 0)))
        self.txtSoKhung.setText(str(d.get("so_khung", "")))
        self.txtSoMay.setText(str(d.get("so_may", "")))

        tt = d.get("trang_thai", "Còn hàng")
        idx2 = self.cmbTrangThai.findText(tt)
        self.cmbTrangThai.setCurrentIndex(idx2 if idx2 >= 0 else 0)

        self.txtMoTa.setPlainText(str(d.get("mo_ta", "")))

    def _save(self):
        if not self.txtTenXe.text().strip():
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập tên xe!")
            return

        updated = {
            "ten_xe":     self.txtTenXe.text().strip(),
            "hang_xe":    self.cmbHang.currentText(),
            "dong_xe":    self.txtDongXe.text().strip(),
            "nam_sx":     self.spnNamSX.value(),
            "mau_sac":    self.txtMauSac.text().strip(),
            "gia_nhap":   self.spnGiaNhap.value(),
            "gia_ban":    self.spnGiaBan.value(),
            "so_khung":   self.txtSoKhung.text().strip(),
            "so_may":     self.txtSoMay.text().strip(),
            "trang_thai": self.cmbTrangThai.currentText(),
            "mo_ta":      self.txtMoTa.toPlainText().strip(),
            "ma_xe":      self.txtMaXe.text(),
        }
        self.xe_data = updated

        if self.conn:
            try:
                cur = self.conn.cursor()
                cur.execute("""
                    UPDATE xe SET ten_xe=?, hang_xe=?, dong_xe=?, nam_sx=?,
                    mau_sac=?, gia_nhap=?, gia_ban=?, so_khung=?,
                    so_may=?, trang_thai=?, mo_ta=?
                    WHERE ma_xe=?
                """, (
                    updated["ten_xe"], updated["hang_xe"], updated["dong_xe"],
                    updated["nam_sx"], updated["mau_sac"], updated["gia_nhap"],
                    updated["gia_ban"], updated["so_khung"], updated["so_may"],
                    updated["trang_thai"], updated["mo_ta"], updated["ma_xe"]
                ))
                self.conn.commit()
            except Exception as e:
                QMessageBox.critical(self, "Lỗi DB", str(e))
                return

        self.accept()


# ════════════════════════════════════════════════════════════
#  DIALOG XOÁ XE
# ════════════════════════════════════════════════════════════
class DialogXoaXe(QDialog):
    def __init__(self, parent=None, db_connection=None, ma_xe="", ten_xe=""):
        super().__init__(parent)
        self.conn = db_connection
        self.ma_xe = ma_xe
        self.ten_xe = ten_xe
        uic.loadUi(os.path.join(BASE_DIR, "dialog_xoa_xe.ui"), self)

        # Cập nhật tên xe vào label cảnh báo
        self.lblMessage.setText(
            f'Bạn có chắc muốn xoá xe\n"{ten_xe}" (Mã: {ma_xe}) không?\n\n'
            f'Hành động này không thể hoàn tác!'
        )
        self.btnHuy.clicked.connect(self.reject)
        self.btnXoa.clicked.connect(self._delete)

    def _delete(self):
        if self.conn and self.ma_xe:
            try:
                cur = self.conn.cursor()
                cur.execute("DELETE FROM xe WHERE ma_xe = ?", (self.ma_xe,))
                self.conn.commit()
            except Exception as e:
                QMessageBox.critical(self, "Lỗi DB", str(e))
                return
        self.accept()
