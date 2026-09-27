content = open('views/thanh_toan_view.py', 'r', encoding='utf-8').read()

# Tim va thay toan bo ham _ai_ask hien tai
import re
old_pattern = r'    def _ai_ask\(self\):.*?(?=\n    def )'
new_method = '''    def _ai_ask(self):
        cau_hoi = self.ai_input.text().strip()
        if not cau_hoi:
            return
        self.ai_output.setText("⏳ Đang hỏi AI...")
        du_lieu = self._lay_du_lieu_tt()
        ket_qua = hoi_tro_ly(cau_hoi, du_lieu)
        self.ai_output.setText(ket_qua)
        self.ai_input.clear()

'''
content = re.sub(old_pattern, new_method, content, flags=re.DOTALL)
open('views/thanh_toan_view.py', 'w', encoding='utf-8').write(content)
print("Khoi phuc xong!")