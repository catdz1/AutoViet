content = open('views/thanh_toan_view.py', 'r', encoding='utf-8').read()

old_func = '    def _lay_du_lieu_tt(self):'

new_func = '''    def _lay_du_lieu_tt(self):
        try:
            conn = get_conn()
            rows = conn.execute(
                "SELECT d.ma_don, kh.ho_ten, xe.hang_xe || ' ' || xe.dong_xe, "
                "d.so_tien_da_tt, d.gia_ban_thuc, d.trang_thai_tt "
                "FROM don_hang d "
                "LEFT JOIN khach_hang kh ON d.kh_id = kh.id "
                "LEFT JOIN xe ON d.xe_id = xe.id "
                "ORDER BY d.id DESC LIMIT 20"
            ).fetchall()
            conn.close()
            result = []
            for r in rows:
                result.append(
                    str(r[0]) + ": " + str(r[1]) + " - " + str(r[2]) +
                    " - Da TT: " + str(r[3]) + " / " + str(r[4]) + " - " + str(r[5])
                )
            return "\\n".join(result)
        except Exception as e:
            return "Khong lay duoc du lieu: " + str(e)

    def _lay_du_lieu_tt_OLD(self):'''

content = content.replace(old_func, new_func, 1)
open('views/thanh_toan_view.py', 'w', encoding='utf-8').write(content)
print("Sua xong!")