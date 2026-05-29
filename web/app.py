from flask import Flask, render_template, request, redirect, session, Response
from werkzeug.security import generate_password_hash, check_password_hash
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from datetime import datetime
import psycopg2
import psycopg2.extras  # 🔥 WAJIB: Untuk membaca hasil query dalam bentuk dictionary
import joblib
import json
import io

app = Flask(__name__)
app.secret_key = "secret"

# ================= MODEL =================
model = joblib.load("model_saved/model_rf.pkl")

# 🔥 load urutan fitur (WAJIB)
fitur_urutan = joblib.load("model_saved/fitur_urutan.pkl")

# ================= DATABASE (SUPABASE POOLER) =================
DATABASE_URL = "postgresql://postgres:Val_27_03_200@db.ujnymohyappmueveidlq.supabase.co:6543/postgres?pgbouncer=true"

db = psycopg2.connect(DATABASE_URL)


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


# ================= REGISTER =================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        hashed_password = generate_password_hash(password)

        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (username, hashed_password)
        )
        db.commit()
        cursor.close()

        return redirect('/login')

    return render_template('register.html')


# ================= LOGIN =================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # 🔥 Menggunakan RealDictCursor menggantikan dictionary=True milik MySQL
        cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(
            "SELECT * FROM users WHERE username=%s",
            (username,)
        )
        user = cursor.fetchone()
        cursor.close()

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
    if 'username' not in session:
        return redirect('/login')

    nama = request.form.get('nama')
    umur = request.form.get('umur')

    if not nama or not umur:
        return "Nama atau umur tidak boleh kosong!"

    umur = int(umur)

    jawaban_dict = {}
    for i in range(16):
        val = int(request.form.get(f'q{i}'))
        jawaban_dict[f'q{i}'] = val

    data_map = {
        'Umur': umur,
        'Batuk_Kering': jawaban_dict['q0'],
        'Batuk_Berdahak': jawaban_dict['q1'],
        'Demam': jawaban_dict['q2'],
        'Pilek': jawaban_dict['q3'],
        'Hidung_Tersumbat': jawaban_dict['q4'],
        'Sesak_Napas': jawaban_dict['q5'],
        'Nyeri_Tenggorokan': jawaban_dict['q6'],
        'Sakit_Kepala': jawaban_dict['q7'],
        'Mual_Muntah': jawaban_dict['q8'],
        'Nyeri_Dada': jawaban_dict['q9'],
        'Suara_Serak': jawaban_dict['q10'],
        'Kelelahan': jawaban_dict['q11'],
        'Berkeringat_Malam': jawaban_dict['q12'],
        'Nafsu_Makan_Turun': jawaban_dict['q13'],
        'Hilang_Penciuman': jawaban_dict['q14'],
        'Nyeri_Saat_Menelan': jawaban_dict['q15'],
    }

    data = [data_map[f] for f in fitur_urutan]

    prob = model.predict_proba([data])[0][1]
    persen = round(prob * 100, 2)
    hasil = "ISPA" if prob > 0.5 else "Tidak ISPA"

    jawaban_json = json.dumps(jawaban_dict)

    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO riwayat 
        (username, nama, umur, hasil, persen, jawaban) 
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (session['username'], nama, umur, hasil, persen, jawaban_json))
    db.commit()
    cursor.close()

    return render_template(
        'result.html',
        hasil=hasil,
        persen=persen,
        nama=nama,
        umur=umur
    )


# ================= RIWAYAT =================
@app.route('/riwayat')
def riwayat():
    if 'username' not in session:
        return redirect('/login')

    # 🔥 Menggunakan RealDictCursor
    cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute(
        "SELECT * FROM riwayat WHERE username=%s ORDER BY id DESC",
        (session['username'],)
    )
    data = cursor.fetchall()
    cursor.close()

    return render_template('riwayat.html', data=data)


# ================= DETAIL =================
@app.route('/detail/<int:id>')
def detail(id):
    if 'username' not in session:
        return redirect('/login')

    # 🔥 Menggunakan RealDictCursor
    cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM riwayat WHERE id=%s", (id,))
    data = cursor.fetchone()
    cursor.close()

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

    # 🔥 Menggunakan RealDictCursor
    cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM riwayat WHERE id=%s", (id,))
    data = cursor.fetchone()
    cursor.close()

    jawaban = json.loads(data['jawaban'])

    pertanyaan = {
        'q0': 'Batuk kering',
        'q1': 'Batuk berdahak',
        'q2': 'Demam',
        'q3': 'Pilek',
        'q4': 'Hidung tersumbat',
        'q5': 'Sesak napas',
        'q6': 'Nyeri tenggorokan',
        'q7': 'Sakit kepala',
        'q8': 'Mual / muntah',
        'q9': 'Nyeri dada',
        'q10': 'Suara serak',
        'q11': 'Kelelahan',
        'q12': 'Keringat malam',
        'q13': 'Nafsu makan turun',
        'q14': 'Hilang penciuman',
        'q15': 'Nyeri saat menelan'
    }

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    elements = []

    # HEADER
    elements.append(Paragraph("<b>HASIL DIAGNOSIS ISPA</b>", styles['Title']))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(
        f"Tanggal: {datetime.now().strftime('%d-%m-%Y %H:%M')}",
        styles['Normal']
    ))
    elements.append(Spacer(1, 20))

    # DATA PASIEN
    pasien = [
        ["Nama", data['nama']],
        ["Umur", str(data['umur'])]
    ]

    table_pasien = Table(pasien, colWidths=[100, 300])
    table_pasien.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('BACKGROUND', (0,0), (-1,-1), colors.whitesmoke)
    ]))

    elements.append(Paragraph("<b>Data Pasien</b>", styles['Heading2']))
    elements.append(table_pasien)
    elements.append(Spacer(1, 20))

    # GEJALA
    table_data = [["No", "Gejala", "Jawaban"]]

    for i, (key, value) in enumerate(jawaban.items()):
        table_data.append([
            i + 1,
            pertanyaan.get(key, key),
            "Ya" if value == 1 else "Tidak"
        ])

    table = Table(table_data, colWidths=[50, 250, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))

    elements.append(Paragraph("<b>Data Gejala</b>", styles['Heading2']))
    elements.append(table)
    elements.append(Spacer(1, 20))

    # HASIL
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

    elements.append(Paragraph(
        f"Tingkat Risiko: <b>{data['persen']}%</b>",
        styles['Normal']
    ))

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

    cursor = db.cursor()
    cursor.execute("DELETE FROM riwayat WHERE id=%s", (id,))
    db.commit()
    cursor.close()

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


# ================= RUN =================
if __name__ == '__main__':
    app.run(debug=True)