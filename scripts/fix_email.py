from database import get_conn

conn = get_conn()
conn.execute("UPDATE users SET email='tngoquoc31@gmail.com' WHERE username='quoctuan01'")
conn.commit()
conn.close()
print("OK! Da cap nhat Gmail thanh cong!")