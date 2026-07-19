from flask import Flask, render_template, request, redirect, session, Response, abort
from werkzeug.security import generate_password_hash, check_password_hash
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from datetime import datetime
from functools import wraps
from flask import session, abort
from functools import wraps
from flask import session, abort, render_template, request, redirect

import psycopg2
import psycopg2.extras  
import joblib
import json
import io
import re  
import numpy as np
import pandas as pd

app = Flask(__name__)
app.secret_key = "secret"
# ================= DEKORATOR ADMIN =================
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function
# ================= ADMIN ROUTES =================
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute("SELECT * FROM riwayat")
            semua_riwayat = cursor.fetchall()
        return render_template('admin_dashboard.html', riwayat=semua_riwayat)
    finally:
        conn.close()

@app.route('/admin/riwayat')
@admin_required
def admin_riwayat():
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            # Mengambil semua riwayat dari seluruh user, urutkan dari yang terbaru
            cursor.execute("SELECT * FROM riwayat ORDER BY id DESC")
            semua_riwayat = cursor.fetchall()
        return render_template('admin_riwayat.html', riwayat=semua_riwayat)
    finally:
        conn.close()

@app.route('/admin/users')
@admin_required
def admin_users():
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute('SELECT username, role, is_active FROM users')
            users = cursor.fetchall()
        return render_template('admin_users.html', users=users)
    finally:
        conn.close()

@app.route('/admin/statistik')
@admin_required
def admin_statistik():
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            # Menggunakan logika SQL yang lebih kuat untuk mengelompokkan data
            cursor.execute('''
                SELECT 
                    CASE 
                        WHEN LOWER(TRIM(hasil)) LIKE 'tidak%ispa%' THEN 'Tidak ISPA'
                        WHEN LOWER(TRIM(hasil)) = 'ispa' THEN 'ISPA'
                        ELSE hasil 
                    END as hasil, 
                    SUM(count) as total
                FROM (
                    SELECT hasil, COUNT(*) as count 
                    FROM riwayat 
                    GROUP BY hasil
                ) as subquery
                GROUP BY 1
            ''')
            stats = cursor.fetchall()
        return render_template('admin_statistik.html', stats=stats)
    finally:
        conn.close()

@app.route('/admin/toggle_user/<username>', methods=['POST'])
@admin_required
def toggle_user(username):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE users SET is_active = NOT is_active WHERE username = %s", (username,))
        conn.commit()
    finally:
        conn.close()
    return redirect('/admin/users')

# ================= DATABASE & MODEL =================
DATABASE_URL = "postgresql://usrcincbrlnv5ctctci3:IBfGxEleM4JgSh94b4slGSAjUVqw1K@bzv6ndii9goa0jgadd44-postgresql.services.clever-cloud.com:50013/bzv6ndii9goa0jgadd44"

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

model = joblib.load("model_saved/model_rf.pkl")
fitur_urutan = joblib.load("model_saved/fitur_urutan.pkl")
scaler = joblib.load("model_saved/scaler.pkl")
importance = joblib.load("model_saved/importance.pkl")
if __name__ == '__main__':
    app.run(debug=True)

# ================= HOME =================
@app.route('/')
def home():
    return render_template('home.html')


# ================= FORM =================
@app.route('/form')
def form():
    if 'username' not in session:
        return redirect('/login')
    return render_template('index.html')


# ================= VALIDATION FUNCTION =================
def validasi_password(password):
    if len(password) < 8:
        return "Password minimal 6 karakter!"
    if not re.search(r"[A-Z]", password):
        return "Harus ada huruf besar!"
    if not re.search(r"[a-z]", password):
        return "Harus ada huruf kecil!"
    if not re.search(r"[0-9]", password):
        return "Harus ada angka!"
    return None


# ================= REGISTER =================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')  # 🔥 tambahan

        # 🔥 VALIDASI
        if not username or not password:
            return render_template('register.html', error="Semua field wajib diisi!")

        if password != confirm:
            return render_template('register.html', error="Konfirmasi password tidak cocok!")

        error_pass = validasi_password(password)
        if error_pass:
            return render_template('register.html', error=error_pass)

        conn = get_db_connection()
        try:
            cursor = conn.cursor()

            # 🔥 cek username sudah ada
            cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
            existing = cursor.fetchone()

            if existing:
                return render_template('register.html', error="Username sudah digunakan!")

            hashed_password = generate_password_hash(password)

            cursor.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s)",
                (username, hashed_password)
            )
            conn.commit()
            cursor.close()
        finally:
            conn.close()

        return redirect('/login')

    return render_template('register.html')


