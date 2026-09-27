from flask import Flask, request

app = Flask(__name__)


@app.route("/webhook-sepay", methods=["POST"])
def nhan_thanh_toan():
    data = request.json
    noi_dung = data.get("content", "")  # VD: "DH033 thanh toan xe"
    so_tien = data.get("transferAmount", 0)

    # Tìm mã đơn trong nội dung chuyển khoản
    import re
    match = re.search(r'DH(\d+)', noi_dung.upper())
    if match:
        ma_don = match.group(1)
        # Cập nhật DB → đánh dấu "Đã thanh toán"
        cap_nhat_trang_thai(ma_don, "DA_THANH_TOAN", so_tien)
        # Gửi thông báo Zalo cho admin
        gui_zalo_admin(f"✅ DH{ma_don} vừa thanh toán {so_tien:,}đ")

    return {"success": True}


if __name__ == "__main__":
    app.run(port=5000)