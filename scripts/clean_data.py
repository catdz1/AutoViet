
import sqlite3, os, shutil, datetime
 
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dealership.db")
 
# Cac bang se bi xoa sach du lieu (giu nguyen 'users')
TABLES_TO_CLEAR = [
    "xe", "khach_hang", "nhan_vien", "don_hang", "dich_vu",
    "cham_cong", "tra_gop", "thanh_toan", "lich_bao_duong", "thong_bao",
]
 
def main():
    if not os.path.exists(DB_PATH):
        print(f"[X] Khong tim thay database tai: {DB_PATH}")
        return
 
    print("=" * 60)
    print("SE XOA TOAN BO DU LIEU trong cac bang sau (giu lai 'users'):")
    for t in TABLES_TO_CLEAR:
        print(f"   - {t}")
    print("=" * 60)
    confirm = input("Go 'YES' de xac nhan xoa (khong the hoan tac): ").strip()
    if confirm != "YES":
        print("[i] Da huy. Khong co gi bi xoa.")
        return
 
    # Backup tu dong truoc khi xoa
    backup_path = DB_PATH + f".backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(DB_PATH, backup_path)
    print(f"[OK] Da tao ban sao luu tai: {backup_path}")
 
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
 
    existing_tables = {r[0] for r in c.execute(
        "SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
 
    for t in TABLES_TO_CLEAR:
        if t in existing_tables:
            c.execute(f"DELETE FROM {t}")
            print(f"[OK] Da xoa du lieu bang '{t}'")
        else:
            print(f"[i] Bang '{t}' khong ton tai, bo qua")
 
    # Reset lai auto-increment ve 0 de id bat dau lai tu 1
    if "sqlite_sequence" in existing_tables:
        for t in TABLES_TO_CLEAR:
            c.execute("DELETE FROM sqlite_sequence WHERE name=?", (t,))
        print("[OK] Da reset lai ID tu dong tang")
 
    conn.commit()
    conn.close()
 
    print("\n[OK] HOAN TAT! Du lieu mau da duoc xoa sach.")
    print("     Tai khoan dang nhap (users) van con nguyen.")
    print(f"     Neu can khoi phuc lai, doi ten file backup '{os.path.basename(backup_path)}' thanh 'dealership.db'")
 
if __name__ == "__main__":
    main()
 