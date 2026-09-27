content = open('views/thanh_toan_view.py', 'r', encoding='utf-8').read()

# Tang kich thuoc nut de de bam hon
content = content.replace(
    'btn_ask.setStyleSheet("background:#2563eb;color:white;border:none;border-radius:8px;padding:10px 20px;font-size:13px;font-weight:700;")',
    'btn_ask.setStyleSheet("background:#2563eb;color:white;border:none;border-radius:8px;padding:14px 28px;font-size:14px;font-weight:700;")'
)
content = content.replace(
    'btn_qr.setStyleSheet("background:#059669;color:white;border:none;border-radius:8px;padding:10px 16px;font-size:12px;font-weight:700;")',
    'btn_qr.setStyleSheet("background:#059669;color:white;border:none;border-radius:8px;padding:14px 24px;font-size:13px;font-weight:700;")'
)
content = content.replace(
    'btn_nhac.setStyleSheet("background:#d97706;color:white;border:none;border-radius:8px;padding:10px 16px;font-size:12px;font-weight:700;")',
    'btn_nhac.setStyleSheet("background:#d97706;color:white;border:none;border-radius:8px;padding:14px 24px;font-size:13px;font-weight:700;")'
)

open('views/thanh_toan_view.py', 'w', encoding='utf-8').write(content)
print("Xong!")