# ================= LOGIN =================
# ================= LOGIN =================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            return render_template('login.html', error="Isi semua field!")

        conn = get_db_connection()
        try:
            # Menggunakan RealDictCursor agar hasil query bisa diakses seperti dictionary
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            # Pastikan kolom role dan is_active ada di tabel users
            cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
            user = cursor.fetchone()
            cursor.close()
        finally:
            conn.close()

        if not user:
            return render_template('login.html', error="User tidak ditemukan!")

        # Mengecek password
        if check_password_hash(user['password'], password):
            # Cek apakah kolom is_active ada dan apakah user diblokir
            if user.get('is_active') == False:
                return render_template('login.html', error="Akun Anda telah diblokir oleh admin!")

            # Menyimpan data ke session
            session['username'] = user['username']
            # Menggunakan .get() agar tidak error jika kolom role tidak ada
            session['role'] = user.get('role', 'user') 
            
            # Redirect berdasarkan role
            if session['role'] == 'admin':
                return redirect('/admin/dashboard')
            return redirect('/')
        else:
            return render_template('login.html', error="Password salah!")

    return render_template('login.html')


# ================= LOGOUT =================
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')


# ================= PREDICT =================
@app.route('/predict', methods=['POST'])
def predict():
    probabilitas = None
    hasil = None

    try:
        if 'username' not in session:
            return redirect('/login')

 # ================= INPUT =================
        nama = request.form.get("nama", "").strip()
        umur_raw = request.form.get("umur", 0)

        try:
            umur = float(umur_raw)
        except:
            umur = 0.0

        gejala = []
        jawaban_dict = {}

        for i in range(16):
            nilai = request.form.get(f"q{i}")

            try:
                # Simpan nilai asli (1-5) ke variabel sementara
                val_asli = float(nilai) if nilai else 1.0
            except:
                val_asli = 1.0

            # Simpan ke dict untuk keperluan database/tampilan detail
            jawaban_dict[f"q{i}"] = int(val_asli)

            # Konversi ke biner hanya untuk input model
            val_biner = 1 if val_asli >= 3 else 0
            gejala.append(val_biner)

        # ================= DATAFRAME =================
        input_data = [umur] + gejala

        if len(input_data) != len(fitur_urutan):
            raise ValueError("Jumlah fitur tidak sesuai dengan model")

        input_df = pd.DataFrame([input_data], columns=fitur_urutan)

        # ================= SCALING =================
        input_scaled = scaler.transform(input_df)

        # ================= PREDIKSI =================
        hasil = model.predict(input_scaled)[0]

        if hasattr(model, "predict_proba"):
            probabilitas = model.predict_proba(input_scaled)[0]
        else:
            probabilitas = [0.5, 0.5]  # fallback aman

        # ================= AMBIL INDEX ISPA =================
        kelas = list(model.classes_)

        if 0 in kelas:
            idx_ispa = kelas.index(0)
        else:
            idx_ispa = 0

        persen = round(float(probabilitas[idx_ispa]) * 100, 2)

        # ================= DIAGNOSIS =================
        diagnosis = "ISPA" if hasil == 0 else "Tidak ISPA"

        # ================= TOP 3 GEJALA =================
        top3 = sorted(
            [(f"q{i}", gejala[i]) for i in range(len(gejala))],
            key=lambda x: x[1],
            reverse=True
        )[:3]

        # ================= DEBUG =================
        print("=== DEBUG WEB ===")
        print("Nama:", nama)
        print("Umur:", umur)
        print("Gejala:", gejala)
        print("Input:", input_df)
        print("Scaled:", input_scaled)
        print("Prob:", probabilitas)
        print("Classes:", kelas)
        print("Persen:", persen)
        print("Hasil:", hasil)

        # ================= SIMPAN DB =================
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO riwayat (username, nama, umur, jawaban, hasil, persen)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                session['username'],
                nama,
                umur,
                json.dumps(jawaban_dict),
                diagnosis,
                persen
            ))
            conn.commit()
            cursor.close()
        finally:
            conn.close()

        # ================= RETURN =================
        return render_template(
            "result.html",
            persen=persen,
            nama=nama,
            umur=umur,
            top3=top3,
            diagnosis=diagnosis,  # 🔥 tambahan penting
            debug_input=input_df.to_dict()
        )

    except Exception as e:
        print("ERROR:", e)
        print("=== CEK MODEL ===")
        if hasattr(model, "classes_"):
            print("Classes:", model.classes_)
        print("Probabilitas:", probabilitas)
        print("Prediksi:", hasil)

        return f"<h2>Error: {str(e)}</h2>"
    
# ================= RIWAYAT =================
@app.route('/riwayat')
def riwayat():
    if 'username' not in session:
        return redirect('/login')

    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(
            "SELECT * FROM riwayat WHERE username=%s ORDER BY id DESC",
            (session['username'],)
        )
        data = cursor.fetchall()
        cursor.close()
    finally:
        conn.close()

    return render_template('riwayat.html', data=data)


