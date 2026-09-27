import qrcode, os
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

QR_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "qr_codes")
os.makedirs(QR_DIR, exist_ok=True)


def tao_qr_don_hang(don_hang: dict) -> str:
    """Tao QR code cho don hang, tra ve duong dan file anh"""
    ma_don = str(don_hang.get("ma_don", ""))

    # Ngan gon — moi app quet duoc
    qr_text = f"AUTOVIET:{ma_don}"

    qr_obj = qrcode.QRCode(
        version=2,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=12,
        border=4,
    )
    qr_obj.add_data(qr_text)
    qr_obj.make(fit=True)

    img = qr_obj.make_image(fill_color="#0f1f35", back_color="white")
    fname = os.path.join(QR_DIR, f"QR_{ma_don}.png")
    img.save(fname)
    return fname


def qr_to_pixmap(qr_path: str, size=200) -> QPixmap:
    """Chuyen file QR thanh QPixmap de hien thi trong PyQt6"""
    if not os.path.exists(qr_path):
        return QPixmap()
    pix = QPixmap(qr_path)
    if pix.isNull():
        return QPixmap()
    return pix.scaled(
        size, size,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )