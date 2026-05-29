import pandas as pd

df = pd.read_csv('data/dataset_labeled.csv')

# Drop kolom diagnosis (karena sudah jadi label)
df = df.drop(columns=['Diagnosis'])

# Pastikan semua numerik
df = df.apply(pd.to_numeric)

# Drop duplicate
df = df.drop_duplicates()

df.to_csv('data/dataset_clean.csv', index=False)

print("Cleaning selesai!")