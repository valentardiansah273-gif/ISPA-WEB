import os
import joblib
import pandas as pd
import numpy as np

print("=== 1. MENGECEK KEBERADAAN FILE MODEL ===")
files_to_check = [
    "model_saved/model_rf.pkl",
    "model_saved/scaler.pkl",
    "model_saved/fitur_urutan.pkl"
]

for f in files_to_check:
    exist = os.path.exists(f)
    exist = os.path.exists(f)
    print(f"- {f}: {'ADA ✅' if exist else 'TIDAK ADA ❌'}")

try:
    print("\n=== 2. MEMUAT FILE MODEL & SCALER ===")
    model = joblib.load("model_saved/model_rf.pkl")
    scaler = joblib.load("model_saved/scaler.pkl")
    fitur_urutan = joblib.load("model_saved/fitur_urutan.pkl")
    
    print(f"Jumlah fitur yang diharapkan model: {len(fitur_urutan)}")
    print(f"Daftar fitur: {fitur_urutan}")
    print(f"Kelas model (model.classes_): {model.classes_}")

    print("\n=== 3. MENCOBA PREDIKSI DUMMY (DATA COBA-COBA) ===")
    # Membuat data dummy dengan panjang yang sama persis dengan jumlah fitur_urutan
    # Nilai 1 untuk semua fitur
    dummy_data = [1.0] * len(fitur_urutan)
    
    # Ubah ke DataFrame sesuai urutan fitur
    input_df = pd.DataFrame([dummy_data], columns=fitur_urutan)
    
    # Lakukan scaling
    input_scaled = scaler.transform(input_df)
    
    # Lakukan prediksi
    prediksi = model.predict(input_scaled)
    probabilitas = model.predict_proba(input_scaled)
    
    print(f"Hasil Prediksi Dummy: {prediksi[0]}")
    print(f"Probabilitas Dummy: {probabilitas[0]}")
    print("\n✅ Uji coba berhasil! Model dan scaler dapat berfungsi normal.")

except Exception as e:
    print(f"\n❌ TERJADI ERROR SAAT MEMUAT/PREDIKSI:\n{e}")