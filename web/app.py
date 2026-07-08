from flask import Flask, render_template, request, redirect, session, Response
from werkzeug.security import generate_password_hash, check_password_hash
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from datetime import datetime

import psycopg2
import psycopg2.extras  
import joblib
import json
import io
import re  
import numpy as np

app = Flask(__name__)
app.secret_key = "secret"

# ================= MODEL =================
model = joblib.load("model_saved/model_rf.pkl")

# 🔥 load urutan fitur (WAJIB)
fitur_urutan = joblib.load("model_saved/fitur_urutan.pkl")
scaler = joblib.load("model_saved/scaler.pkl")

# ================= DATABASE URL =================
DATABASE_URL = "postgresql://usrcincbrlnv5ctctci3:IBfGxEleM4JgSh94b4slGSAjUVqw1K@bzv6ndii9goa0jgadd44-postgresql.services.clever-cloud.com:50013/bzv6ndii9goa0jgadd44"

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)


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
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            return render_template('login.html', error="Isi semua field!")

        conn = get_db_connection()
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute(
                "SELECT * FROM users WHERE username=%s",
                (username,)
            )
            user = cursor.fetchone()
            cursor.close()
        finally:
            conn.close()

        if not user:
            return render_template('login.html', error="User tidak ditemukan!")

        if check_password_hash(user['password'], password):
            session['username'] = user['username']
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
try:
    # Ambil input dari form sesuai urutan fitur
    input_data = []

    for fitur in fitur_urutan:
        nilai = request.form.get(fitur)

        if nilai is None or nilai == "":
            nilai = 0  # default kalau kosong
        else:
            nilai = float(nilai)

        input_data.append(nilai)

    # Ubah ke numpy array
    input_array = np.array(input_data).reshape(1, -1)

    # =========================
    # WAJIB: SCALING (INI YANG SERING LUPA)
    # =========================
    input_scaled = scaler.transform(input_array)

    # Prediksi
    hasil = model.predict(input_scaled)[0]
    probabilitas = model.predict_proba(input_scaled)[0]

    # Mapping hasil (opsional, sesuaikan label kamu)
    if hasil == 1:
        diagnosis = "Terindikasi ISPA"
    else:
        diagnosis = "Tidak Terindikasi ISPA"

    return render_template(
        'index.html',
        prediction_text=diagnosis,
        probability=round(max(probabilitas) * 100, 2)
    )

except Exception as e:
    return f"Terjadi error: {str(e)}"

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
        1: "1 (Tidak Anda)",
        2: "2 (Ringan)",
        3: "3 (Sedang)",
        4: "4 (Parah)",
        5: "5 (Sangat Berat)"
    }

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("<b>HASIL DIAGNOSIS ISPA</b>", styles['Title']))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(f"Tanggal: {datetime.now().strftime('%d-%m-%Y %H:%M')}", styles['Normal']))
    elements.append(Spacer(1, 20))

    pasien = [["Nama", data['nama']], ["Umur", str(data['umur'])]]
    table_pasien = Table(pasien, colWidths=[100, 300])
    table_pasien.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('BACKGROUND', (0,0), (-1,-1), colors.whitesmoke)
    ]))
    elements.append(Paragraph("<b>Data Pasien</b>", styles['Heading2']))
    elements.append(table_pasien)
    elements.append(Spacer(1, 20))

    table_data = [["No", "Gejala", "Tingkat Keparahan"]]
    for i, (key, value) in enumerate(jawaban.items()):
        keterangan = teks_skala.get(int(value), str(value))
        table_data.append([i + 1, pertanyaan.get(key, key), keterangan])

    table = Table(table_data, colWidths=[50, 230, 120])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))
    elements.append(Paragraph("<b>Data Gejala</b>", styles['Heading2']))
    elements.append(table)
    elements.append(Spacer(1, 20))

    warna = colors.red if data['hasil'] == "ISPA" else colors.green
    hasil_box = Table([[data['hasil']]], colWidths=[400])
    hasil_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), warna),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTSIZE', (0,0), (-1,-1), 16),
    ]))
    elements.append(Paragraph("<b>Hasil Diagnosis</b>", styles['Heading2']))
    elements.append(hasil_box)
    elements.append(Spacer(1, 15))
    elements.append(Paragraph(f"Tingkat Risiko: <b>{data['persen']}%</b>", styles['Normal']))

    doc.build(elements)
    buffer.seek(0)

    return Response(
        buffer,
        mimetype='application/pdf',
        headers={"Content-Disposition": "attachment;filename=hasil_prediksi.pdf"}
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