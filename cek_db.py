import sqlite3

conn = sqlite3.connect('users.db')

print("\n=== TABEL ===")
tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
print(tables.fetchall())

print("\n=== USERS ===")
users = conn.execute("SELECT * FROM users")
for u in users:
    print(u)

print("\n=== HASIL ===")
hasil = conn.execute("SELECT * FROM hasil_prediksi")
for h in hasil:
    print(h)

conn.close()