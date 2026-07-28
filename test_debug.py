import joblib
import pandas as pd
import numpy as np

print("=== MEMUAT MODEL, SCALER, DAN FITUR ===")
try:
    model = joblib.load("model_saved/model_rf.pkl")
    scaler = joblib.load("model_saved/scaler.pkl")
    fitur_urutan = joblib.load("model_saved/fitur_urutan.pkl")
    print("Berhasil memuat file-file model! ✅\n")
except Exception as e:
    print(f"Gagal memuat file: {e}")
    exit()

# ================= SIMULASI 1: KASUS GEJALA RINGAN (NILAI 1 / KECIL) =================
print("--- SIMULASI 1: INPUT GEJALA RINGAN (Semua 1 / Tidak Ada) ---")
# Buat data dummy di mana umur 22 dan semua gejala bernilai 1 (biner 0)
data_ringan = {
    'Umur': [22.0],
    'Batuk_Kering': [0], 'Batuk_Berdahak': [0], 'Demam': [0], 'Pilek': [0],
    'Hidung_Tersumbat': [0], 'Sesak_Napas': [0], 'Nyeri_Tenggorokan': [0],
    'Sakit_Kepala': [0], 'Mual_Muntah': [0], 'Nyeri_Dada': [0],
    'Suara_Serak': [0], 'Kelelahan': [0], 'Berkeringat_Malam': [0],
    'Nafsu_Makan_Turun': [0], 'Hilang_Penciuman': [0], 'Nyeri_Saat_Menelan': [0]
}

df_ringan = pd.DataFrame(data_ringan)[fitur_urutan]
scaled_ringan = scaler.transform(df_ringan)

pred_ringan = model.predict(scaled_ringan)[0]
prob_ringan = model.predict_proba(scaled_ringan)[0]

print(f"Model Classes (Urutan Kelas): {model.classes_}")
print(f"Hasil Prediksi (0 atau 1): {pred_ringan}")
print(f"Array Probabilitas: {prob_ringan}")
print(f"Persentase Kelas Indeks 1: {round(prob_ringan[1] * 100, 2)}%")
print(f"Persentase Kelas Indeks 0: {round(prob_ringan[0] * 100, 2)}%\n")


# ================= SIMULASI 2: KASUS GEJALA BERAT (NILAI 5 / PARAH) =================
print("--- SIMULASI 2: INPUT GEJALA BERAT (Semua Parah / Biner 1) ---")
data_berat = {
    'Umur': [22.0],
    'Batuk_Kering': [1], 'Batuk_Berdahak': [1], 'Demam': [1], 'Pilek': [1],
    'Hidung_Tersumbat': [1], 'Sesak_Napas': [1], 'Nyeri_Tenggorokan': [1],
    'Sakit_Kepala': [1], 'Mual_Muntah': [1], 'Nyeri_Dada': [1],
    'Suara_Serak': [1], 'Kelelahan': [1], 'Berkeringat_Malam': [1],
    'Nafsu_Makan_Turun': [1], 'Hilang_Penciuman': [1], 'Nyeri_Saat_Menelan': [1]
}

df_berat = pd.DataFrame(data_berat)[fitur_urutan]
scaled_berat = scaler.transform(df_berat)

pred_berat = model.predict(scaled_berat)[0]
prob_berat = model.predict_proba(scaled_berat)[0]

print(f"Hasil Prediksi (0 atau 1): {pred_berat}")
print(f"Array Probabilitas: {prob_berat}")
print(f"Persentase Kelas Indeks 1: {round(prob_berat[1] * 100, 2)}%")
print(f"Persentase Kelas Indeks 0: {round(prob_berat[0] * 100, 2)}%")