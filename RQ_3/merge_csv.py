import pandas as pd

# Liste de tes fichiers CSV
fichiers = ["data/IST_MIR.csv", "data/IST_MOZ.csv", "data/IST_OST.csv", "data/IST_WIK.csv"]

# Lecture et fusion (concaténation)
df_merged = pd.concat([pd.read_csv(f) for f in fichiers], ignore_index=True)

# Sauvegarde dans un nouveau CSV
df_merged.to_csv("data/merged_data.csv", index=False)