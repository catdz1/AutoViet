import requests, configparser, os

def _get_token():
    cfg = configparser.ConfigParser()
    cfg.read(os.path.join(os.path.dirname(__file__), '..', 'api_config.txt'))
    return cfg['DEFAULT'].get('ZALO_ACCESS_TOKEN', '')

def gui_zalo_admin(noi_dung: str):
    try:
        ADMIN_ID = "YOUR_ZALO_USER_ID"  # ← đổi thành Zalo ID của bạn
        requests.post(
            "https://openapi.zalo.me/v3.0/oa/message/cs",
            headers={"access_token": _get_token()},
            json={
                "recipient": {"user_id": ADMIN_ID},
                "message":   {"text": noi_dung}
            },
            timeout=10
        )
    except Exception as e:
        print(f"Zalo error: {e}")

def gui_bao_cao_cuoi_ngay(tong_don, da_tt, chua_tt, doanh_thu):
    gui_zalo_admin(f"""
📊 BÁO CÁO CUỐI NGÀY — AutoViet
━━━━━━━━━━━━━━━
📦 Tổng đơn  : {tong_don}
✅ Đã TT     : {da_tt}
❌ Chưa TT   : {chua_tt}
💰 Doanh thu : {doanh_thu:,.0f} đồng
━━━━━━━━━━━━━━━""")