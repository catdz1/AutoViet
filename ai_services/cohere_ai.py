import os

import cohere

COHERE_API_KEY = os.getenv("COHERE_API_KEY")


def hoi_tro_ly(cau_hoi, du_lieu_don):
    try:
        co = cohere.ClientV2(COHERE_API_KEY)
        noi_dung = (
                "Ban la tro ly quan ly dai ly xe AutoViet. "
                "Tra loi NGAN GON, suc tich, TOI DA 3-4 dong. "
                "Khong liet ke tung don, chi tong hop so lieu chinh. "
                "Su dung don vi ty dong cho so lon. "
                "Du lieu: " + du_lieu_don + ". "
                                            "Cau hoi: " + cau_hoi
        )
        response = co.chat(
            model="command-r7b-12-2024",
            messages=[{"role": "user", "content": noi_dung}]
        )
        return response.message.content[0].text
    except Exception as e:
        return "Loi AI: " + str(e)


def soan_nhac_no(ten_khach, ma_don, so_tien_con):
    try:
        co = cohere.ClientV2(COHERE_API_KEY)
        noi_dung = "Soan tin nhan nhac no ngan gon cho khach " + ten_khach + ", don " + ma_don + ", con no " + str(so_tien_con) + " dong. Chi viet tin nhan thoi."
        response = co.chat(
            model="command-r7b-12-2024",
            messages=[{"role": "user", "content": noi_dung}]
        )
        return response.message.content[0].text
    except Exception as e:
        return "Loi AI: " + str(e)