"""
invoice_pdf.py — In hóa đơn PDF + Phiếu dịch vụ PDF
File MỚI — copy vào thư mục gốc (cùng chỗ main.py)
"""
import os
from datetime import datetime
def in_hoa_don(don_hang_id: int) -> str:
    """
    Xuất hóa đơn PDF cho đơn hàng.
    Trả về đường dẫn file PDF hoặc raise Exception
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
    except ImportError:
        raise Exception("Cần cài reportlab:\npip install reportlab")
    from database import get_conn
    conn = get_conn()
    dh = conn.execute("""
        SELECT dh.*,
               x.hang_xe||' '||x.dong_xe as ten_xe, x.ma_xe, x.so_khung, x.so_may,
               x.nam_sx, x.mau_sac,
               kh.ho_ten as ten_kh, kh.so_dt, kh.email, kh.dia_chi, kh.cmnd,
               nv.ho_ten as ten_nv, nv.so_dt as sdt_nv
        FROM don_hang dh
        JOIN xe x ON dh.xe_id=x.id
        JOIN khach_hang kh ON dh.kh_id=kh.id
        JOIN nhan_vien nv ON dh.nv_id=nv.id
        WHERE dh.id=?""", (don_hang_id,)).fetchone()
    conn.close()
    if not dh: raise Exception("Không tìm thấy đơn hàng!")
    dh = dict(dh)
    fname = f"hoa_don_{dh['ma_don']}.pdf"
    doc = SimpleDocTemplate(fname, pagesize=A4,
        rightMargin=1.5*cm, leftMargin=1.5*cm,
        topMargin=1.5*cm, bottomMargin=1.5*cm)

    styles = getSampleStyleSheet()
    def style(name, size=10, bold=False, color=colors.black, align=0, space_before=0, space_after=4):
        return ParagraphStyle(name, fontSize=size,
            fontName='Helvetica-Bold' if bold else 'Helvetica',
            textColor=color, alignment=align,
            spaceBefore=space_before, spaceAfter=space_after)

    story = []

    # ── Header ───────────────────────────────────────────────────────────
    header_data = [[
        Paragraph("<b>AUTOVIET</b>", style("h1",18,True,colors.HexColor('#6d28d9'),1)),
        Paragraph(f"<b>HOA DON BAN XE</b><br/>So: {dh['ma_don']}<br/>{datetime.now().strftime('%d/%m/%Y %H:%M')}",
                  style("h2",11,True,colors.HexColor('#1a1a2e'),2))
    ]]
    ht = Table(header_data, colWidths=[9*cm, 9*cm])
    ht.setStyle(TableStyle([
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('BACKGROUND',(0,0),(-1,-1),colors.HexColor('#f3f0ff')),
        ('PADDING',(0,0),(-1,-1),12),
        ('ROUNDEDCORNERS',[8,8,8,8]),
    ]))
    story.append(ht); story.append(Spacer(1,12))

    # ── Thông tin khách hàng & NV ─────────────────────────────────────────
    info_data = [
        [Paragraph("<b>THONG TIN KHACH HANG</b>", style("",10,True,colors.HexColor('#6d28d9'))),
         Paragraph("<b>NHAN VIEN PHU TRACH</b>", style("",10,True,colors.HexColor('#6d28d9')))],
        [Paragraph(f"Ho ten: <b>{dh['ten_kh']}</b>", style("")),
         Paragraph(f"Ho ten: <b>{dh['ten_nv']}</b>", style(""))],
        [Paragraph(f"So DT: {dh['so_dt']}", style("")),
         Paragraph(f"So DT: {dh['sdt_nv']}", style(""))],
        [Paragraph(f"Email: {dh.get('email','') or 'N/A'}", style("")),
         Paragraph(f"Ngay dat: {dh['ngay_dat']}", style(""))],
        [Paragraph(f"Dia chi: {dh.get('dia_chi','') or 'N/A'}", style("")),
         Paragraph(f"Phuong thuc: <b>{dh['phuong_thuc']}</b>", style(""))],
    ]
    it = Table(info_data, colWidths=[9*cm, 9*cm])
    it.setStyle(TableStyle([
        ('GRID',(0,0),(-1,-1),0.3,colors.lightgrey),
        ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#ede9fe')),
        ('PADDING',(0,0),(-1,-1),7),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
    ]))
    story.append(it); story.append(Spacer(1,12))

    # ── Thông tin xe ──────────────────────────────────────────────────────
    story.append(Paragraph("<b>THONG TIN XE HANG</b>",
        style("",11,True,colors.HexColor('#6d28d9'),0,0,6)))
    xe_data = [
        ["Ten xe", dh['ten_xe'], "Ma xe", dh['ma_xe']],
        ["Nam san xuat", str(dh['nam_sx']), "Mau sac", dh.get('mau_sac','N/A')],
        ["So khung (VIN)", dh.get('so_khung','N/A'), "So may", dh.get('so_may','N/A')],
    ]
    xt = Table(xe_data, colWidths=[4*cm,5*cm,4*cm,5*cm])
    xt.setStyle(TableStyle([
        ('GRID',(0,0),(-1,-1),0.3,colors.lightgrey),
        ('BACKGROUND',(0,0),(0,-1),colors.HexColor('#f3f0ff')),
        ('BACKGROUND',(2,0),(2,-1),colors.HexColor('#f3f0ff')),
        ('FONTNAME',(0,0),(0,-1),'Helvetica-Bold'),
        ('FONTNAME',(2,0),(2,-1),'Helvetica-Bold'),
        ('PADDING',(0,0),(-1,-1),8),
    ]))
    story.append(xt); story.append(Spacer(1,12))

    # ── Bảng thanh toán ───────────────────────────────────────────────────
    story.append(Paragraph("<b>CHI TIET THANH TOAN</b>",
        style("",11,True,colors.HexColor('#6d28d9'),0,0,6)))
    gia = dh['gia_ban_thuc']; ck = dh.get('chiet_khau',0) or 0; tt = gia - ck
    pay_data = [
        ["", "Gia tri"],
        ["Gia ban xe", f"{gia:,.0f} dong"],
        ["Chiet khau", f"- {ck:,.0f} dong"],
        ["TONG THANH TOAN", f"{tt:,.0f} dong"],
    ]
    pt = Table(pay_data, colWidths=[12*cm, 6*cm])
    pt.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#1e2236')),
        ('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
        ('FONTNAME',(0,3),(-1,3),'Helvetica-Bold'),
        ('BACKGROUND',(0,3),(-1,3),colors.HexColor('#6d28d9')),
        ('TEXTCOLOR',(0,3),(-1,3),colors.white),
        ('FONTSIZE',(0,3),(-1,3),12),
        ('ALIGN',(1,0),(1,-1),'RIGHT'),
        ('GRID',(0,0),(-1,-1),0.3,colors.lightgrey),
        ('PADDING',(0,0),(-1,-1),10),
    ]))
    story.append(pt); story.append(Spacer(1,16))

    # ── Ghi chú & Chữ ký ──────────────────────────────────────────────────
    if dh.get('ghi_chu'):
        story.append(Paragraph(f"Ghi chu: {dh['ghi_chu']}",
            style("",9,False,colors.grey)))
        story.append(Spacer(1,8))

    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey))
    ky_data = [[
        Paragraph("<b>Khach hang</b><br/><br/><br/>(Ky, ghi ro ho ten)",
            style("",9,False,colors.grey,1)),
        Paragraph("<b>Nhan vien ban hang</b><br/><br/><br/>(Ky, ghi ro ho ten)",
            style("",9,False,colors.grey,1)),
        Paragraph("<b>Giam doc</b><br/><br/><br/>(Ky dong dau)",
            style("",9,False,colors.grey,1)),
    ]]
    kt = Table(ky_data, colWidths=[6*cm,6*cm,6*cm])
    story.append(Spacer(1,8)); story.append(kt)

    story.append(Spacer(1,10))
    story.append(Paragraph(
        "Cam on quy khach da tin tuong AutoViet! | Tel: 1900-xxxx | autoviet.vn",
        style("",8,False,colors.grey,1)))

    doc.build(story)
    return fname


def in_phieu_dich_vu(dich_vu_id: int) -> str:
    """Xuất phiếu dịch vụ PDF"""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.units import cm
    except ImportError:
        raise Exception("Cần cài reportlab:\npip install reportlab")

    from database import get_conn
    conn = get_conn()
    dv = conn.execute("""
           SELECT dv.*,
                  x.hang_xe||' '||x.dong_xe as ten_xe, x.ma_xe, x.so_khung,
                  x.anh_url,
                  kh.ho_ten as ten_kh, kh.so_dt,
                  nv.ho_ten as ten_nv
           FROM dich_vu dv
           LEFT JOIN xe x ON dv.xe_id=x.id
           LEFT JOIN khach_hang kh ON dv.kh_id=kh.id
           LEFT JOIN nhan_vien nv ON dv.nv_id=nv.id
           WHERE dv.id=?""", (dich_vu_id,)).fetchone()
    conn.close()
    if not dv: raise Exception("Không tìm thấy phiếu dịch vụ!")
    dv = dict(dv)

    fname = f"phieu_dv_{dv['ma_dv']}.pdf"
    doc = SimpleDocTemplate(fname, pagesize=A4,
        rightMargin=1.5*cm, leftMargin=1.5*cm,
        topMargin=1.5*cm, bottomMargin=1.5*cm)

    def style(name, size=10, bold=False, color=colors.black, align=0):
        return ParagraphStyle(name, fontSize=size,
            fontName='Helvetica-Bold' if bold else 'Helvetica',
            textColor=color, alignment=align, spaceAfter=4)

    story = []
    story.append(Paragraph("<b>AUTOVIET — PHIEU DICH VU BAO DUONG</b>",
        style("",14,True,colors.HexColor('#006064'),1)))
    story.append(Paragraph(f"Ma phieu: {dv['ma_dv']} | Ngay nhan: {dv['ngay_nhan']} | {datetime.now().strftime('%H:%M %d/%m/%Y')}",
        style("",9,False,colors.grey,1)))
    story.append(Spacer(1,12))

    data = [
        ["THONG TIN", "CHI TIET"],
        ["Ten xe", dv.get('ten_xe','N/A')],
        ["Ma xe", dv.get('ma_xe','N/A')],
        ["So khung", dv.get('so_khung','N/A')],
        ["Khach hang", dv.get('ten_kh','N/A')],
        ["So dien thoai", dv.get('so_dt','N/A')],
        ["Ky thuat vien", dv.get('ten_nv','N/A')],
        ["Loai dich vu", dv.get('loai_dv','N/A')],
        ["Mo ta cong viec", dv.get('mo_ta','') or 'N/A'],
        ["Chi phi", f"{int(dv.get('chi_phi',0) or 0):,} dong"],
        ["Trang thai", dv.get('trang_thai','N/A')],
        ["Ngay hoan thanh", dv.get('ngay_hoan','Chua xong') or 'Chua xong'],
    ]
    t = Table(data, colWidths=[6*cm,12*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#006064')),
        ('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
        ('BACKGROUND',(0,1),(0,-1),colors.HexColor('#e0f7fa')),
        ('FONTNAME',(0,1),(0,-1),'Helvetica-Bold'),
        ('GRID',(0,0),(-1,-1),0.3,colors.lightgrey),
        ('PADDING',(0,0),(-1,-1),8),
        ('BACKGROUND',(0,9),(-1,9),colors.HexColor('#fffde7')),
        ('FONTSIZE',(0,9),(-1,9),11),
    ]))
    story.append(t)
    story.append(Spacer(1, 14))

    # Ảnh xe
    story.append(Paragraph("<b>ANH XE</b>",
                           style("", 11, True, colors.HexColor('#006064'), 0)))
    story.append(Spacer(1, 6))
    anh_url = dv.get("anh_url", "") or ""
    if anh_url and os.path.exists(anh_url):
        from reportlab.platypus import Image as RLImage
        try:
            img = RLImage(anh_url, width=10 * cm, height=7 * cm)
            img.hAlign = "LEFT"
            story.append(img)
        except Exception:
            story.append(Paragraph("(Khong the tai anh xe)",
                                   style("", 9, False, colors.grey)))
    else:
        no_img_data = [["[ Xe chua co anh ]"]]
        ni = Table(no_img_data, colWidths=[10 * cm], rowHeights=[3 * cm])
        ni.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0f4f8')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#94a3b8')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
        ]))
        story.append(ni)

    story.append(Spacer(1, 16))
    from reportlab.platypus import HRFlowable
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey))
    ky_data = [[
        Paragraph("<b>Khach hang</b><br/><br/><br/>(Ky ten)",
                  style("", 9, False, colors.grey, 1)),
        Paragraph("<b>Ky thuat vien</b><br/><br/><br/>(Ky ten)",
                  style("", 9, False, colors.grey, 1)),
        Paragraph("<b>Quan ly</b><br/><br/><br/>(Ky dong dau)",
                  style("", 9, False, colors.grey, 1)),
    ]]
    kt = Table(ky_data, colWidths=[6 * cm, 6 * cm, 6 * cm])
    story.append(Spacer(1, 8))
    story.append(kt)
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "Cam on quy khach da tin tuong AutoViet! | Tel: 1900-xxxx | autoviet.vn",
        style("", 8, False, colors.grey, 1)))

    doc.build(story)
    return fname
