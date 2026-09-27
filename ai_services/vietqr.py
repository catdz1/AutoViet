import requests
def tao_ma_qr(ma_don, so_tien, ten_khach=""):
    BANK_ID = "MB"  # ← đổi thành ngân hàng của bạn
    ACCOUNT = "0123456789"  # ← đổi thành số TK của đại lý

    url = f"https://img.vietqr.io/image/{BANK_ID}-{ACCOUNT}-compact2.png"
    params = {
        "amount": int(so_tien),
        "addInfo": f"{ma_don} {ten_khach}".strip(),
        "accountName": "DAI LY AUTO VIET"
    }
    r = requests.get(url, params=params, timeout=10)
    path = f"assets/qr_{ma_don}.png"
    with open(path, "wb") as f:
        f.write(r.content)
    return path  # trả về đường dẫn ảnh QR để hiển thị trong PyQt6