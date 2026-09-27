import os

import cohere

COHERE_API_KEY = os.getenv("COHERE_API_KEY")


def hoi_tro_ly(cau_hoi, du_lieu_don):
    try:
        co = cohere.ClientV2(COHERE_API_KEY)
        response = co.chat(
            model="command-r-plus",
            messages=[{
                "role": "user",
                "content": "Ban la tro ly AutoViet. Du lieu: " + du_lieu_don + ". Cau hoi: " + cau_hoi + ". Tra loi tieng Viet."
            }]
        )
        return response.message.content[0].text
    except Exception as e:
        return "Loi AI: " + str(e)


def soan_nhac_no(ten_khach, ma_don, so_tien_con):
    try:
        co = cohere.ClientV2(COHERE_API_KEY)
        response = co.chat(
            model="command-r-plus",
            messages=[{
                "role": "user",
                "content": "Soan tin nhan nhac no ngan gon cho khach " + ten_khach + ", don " + ma_don + ", con no " + str(so_tien_con) + " dong."
            }]
        )
        return response.message.content[0].text
    except Exception as e:
        return "Loi AI: " + str(e)