# ================= DETAIL =================
@app.route('/detail/<int:id>')
def detail(id):
    if 'username' not in session:
        return redirect('/login')

    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM riwayat WHERE id=%s", (id,))
        data = cursor.fetchone()
        cursor.close()
    finally:
        conn.close()

    if not data:
        return "Data tidak ditemukan!"

    jawaban = json.loads(data['jawaban'])

    return render_template(
        'detail.html',
        data=data,
        jawaban=jawaban
    )


# ================= DOWNLOAD PDF =================
@app.route('/download_pdf/<int:id>')
def download_pdf(id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM riwayat WHERE id=%s", (id,))
        data = cursor.fetchone()
        cursor.close()
    finally:
        conn.close()

    if not data:
        return "Data tidak ditemukan!"

    jawaban = json.loads(data['jawaban'])

    pertanyaan = {
        'q0': 'Batuk kering', 'q1': 'Batuk berdahak', 'q2': 'Demam', 'q3': 'Pilek',
        'q4': 'Hidung tersumbat', 'q5': 'Sesak napas', 'q6': 'Nyeri tenggorokan',
        'q7': 'Sakit kepala', 'q8': 'Mual / muntah', 'q9': 'Nyeri dada',
        'q10': 'Suara serak', 'q11': 'Kelelahan', 'q12': 'Keringat malam',
        'q13': 'Nafsu makan turun', 'q14': 'Hilang penciuman', 'q15': 'Nyeri saat menelan'
    }

    teks_skala = {
        1: "1 (Tidak Ada)",
        2: "2 (Sangat Ringan)",
        3: "3 (Sedang)",
        4: "4 (Parah)",
        5: "5 (Sangat Parah)"
    }

    # ====== BUAT PDF ======
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    elements = []

    # ====== JUDUL ======
    elements.append(Paragraph("<b>HASIL ANALISIS KESEHATAN</b>", styles['Title']))
    elements.append(Spacer(1, 10))

    # ====== TANGGAL ======
    elements.append(Paragraph(
        f"Tanggal: {datetime.now().strftime('%d-%m-%Y %H:%M')}",
        styles['Normal']
    ))
    elements.append(Spacer(1, 20))

    # ====== DATA PASIEN ======
    elements.append(Paragraph("<b>Data Pasien</b>", styles['Heading2']))

    pasien = [
        ["Nama", data['nama']],
        ["Umur", f"{data['umur']} tahun"]
    ]

    table_pasien = Table(pasien, colWidths=[100, 300])
    table_pasien.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('BACKGROUND', (0,0), (-1,-1), colors.whitesmoke)
    ]))

    elements.append(table_pasien)
    elements.append(Spacer(1, 20))

    # ====== DATA GEJALA ======
    elements.append(Paragraph("<b>Data Gejala</b>", styles['Heading2']))

    table_data = [["No", "Gejala", "Tingkat Keparahan"]]

    for i, key in enumerate(pertanyaan.keys()):
        val = int(jawaban.get(key, 0))
        keterangan = teks_skala.get(val, "Tidak Diisi")

        table_data.append([
            i + 1,
            pertanyaan[key],
            keterangan
        ])

    table = Table(table_data, colWidths=[40, 240, 140])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('ALIGN', (0,0), (-1,0), 'CENTER')
    ]))

    elements.append(table)
    elements.append(Spacer(1, 20))

    # ====== HASIL ANALISIS (TANPA ISPA) ======
    elements.append(Paragraph("<b>Hasil Analisis</b>", styles['Heading2']))
    elements.append(Spacer(1, 10))

    # Status berdasarkan persen
    persen = float(data['persen'])

    if persen < 40:
        status = "Risiko Rendah"
        warna = colors.green
    elif persen < 70:
        status = "Risiko Sedang"
        warna = colors.orange
    else:
        status = "Risiko Tinggi"
        warna = colors.red

    # Box hasil
    hasil_box = Table([
        ["Status", status],
        ["Tingkat Risiko", f"{persen}%"]
    ], colWidths=[150, 250])

    hasil_box.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('BACKGROUND', (0,0), (-1,0), colors.whitesmoke),
        ('TEXTCOLOR', (1,0), (1,0), warna),
        ('TEXTCOLOR', (1,1), (1,1), warna),
    ]))

    elements.append(hasil_box)

    # ====== BUILD PDF ======
    doc.build(elements)
    buffer.seek(0)

    return Response(
        buffer,
        mimetype='application/pdf',
        headers={"Content-Disposition": "attachment;filename=hasil_analisis.pdf"}
    )


@app.route('/hapus/<int:id>', methods=['POST'])
def hapus(id):
    if 'username' not in session:
        return redirect('/login')

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM riwayat WHERE id=%s", (id,))
        conn.commit()
        cursor.close()
    finally:
        conn.close()

    return redirect('/riwayat')


@app.route('/tentang')
def tentang():
    return render_template('tentang.html')


@app.route('/cara_kerja')
def cara_kerja():
    return render_template('cara_kerja.html')


@app.route('/home')
def home_page():
    return render_template('home.html')


if __name__ == '__main__':
    app.run(debug=True)