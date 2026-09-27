"""
database.py
Ket noi SQLite — tao bang — seed du lieu mau
AutoViet v2.0 — Day du cac bang chuc nang
"""
import sqlite3, os
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dealership.db")
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
def init_db():
    conn = get_conn(); c = conn.cursor()
    # ── 1. BANG XE ──────────────────────────────────────────────────────
    c.execute("""CREATE TABLE IF NOT EXISTS xe (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        ma_xe       TEXT UNIQUE NOT NULL,
        hang_xe     TEXT NOT NULL,
        dong_xe     TEXT NOT NULL,
        nam_sx      INTEGER NOT NULL,
        mau_sac     TEXT,
        so_khung    TEXT UNIQUE,
        so_may      TEXT UNIQUE,
        gia_nhap    REAL NOT NULL DEFAULT 0,
        gia_ban     REAL NOT NULL DEFAULT 0,
        so_km       INTEGER DEFAULT 0,
        tinh_trang  TEXT DEFAULT 'Moi',
        trang_thai  TEXT DEFAULT 'Con hang',
        mo_ta       TEXT,
        ngay_nhap   TEXT DEFAULT CURRENT_DATE,
        anh_url     TEXT,
        noi_bat     INTEGER DEFAULT 0,
        giam_gia    REAL DEFAULT 0
    )""")
    # ── 2. BANG KHACH HANG ──────────────────────────────────────────────
    c.execute("""CREATE TABLE IF NOT EXISTS khach_hang (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        ma_kh       TEXT UNIQUE NOT NULL,
        ho_ten      TEXT NOT NULL,
        so_dt       TEXT NOT NULL,
        email       TEXT,
        dia_chi     TEXT,
        cmnd        TEXT,
        ngay_sinh   TEXT,
        loai_kh     TEXT DEFAULT 'Ca nhan',
        ghi_chu     TEXT,
        created_at  TEXT DEFAULT CURRENT_TIMESTAMP
    )""")

    # ── 3. BANG NHAN VIEN ───────────────────────────────────────────────
    c.execute("""CREATE TABLE IF NOT EXISTS nhan_vien (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        ma_nv       TEXT UNIQUE NOT NULL,
        ho_ten      TEXT NOT NULL,
        chuc_vu     TEXT NOT NULL,
        so_dt       TEXT,
        email       TEXT,
        ngay_vao    TEXT,
        luong       REAL DEFAULT 0,
        trang_thai  TEXT DEFAULT 'Dang lam',
        created_at  TEXT DEFAULT CURRENT_TIMESTAMP
    )""")

    # ── 4. BANG DON HANG ────────────────────────────────────────────────
    c.execute("""CREATE TABLE IF NOT EXISTS don_hang (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        ma_don          TEXT UNIQUE NOT NULL,
        xe_id           INTEGER NOT NULL REFERENCES xe(id),
        kh_id           INTEGER NOT NULL REFERENCES khach_hang(id),
        nv_id           INTEGER NOT NULL REFERENCES nhan_vien(id),
        gia_ban_thuc    REAL NOT NULL,
        chiet_khau      REAL DEFAULT 0,
        phuong_thuc     TEXT DEFAULT 'Tien mat',
        trang_thai      TEXT DEFAULT 'Cho xu ly',
        trang_thai_tt   TEXT DEFAULT 'Chua thanh toan',
        so_tien_da_tt   REAL DEFAULT 0,
        ghi_chu_tt      TEXT,
        ngay_dat        TEXT DEFAULT CURRENT_DATE,
        ngay_giao       TEXT,
        ghi_chu         TEXT,
        created_at      TEXT DEFAULT CURRENT_TIMESTAMP
    )""")

    # ── 5. BANG DICH VU ─────────────────────────────────────────────────
    c.execute("""CREATE TABLE IF NOT EXISTS dich_vu (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        ma_dv       TEXT UNIQUE NOT NULL,
        xe_id       INTEGER REFERENCES xe(id),
        kh_id       INTEGER REFERENCES khach_hang(id),
        nv_id       INTEGER REFERENCES nhan_vien(id),
        loai_dv     TEXT NOT NULL,
        mo_ta       TEXT,
        chi_phi     REAL DEFAULT 0,
        trang_thai  TEXT DEFAULT 'Tiep nhan',
        ngay_nhan   TEXT DEFAULT CURRENT_DATE,
        ngay_hoan   TEXT,
        created_at  TEXT DEFAULT CURRENT_TIMESTAMP
    )""")

    # ── 6. BANG CHAM CONG ───────────────────────────────────────────────
    c.execute("""CREATE TABLE IF NOT EXISTS cham_cong (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        nv_id       INTEGER NOT NULL REFERENCES nhan_vien(id),
        ngay        TEXT NOT NULL,
        gio_vao     TEXT,
        gio_ra      TEXT,
        trang_thai  TEXT DEFAULT 'Dung gio',
        ghi_chu     TEXT,
        thuong      REAL DEFAULT 0,
        phat        REAL DEFAULT 0,
        created_at  TEXT DEFAULT (datetime('now','localtime'))
    )""")

    # ── 7. BANG TRA GOP ─────────────────────────────────────────────────
    c.execute("""CREATE TABLE IF NOT EXISTS tra_gop (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        ma_tg           TEXT UNIQUE NOT NULL,
        don_hang_id     INTEGER REFERENCES don_hang(id),
        kh_id           INTEGER REFERENCES khach_hang(id),
        tong_tien       REAL NOT NULL DEFAULT 0,
        so_tien_tra_truoc REAL DEFAULT 0,
        lai_suat        REAL DEFAULT 0,
        so_thang        INTEGER DEFAULT 12,
        tien_hang_thang REAL DEFAULT 0,
        so_thang_da_tra INTEGER DEFAULT 0,
        tong_da_tra     REAL DEFAULT 0,
        con_lai         REAL DEFAULT 0,
        trang_thai      TEXT DEFAULT 'Dang tra',
        ngay_bat_dau    TEXT DEFAULT CURRENT_DATE,
        ghi_chu         TEXT,
        created_at      TEXT DEFAULT CURRENT_TIMESTAMP
    )""")

    # ── 8. BANG THANH TOAN ──────────────────────────────────────────────
    c.execute("""CREATE TABLE IF NOT EXISTS thanh_toan (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        ma_tt           TEXT UNIQUE NOT NULL,
        don_hang_id     INTEGER REFERENCES don_hang(id),
        so_tien         REAL NOT NULL DEFAULT 0,
        phuong_thuc     TEXT DEFAULT 'Tien mat',
        trang_thai      TEXT DEFAULT 'Hoan thanh',
        ngay_tt         TEXT DEFAULT CURRENT_DATE,
        ghi_chu         TEXT,
        nv_id           INTEGER REFERENCES nhan_vien(id),
        created_at      TEXT DEFAULT CURRENT_TIMESTAMP
    )""")

    # ── 9. BANG USERS (TAI KHOAN) ───────────────────────────────────────
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        username    TEXT UNIQUE NOT NULL,
        password    TEXT NOT NULL,
        role        TEXT DEFAULT 'nhanvien',
        ho_ten      TEXT,
        email       TEXT,
        nv_id       INTEGER REFERENCES nhan_vien(id),
        status      TEXT DEFAULT 'approved',
        created_at  TEXT DEFAULT CURRENT_TIMESTAMP
    )""")

    # ── 10. BANG LICH BAO DUONG ─────────────────────────────────────────
    c.execute("""CREATE TABLE IF NOT EXISTS lich_bao_duong (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        xe_id       INTEGER REFERENCES xe(id),
        kh_id       INTEGER REFERENCES khach_hang(id),
        nv_id       INTEGER REFERENCES nhan_vien(id),
        loai_bd     TEXT NOT NULL,
        mo_ta       TEXT,
        ngay_hen    TEXT,
        ngay_thuc   TEXT,
        chi_phi     REAL DEFAULT 0,
        trang_thai  TEXT DEFAULT 'Cho xac nhan',
        ghi_chu     TEXT,
        created_at  TEXT DEFAULT CURRENT_TIMESTAMP
    )""")

    # ── 11. BANG THONG BAO ──────────────────────────────────────────────
    c.execute("""CREATE TABLE IF NOT EXISTS thong_bao (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        tieu_de     TEXT NOT NULL,
        noi_dung    TEXT,
        loai        TEXT DEFAULT 'he_thong',
        da_doc      INTEGER DEFAULT 0,
        user_id     INTEGER REFERENCES users(id),
        created_at  TEXT DEFAULT CURRENT_TIMESTAMP
    )""")

    conn.commit()

    # ── Cap nhat cot neu thieu (cho database cu) ─────────────────────────
    _migrate(conn)

    conn.close()
    print("[OK] Database khoi tao xong!")
def _migrate(conn):
    """Them cot moi vao bang cu neu chua co"""
    migrations = [
        ("xe",       "anh_url",          "TEXT"),
        ("xe",       "noi_bat",          "INTEGER DEFAULT 0"),
        ("xe",       "giam_gia",         "REAL DEFAULT 0"),
        ("don_hang", "trang_thai_tt",    "TEXT DEFAULT 'Chua thanh toan'"),
        ("don_hang", "so_tien_da_tt",    "REAL DEFAULT 0"),
        ("don_hang", "ghi_chu_tt",       "TEXT"),
    ]
    for table, col, col_type in migrations:
        try:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}")
            conn.commit()
        except sqlite3.OperationalError:
            pass  # Cot da ton tai, bo qua (binh thuong khi DB da co san)
def seed_data():
    conn = get_conn(); c = conn.cursor()
    if c.execute("SELECT COUNT(*) FROM xe").fetchone()[0] > 0:
        conn.close(); return

    # ── Xe mau ──────────────────────────────────────────────────────────
    c.executemany("""INSERT OR IGNORE INTO xe
        (ma_xe,hang_xe,dong_xe,nam_sx,mau_sac,so_khung,so_may,
         gia_nhap,gia_ban,so_km,tinh_trang,trang_thai,mo_ta,noi_bat,giam_gia)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", [
        ("XE001","Toyota","Camry 2.5Q",2024,"Trang Ngoc Trai","TN24001","MY24001",
         1050000000,1150000000,0,"Moi","Con hang","Xe moi nguyen tem",1,0),
        ("XE002","Toyota","Fortuner 2.8AT",2024,"Den Anh Kim","TN24002","MY24002",
         1200000000,1350000000,0,"Moi","Con hang","Nhap khau nguyen chiec",1,0),
        ("XE003","Honda","CR-V e:HEV RS",2024,"Xanh Co Vit","HN24001","MH24001",
         1050000000,1180000000,0,"Moi","Dat coc","Hybrid tiet kiem",1,0),
        ("XE004","Hyundai","Tucson Premium",2023,"Do Crimson","HY23001","MHY23001",
         780000000,890000000,5000,"Da qua SD","Da ban","Xe demo bao hanh",0,10),
        ("XE005","Kia","Sorento AWD",2024,"Bac Thien Thanh","KA24001","MK24001",
         1100000000,1260000000,0,"Moi","Con hang","Full option cao cap",1,0),
        ("XE006","Mazda","CX-5 2.5 Premium",2024,"Do Soul Red","MA24001","MM24001",
         850000000,969000000,0,"Moi","Con hang","Phien ban the thao",0,0),
        ("XE007","Ford","Ranger Wildtrak",2024,"Xanh Storm Blue","FO24001","MF24001",
         760000000,889000000,0,"Moi","Con hang","Ban tai manh me",0,0),
        ("XE008","Toyota","Veloz Cross 1.5CVT",2024,"Trang Tinh","TN24003","MY24003",
         580000000,648000000,0,"Moi","Con hang","MPV 7 cho",0,0),
        ("XE009","Mercedes-Benz","GLC 300",2023,"Bac","MB23001","MMB23001",
         2100000000,2300000000,8000,"Da qua SD","Con hang","Sang trong",1,10),
        ("XE010","BMW","X6M",2023,"Den","BM23001","MBM23001",
         7200000000,7900000000,3000,"Da qua SD","Con hang","Sieu xe hiem",1,5),
    ])

    # ── Nhan vien mau ───────────────────────────────────────────────────
    c.executemany("""INSERT OR IGNORE INTO nhan_vien
        (ma_nv,ho_ten,chuc_vu,so_dt,email,ngay_vao,luong,trang_thai)
        VALUES(?,?,?,?,?,?,?,?)""", [
        ("NV001","Nguyen Van An","Giam doc","0901234567","an@auto.vn","2018-01-15",25000000,"Dang lam"),
        ("NV002","Tran Thi Binh","Quan ly BH","0912345678","binh@auto.vn","2019-03-20",18000000,"Dang lam"),
        ("NV003","Le Van Cuong","Nhan vien BH","0923456789","cuong@auto.vn","2020-06-01",12000000,"Dang lam"),
        ("NV004","Pham Thi Dung","Nhan vien BH","0934567890","dung@auto.vn","2021-01-10",12000000,"Dang lam"),
        ("NV005","Hoang Van Em","Ky thuat vien","0945678901","em@auto.vn","2020-09-15",10000000,"Dang lam"),
    ])

    # ── Khach hang mau ──────────────────────────────────────────────────
    c.executemany("""INSERT OR IGNORE INTO khach_hang
        (ma_kh,ho_ten,so_dt,email,dia_chi,cmnd,ngay_sinh,loai_kh)
        VALUES(?,?,?,?,?,?,?,?)""", [
        ("KH001","Nguyen Minh Tuan","0987654321","tuan@gmail.com","123 Tran Hung Dao, Q1","079001234","1985-06-15","Ca nhan"),
        ("KH002","Tran Thi Hoa","0976543210","hoa@yahoo.com","456 Nguyen Hue, Q1","079002345","1990-03-22","Ca nhan"),
        ("KH003","Le Quoc Hung","0965432109","hung@gmail.com","12 Le Loi, Q1","079003456","1978-11-30","Ca nhan"),
        ("KH004","Pham Thi Lan","0954321098","lan@gmail.com","34 Bui Thi Xuan, Q1","079004567","1992-08-14","Ca nhan"),
        ("KH005","Nguyen Thu Huyen","0943210987","huyen@gmail.com","56 Hai Ba Trung, Q3","079005678","1995-12-25","Ca nhan"),
    ])

    # ── Don hang mau ────────────────────────────────────────────────────
    c.executemany("""INSERT OR IGNORE INTO don_hang
        (ma_don,xe_id,kh_id,nv_id,gia_ban_thuc,chiet_khau,phuong_thuc,
         trang_thai,trang_thai_tt,so_tien_da_tt,ngay_dat,ngay_giao)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""", [
        ("DH001",4,1,3,890000000,0,"Tien mat","Da giao xe","Da thanh toan",890000000,"2024-01-15","2024-01-20"),
        ("DH002",1,2,4,1130000000,20000000,"Vay NH","Da thanh toan","Da thanh toan",1130000000,"2024-02-10",None),
        ("DH003",3,3,3,1160000000,20000000,"Vay NH","Cho xu ly","Chua thanh toan",0,"2024-03-10",None),
        ("DH004",6,4,3,969000000,0,"Tien mat","Da giao xe","Da thanh toan",969000000,"2024-04-27",None),
        ("DH005",7,5,4,889000000,0,"Chuyen khoan","Cho xu ly","Chua thanh toan",0,"2024-04-28",None),
    ])

    # ── Dich vu mau ─────────────────────────────────────────────────────
    c.executemany("""INSERT OR IGNORE INTO dich_vu
        (ma_dv,xe_id,kh_id,nv_id,loai_dv,mo_ta,chi_phi,trang_thai,ngay_nhan,ngay_hoan)
        VALUES(?,?,?,?,?,?,?,?,?,?)""", [
        ("DV001",4,1,5,"Bao duong dinh ky","Thay dau, loc gio, kiem tra phanh",1500000,"Hoan thanh","2024-03-01","2024-03-01"),
        ("DV002",3,3,5,"Sua chua","Thay ma phanh truoc",2200000,"Dang thuc hien","2024-03-10",None),
        ("DV003",1,2,5,"Dang kiem","Dang kiem dinh ky 6 thang",500000,"Tiep nhan","2024-03-11",None),
        ("DV004",9,3,5,"Bao duong dinh ky","Kiem tra toan bo",3500000,"Hoan thanh","2024-04-01","2024-04-02"),
    ])

    conn.commit(); conn.close()
    print("[✓] Seed data xong!")


if __name__ == "__main__":
    init_db()
    seed_data()
    print("[✓] Hoan tat!")