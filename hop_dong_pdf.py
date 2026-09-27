"""
hop_dong_pdf.py — In hợp đồng mua xe PDF chính thức
File MỚI — copy vào thư mục gốc (cùng chỗ main.py)
"""
from datetime import datetime
def in_hop_dong(don_hang_id: int) -> str:
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle,
            Paragraph, Spacer, HRFlowable)
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.units import cm
    except ImportError:
        raise Exception("Cần cài reportlab:\npip install reportlab")
    from database import get_conn
    conn = get_conn()
    dh = conn.execute("""
        SELECT dh.*,
               x.hang_xe||' '||x.dong_xe as ten_xe, x.ma_xe,
               x.so_khung, x.so_may, x.nam_sx, x.mau_sac,
               kh.ho_ten as ten_kh, kh.so_dt, kh.email,
               kh.dia_chi, kh.cmnd,
               nv.ho_ten as ten_nv, nv.so_dt as sdt_nv
        FROM don_hang dh
        JOIN xe x ON dh.xe_id=x.id
        JOIN khach_hang kh ON dh.kh_id=kh.id
        JOIN nhan_vien nv ON dh.nv_id=nv.id
        WHERE dh.id=?""", (don_hang_id,)).fetchone()
    conn.close()
    if not dh: raise Exception("Không tìm thấy đơn hàng!")
    dh = dict(dh)

    fname = f"hop_dong_{dh['ma_don']}.pdf"
    doc = SimpleDocTemplate(fname, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=1.5*cm, bottomMargin=2*cm)

    def sty(name, size=10, bold=False, color=colors.black, align=0, sb=4, sa=4):
        return ParagraphStyle(name, fontSize=size,
            fontName='Helvetica-Bold' if bold else 'Helvetica',
            textColor=color, alignment=align, spaceBefore=sb, spaceAfter=sa)
    story = []
    today = datetime.now()

    # ── Tiêu đề ──────────────────────────────────────────────────────────
    story.append(Paragraph("CONG HOA XA HOI CHU NGHIA VIET NAM",
        sty("",11,True,colors.black,1,0,2)))
    story.append(Paragraph("Doc lap - Tu do - Hanh phuc",
        sty("",10,False,colors.black,1,0,2)))
    story.append(Paragraph("---oOo---", sty("",9,False,colors.grey,1,0,8)))

    story.append(Paragraph("HOP DONG MUA BAN XE O TO",
        sty("",16,True,colors.HexColor('#6d28d9'),1,0,4)))
    story.append(Paragraph(f"So hop dong: {dh['ma_don']}/HD-{today.year}",
        sty("",10,False,colors.HexColor('#7c3aed'),1,0,2)))
    story.append(Paragraph(
        f"Ngay {today.day} thang {today.month} nam {today.year}",
        sty("",10,False,colors.grey,1,0,10)))

    story.append(HRFlowable(width="100%",thickness=1,color=colors.HexColor('#6d28d9')))
    story.append(Spacer(1,8))

    # ── Bên bán ───────────────────────────────────────────────────────────
    story.append(Paragraph("BEN BAN (Ben A):", sty("",11,True,colors.HexColor('#1e3a5f'),0,6,4)))
    ban_data = [
        ["Ten cong ty:", "AUTOVIET — He thong Quan ly Dai ly Xe Hoi"],
        ["Dia chi:", "So 1 Duong Giai Phong, Ha Noi"],
        ["Dien thoai:", "1900-xxxx"],
        ["Nguoi dai dien:", dh['ten_nv']],
        ["So DT NV:", dh['sdt_nv'] or "N/A"],
    ]
    t_ban = Table(ban_data, colWidths=[4*cm, 13*cm])
    t_ban.setStyle(TableStyle([
        ('FONTNAME',(0,0),(0,-1),'Helvetica-Bold'),
        ('FONTSIZE',(0,0),(-1,-1),10),
        ('PADDING',(0,0),(-1,-1),5),
        ('TEXTCOLOR',(0,0),(0,-1),colors.HexColor('#4a5568')),
    ]))
    story.append(t_ban); story.append(Spacer(1,8))

    # ── Bên mua ───────────────────────────────────────────────────────────
    story.append(Paragraph("BEN MUA (Ben B):", sty("",11,True,colors.HexColor('#1e3a5f'),0,6,4)))
    mua_data = [
        ["Ho va ten:", dh['ten_kh']],
        ["CMND/CCCD:", dh.get('cmnd','') or "N/A"],
        ["Dia chi:", dh.get('dia_chi','') or "N/A"],
        ["Dien thoai:", dh.get('so_dt','') or "N/A"],
        ["Email:", dh.get('email','') or "N/A"],
    ]
    t_mua = Table(mua_data, colWidths=[4*cm, 13*cm])
    t_mua.setStyle(TableStyle([
        ('FONTNAME',(0,0),(0,-1),'Helvetica-Bold'),
        ('FONTSIZE',(0,0),(-1,-1),10),
        ('PADDING',(0,0),(-1,-1),5),
        ('TEXTCOLOR',(0,0),(0,-1),colors.HexColor('#4a5568')),
    ]))
    story.append(t_mua); story.append(Spacer(1,8))

    story.append(HRFlowable(width="100%",thickness=0.5,color=colors.lightgrey))
    story.append(Spacer(1,6))

    # ── Điều khoản ────────────────────────────────────────────────────────
    story.append(Paragraph("DIEU 1: THONG TIN XE HANG",
        sty("",11,True,colors.HexColor('#6d28d9'),0,8,4)))
    xe_data = [
        ["Ten xe:", dh['ten_xe'],        "Ma xe:", dh['ma_xe']],
        ["Nam SX:", str(dh['nam_sx']),   "Mau sac:", dh.get('mau_sac','N/A')],
        ["So khung (VIN):", dh.get('so_khung','N/A'), "So may:", dh.get('so_may','N/A')],
    ]
    t_xe = Table(xe_data, colWidths=[3.5*cm,5.5*cm,3.5*cm,5.5*cm])
    t_xe.setStyle(TableStyle([
        ('FONTNAME',(0,0),(0,-1),'Helvetica-Bold'),
        ('FONTNAME',(2,0),(2,-1),'Helvetica-Bold'),
        ('FONTSIZE',(0,0),(-1,-1),10),
        ('GRID',(0,0),(-1,-1),0.3,colors.lightgrey),
        ('BACKGROUND',(0,0),(0,-1),colors.HexColor('#f3f0ff')),
        ('BACKGROUND',(2,0),(2,-1),colors.HexColor('#f3f0ff')),
        ('PADDING',(0,0),(-1,-1),7),
    ]))
    story.append(t_xe); story.append(Spacer(1,8))

    story.append(Paragraph("DIEU 2: GIA TRI HOP DONG VA PHUONG THUC THANH TOAN",
        sty("",11,True,colors.HexColor('#6d28d9'),0,8,4)))
    gia = dh['gia_ban_thuc']; ck = dh.get('chiet_khau',0) or 0; tt = gia - ck
    pay_data = [
        ["Dien giai","So tien (VND)"],
        ["Gia ban xe",f"{gia:,.0f} dong"],
        ["Chiet khau",f"- {ck:,.0f} dong"],
        ["TONG THANH TOAN",f"{tt:,.0f} dong"],
        ["Phuong thuc TT",dh['phuong_thuc']],
    ]
    t_pay = Table(pay_data, colWidths=[10*cm,8*cm])
    t_pay.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#6d28d9')),
        ('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
        ('FONTNAME',(0,3),(-1,3),'Helvetica-Bold'),
        ('FONTSIZE',(0,3),(-1,3),12),
        ('BACKGROUND',(0,3),(-1,3),colors.HexColor('#ede9fe')),
        ('TEXTCOLOR',(0,3),(-1,3),colors.HexColor('#6d28d9')),
        ('ALIGN',(1,0),(1,-1),'RIGHT'),
        ('GRID',(0,0),(-1,-1),0.3,colors.lightgrey),
        ('PADDING',(0,0),(-1,-1),8),
        ('FONTSIZE',(0,0),(-1,-1),10),
    ]))
    story.append(t_pay); story.append(Spacer(1,8))

    story.append(Paragraph("DIEU 3: CAM KET CUA CAC BEN",
        sty("",11,True,colors.HexColor('#6d28d9'),0,8,4)))
    story.append(Paragraph(
        "3.1. Ben ban cam ket: Xe hang dung nhu mo ta, day du giay to hop le, bao hanh theo quy dinh.",
        sty("",10,False,colors.black,0,2,2)))
    story.append(Paragraph(
        "3.2. Ben mua cam ket: Thanh toan dung han, su dung xe dung muc dich, tuan thu phap luat.",
        sty("",10,False,colors.black,0,2,2)))
    story.append(Paragraph(
        "3.3. Hop dong co hieu luc tu ngay ky. Moi tranh chap duoc giai quyet bang thuong luong.",
        sty("",10,False,colors.black,0,2,8)))

    story.append(HRFlowable(width="100%",thickness=0.5,color=colors.lightgrey))
    story.append(Spacer(1,12))

    # ── Chữ ký ────────────────────────────────────────────────────────────
    ky_data = [[
        Paragraph(f"<b>BEN MUA (Ben B)</b><br/>{dh['ten_kh']}<br/><br/><br/><br/>(Ky, ghi ro ho ten)",
            sty("",10,False,colors.grey,1)),
        Paragraph(f"<b>BEN BAN (Ben A)</b><br/>AUTOVIET<br/><br/><br/><br/>(Ky, dong dau)",
            sty("",10,False,colors.grey,1)),
    ]]
    t_ky = Table(ky_data, colWidths=[8.5*cm,9*cm])
    story.append(t_ky)
    story.append(Spacer(1,10))
    story.append(Paragraph(
        "AutoViet — He thong Quan ly Dai ly Xe Hoi | Tel: 1900-xxxx | autoviet.vn",
        sty("",8,False,colors.grey,1)))

    doc.build(story)
    return fname
