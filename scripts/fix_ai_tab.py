content = open('views/thanh_toan_view.py', 'r', encoding='utf-8').read()

# Kiem tra xem method co bi them ngoai class khong
if '\ndef    def _build_tab_ai' in content or '\n    def _build_tab_ai' not in content:
    print("Method nam ngoai class, dang fix...")

# Xoa phan ai_methods cu bi them sai (nam o cuoi file ngoai class)
import re

# Tim va xoa phan code AI bi them sai (bat dau tu dong khong co indent)
lines = content.split('\n')
new_lines = []
skip = False
for i, line in enumerate(lines):
    # Neu gap "def _build_tab_ai" ma KHONG co 4 spaces indent = bi them sai
    if line.startswith('def _build_tab_ai') or line.startswith('    def _build_tab_ai') and skip:
        skip = False
    if line.startswith('\ndef _build_tab_ai(') or (i > 0 and lines[i-1] == '' and line == 'def _build_tab_ai(self):'):
        skip = True
    if not skip:
        new_lines.append(line)

content = '\n'.join(new_lines)

# Them lai dung method vao trong class - truoc dong cuoi cung cua class
ai_methods = """
    def _build_tab_ai(self):
        w = QWidget()
        w.setStyleSheet("background:#f0f4f8;")
        lv = QVBoxLayout(w)
        lv.setContentsMargins(20, 20, 20, 20)
        lv.setSpacing(12)
        title = QLabel("🤖  Trợ lý AI AutoViet")
        title.setStyleSheet("font-size:15px;font-weight:700;color:#1e40af;background:transparent;")
        lv.addWidget(title)
        self.ai_output = QTextEdit()
        self.ai_output.setReadOnly(True)
        self.ai_output.setStyleSheet("background:#ffffff;border:1px solid #dbeafe;border-radius:10px;padding:12px;font-size:13px;color:#1e293b;")
        self.ai_output.setPlaceholderText("Câu trả lời của AI sẽ hiển thị ở đây...")
        self.ai_output.setMinimumHeight(200)
        lv.addWidget(self.ai_output, 1)
        hl = QHBoxLayout()
        hl.setSpacing(8)
        self.ai_input = QLineEdit()
        self.ai_input.setStyleSheet("background:#ffffff;border:1px solid #dbeafe;border-radius:8px;padding:10px 14px;font-size:13px;")
        self.ai_input.setPlaceholderText("Hỏi AI: Doanh thu hôm nay? Đơn nào chưa TT?...")
        self.ai_input.returnPressed.connect(self._ai_ask)
        hl.addWidget(self.ai_input, 1)
        btn_ask = QPushButton("🚀 Hỏi AI")
        btn_ask.setStyleSheet("background:#2563eb;color:white;border:none;border-radius:8px;padding:10px 20px;font-size:13px;font-weight:700;")
        btn_ask.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ask.clicked.connect(self._ai_ask)
        hl.addWidget(btn_ask)
        lv.addLayout(hl)
        lbl_quick = QLabel("Câu hỏi nhanh:")
        lbl_quick.setStyleSheet("font-size:12px;color:#64748b;background:transparent;")
        lv.addWidget(lbl_quick)
        quick_hl = QHBoxLayout()
        quick_hl.setSpacing(8)
        for q in ["Doanh thu hôm nay?", "Đơn nào chưa thanh toán?", "Tổng đơn tháng này?", "Khách nào nợ nhiều nhất?"]:
            btn_q = QPushButton(q)
            btn_q.setStyleSheet("background:#eff6ff;color:#1e40af;border:1px solid #bfdbfe;border-radius:6px;padding:6px 10px;font-size:11px;")
            btn_q.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_q.clicked.connect(lambda checked, qq=q: self._ai_quick(qq))
            quick_hl.addWidget(btn_q)
        quick_hl.addStretch()
        lv.addLayout(quick_hl)
        hl2 = QHBoxLayout()
        hl2.setSpacing(8)
        btn_qr = QPushButton("📱 Tạo QR Thanh Toán")
        btn_qr.setStyleSheet("background:#059669;color:white;border:none;border-radius:8px;padding:10px 16px;font-size:12px;font-weight:700;")
        btn_qr.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_qr.clicked.connect(self._tao_qr)
        hl2.addWidget(btn_qr)
        btn_nhac = QPushButton("📨 Soạn Tin Nhắc Nợ")
        btn_nhac.setStyleSheet("background:#d97706;color:white;border:none;border-radius:8px;padding:10px 16px;font-size:12px;font-weight:700;")
        btn_nhac.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_nhac.clicked.connect(self._soan_nhac_no)
        hl2.addWidget(btn_nhac)
        hl2.addStretch()
        lv.addLayout(hl2)
        return w

    def _lay_du_lieu_tt(self):
        try:
            conn = get_conn()
            rows = conn.execute("SELECT ma_don, ho_ten, ten_xe, so_tien_da_tt, gia_ban, trang_thai_tt FROM don_hang ORDER BY id DESC LIMIT 20").fetchall()
            conn.close()
            result = []
            for r in rows:
                result.append(str(r[0]) + ": " + str(r[1]) + " - " + str(r[2]) + " - Da TT: " + str(r[3]) + " / " + str(r[4]) + " - " + str(r[5]))
            return "\\n".join(result)
        except Exception as e:
            return "Khong lay duoc du lieu: " + str(e)

    def _ai_ask(self):
        cau_hoi = self.ai_input.text().strip()
        if not cau_hoi:
            return
        self.ai_output.setText("⏳ Đang hỏi AI...")
        du_lieu = self._lay_du_lieu_tt()
        ket_qua = hoi_tro_ly(cau_hoi, du_lieu)
        self.ai_output.setText(ket_qua)
        self.ai_input.clear()

    def _ai_quick(self, cau_hoi):
        self.ai_input.setText(cau_hoi)
        self._ai_ask()

    def _tao_qr(self):
        row = self.tbl.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Chú ý", "Vui lòng chọn một đơn hàng trong tab Danh sách!")
            return
        ma_don = self.tbl.item(row, 0).text()
        ho_ten = self.tbl.item(row, 1).text()
        try:
            con_lai_text = self.tbl.item(row, 6).text().replace(",", "").replace(" đ", "").replace("đ", "").strip()
            so_tien = int(float(con_lai_text))
        except:
            so_tien = 0
        if so_tien <= 0:
            QMessageBox.information(self, "Thông báo", "Đơn này đã thanh toán đủ rồi!")
            return
        try:
            qr_path = tao_ma_qr(ma_don, so_tien, ho_ten)
            QMessageBox.information(self, "QR Thanh Toán",
                "Đã tạo mã QR cho đơn " + ma_don + "\\nKhách: " + ho_ten + "\\nSố tiền: " + str(so_tien) + " đ\\nFile: " + qr_path)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))

    def _soan_nhac_no(self):
        row = self.tbl.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Chú ý", "Vui lòng chọn một đơn hàng trong tab Danh sách!")
            return
        ma_don = self.tbl.item(row, 0).text()
        ho_ten = self.tbl.item(row, 1).text()
        trang_thai = self.tbl.item(row, 7).text()
        if "Đã thanh toán" in trang_thai:
            QMessageBox.information(self, "Thông báo", "Đơn này đã thanh toán đủ rồi!")
            return
        try:
            con_lai_text = self.tbl.item(row, 6).text().replace(",", "").replace(" đ", "").replace("đ", "").strip()
            so_tien = int(float(con_lai_text))
        except:
            so_tien = 0
        self.ai_output.setText("⏳ AI đang soạn tin nhắn...")
        self.tabs.setCurrentIndex(3)
        tin_nhan = soan_nhac_no(ho_ten, ma_don, so_tien)
        self.ai_output.setText("📨 Tin nhắn nhắc nợ:\\n\\n" + tin_nhan)
"""

# Them vao truoc dong "class ThanhToanDialog" hoac cuoi file
if 'class ThanhToanDialog' in content:
    content = content.replace('class ThanhToanDialog', ai_methods + '\nclass ThanhToanDialog')
else:
    content = content + ai_methods

open('views/thanh_toan_view.py', 'w', encoding='utf-8').write(content)
print("Fix xong!")