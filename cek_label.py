import joblib
import pandas as pd

# Memuat model dan fitur urutan
model = joblib.load("model_saved/model_rf.pkl")
fitur_urutan = joblib.load("model_saved/fitur_urutan.pkl")
scaler = joblib.load("model_saved/scaler.pkl")

print(f"Urutan kelas model (model.classes_): {model.classes_}")

# Tes A: Masukkan data SEMUA GEJALA NOL / RINGAN (Harusnya Tidak ISPA)
data_ringan = {col: [0.0] if col != 'Umur' else [22.0] for col in fitur_urutan}
df_ringan = pd.DataFrame(data_ringan)[fitur_urutan]
scaled_ringan = scaler.transform(df_ringan)
pred_ringan = model.predict(scaled_ringan)[0]
prob_ringan = model.predict_proba(scaled_ringan)[0]

print("\n--- TEST KASUS 1: Gejala Kosong/Ringan ---")
print(f"Hasil model.predict(): {pred_ringan}")
print(f"Probabilitas untuk setiap kelas {model.classes_}: {prob_ringan}")

# Tes B: Masukkan data SEMUA GEJALA MAKSIMAL/PARAH (Harusnya ISPA)
data_berat = {col: [1.0] if col != 'Umur' else [22.0] for col in fitur_urutan}
df_berat = pd.DataFrame(data_berat)[fitur_urutan]
scaled_berat = scaler.transform(df_berat)
pred_berat = model.predict(scaled_berat)[0]
prob_berat = model.predict_proba(scaled_berat)[0]

print("\n--- TEST KASUS 2: Gejala Parah/Penuh ---")
print(f"Hasil model.predict(): {pred_berat}")
print(f"Probabilitas untuk setiap kelas {model.classes_}: {prob_berat}")