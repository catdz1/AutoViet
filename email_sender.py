"""
email_sender.py — Gửi mã xác nhận qua Gmail SMTP
Copy vào thư mục gốc (cùng chỗ main.py)
"""
import smtplib
import random
import string
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
# Lưu mã xác nhận tạm thời trong bộ nhớ
# {email: {"code": "123456", "expires": timestamp}}
_pending_codes = {}
CODE_EXPIRE_SECONDS = 300  # Mã hết hạn sau 5 phút
def generate_code() -> str:
    """Tạo mã xác nhận 6 chữ số"""
    return "".join(random.choices(string.digits, k=6))
def send_reset_code(to_email: str, ho_ten: str) -> tuple:
    """
    Gửi mã xác nhận về Gmail của nhân viên.
    Trả về (True, "OK") hoặc (False, "lý do lỗi")
    """
    try:
        from email_config import GMAIL_USER, GMAIL_APP_PASS, SENDER_NAME
    except ImportError:
        return False, "Chưa cấu hình email_config.py!"

    if not GMAIL_USER or GMAIL_USER == "your_email@gmail.com":
        return False, "Chưa cấu hình Gmail trong email_config.py!"

    code = generate_code()
    expires = time.time() + CODE_EXPIRE_SECONDS
    _pending_codes[to_email.lower()] = {"code": code, "expires": expires}
    # Nội dung email HTML đẹp
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  body {{ font-family: 'Segoe UI', Arial, sans-serif; background:#f5f5f5; margin:0; padding:20px; }}
  .container {{ max-width:480px; margin:0 auto; background:white; border-radius:12px;
                box-shadow:0 4px 20px rgba(0,0,0,0.1); overflow:hidden; }}
  .header {{ background:linear-gradient(135deg,#6d28d9,#7c3aed);
             padding:28px; text-align:center; }}
  .header h1 {{ color:white; margin:0; font-size:22px; }}
  .header p  {{ color:rgba(255,255,255,0.8); margin:6px 0 0; font-size:13px; }}
  .body {{ padding:32px; }}
  .greeting {{ font-size:15px; color:#374151; margin-bottom:20px; }}
  .code-box {{ background:#f3f0ff; border:2px dashed #7c3aed; border-radius:12px;
               padding:24px; text-align:center; margin:24px 0; }}
  .code {{ font-size:38px; font-weight:800; color:#6d28d9; letter-spacing:12px;
           font-family:monospace; }}
  .code-label {{ font-size:12px; color:#9ca3af; margin-top:8px; }}
  .warning {{ background:#fef3c7; border-left:4px solid #f59e0b; border-radius:4px;
              padding:12px 16px; margin:20px 0; font-size:13px; color:#92400e; }}
  .footer {{ background:#f9fafb; padding:20px; text-align:center;
             font-size:12px; color:#9ca3af; border-top:1px solid #e5e7eb; }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>🚗 AutoViet</h1>
    <p>Hệ thống Quản lý Đại lý Xe Hơi</p>
  </div>
  <div class="body">
    <p class="greeting">Xin chào <strong>{ho_ten}</strong>,</p>
    <p>Chúng tôi nhận được yêu cầu đặt lại mật khẩu cho tài khoản của bạn.
       Sử dụng mã xác nhận bên dưới để tiếp tục:</p>

    <div class="code-box">
      <div class="code">{code}</div>
      <div class="code-label">Mã xác nhận (hết hạn sau 5 phút)</div>
    </div>

    <div class="warning">
      ⚠️ <strong>Lưu ý bảo mật:</strong> Không chia sẻ mã này với bất kỳ ai.
      Nếu bạn không yêu cầu đặt lại mật khẩu, hãy bỏ qua email này.
    </div>

    <p style="color:#6b7280; font-size:13px;">
      Mã sẽ hết hạn lúc <strong>{time.strftime('%H:%M:%S', time.localtime(expires))}</strong>
    </p>
  </div>
  <div class="footer">
    © 2025 AutoViet — Hệ thống Quản lý Đại lý Xe Hơi<br>
    Email này được gửi tự động, vui lòng không trả lời.
  </div>
</div>
</body>
</html>
"""

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "🔐 Mã xác nhận đặt lại mật khẩu AutoViet"
        msg["From"]    = f"{SENDER_NAME} <{GMAIL_USER}>"
        msg["To"]      = to_email

        msg.attach(MIMEText(
            f"Mã xác nhận của bạn: {code}\nHết hạn sau 5 phút.", "plain", "utf-8"))
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASS)
            server.sendmail(GMAIL_USER, to_email, msg.as_string())

        return True, f"Mã xác nhận đã gửi đến {to_email}"

    except smtplib.SMTPAuthenticationError:
        return False, ("Lỗi xác thực Gmail!\n\n"
                       "Kiểm tra lại GMAIL_USER và GMAIL_APP_PASS\n"
                       "trong file email_config.py\n\n"
                       "Hướng dẫn: myaccount.google.com/apppasswords")
    except smtplib.SMTPException as e:
        return False, f"Lỗi gửi email: {str(e)}"
    except Exception as e:
        return False, f"Lỗi kết nối: {str(e)}"


def verify_code(email: str, code: str) -> tuple:
    """
    Xác nhận mã.
    Trả về (True, "ok") hoặc (False, "lý do")
    """
    email = email.lower().strip()
    entry = _pending_codes.get(email)

    if not entry:
        return False, "Chưa có mã xác nhận cho email này!"
    if time.time() > entry["expires"]:
        del _pending_codes[email]
        return False, "Mã xác nhận đã hết hạn! Vui lòng gửi lại."
    if entry["code"] != code.strip():
        return False, "Mã xác nhận không đúng!"

    # Xoá mã sau khi dùng
    del _pending_codes[email]
    return True, "ok"


def reset_password_by_email(email: str, new_password: str) -> tuple:
    """Đặt lại mật khẩu sau khi xác nhận thành công"""
    import hashlib
    from database import get_conn

    if len(new_password) < 6:
        return False, "Mật khẩu phải có ít nhất 6 ký tự!"

    conn = get_conn()
    row = conn.execute(
        "SELECT id FROM users WHERE LOWER(email)=? AND active=1",
        (email.lower(),)
    ).fetchone()

    if not row:
        conn.close()
        return False, "Không tìm thấy tài khoản với email này!"

    new_hash = hashlib.sha256(new_password.encode()).hexdigest()
    conn.execute("UPDATE users SET password=? WHERE id=?", (new_hash, row["id"]))
    conn.commit(); conn.close()
    return True, "Đặt lại mật khẩu thành công!"
