import joblib
import numpy as np

# Load model Anda (sesuaikan path foldernya jika model ada di dalam folder lain)
try:
    model = joblib.load('model_saved/model_rf.pkl') # atau sesuaikan path file .pkl Anda
except:
    model = joblib.load('model_rf.pkl')

print("--- BERHASIL LOAD MODEL ---")
print("Model Classes:", model.classes_)

# Simulasi input data gejala (misal 16 fitur diisi angka kecil/0)
# Ubah angka 0 di bawah ini sesuai jumlah fitur Anda
dummy_input = np.zeros((1, 16)) 

hasil = model.predict(dummy_input)[0]
probabilitas = model.predict_proba(dummy_input)[0]

print("Hasil Prediksi (0/1):", hasil)
print("Probabilitas Mentah:", probabilitas)