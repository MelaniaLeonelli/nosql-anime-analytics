import pandas as pd

# 1. Carica solo le prime 100.000 righe del file gigante
df_anime = pd.read_csv('anime_cleaned.csv', nrows=100000)
df_users = pd.read_csv('users_cleaned.csv', nrows=100000)
df_lists = pd.read_csv('animelists_cleaned.csv', nrows=100000)

# 2. Salva i nuovi file leggeri (seed data)
df_anime.to_csv('anime_sample.csv', index=False)
df_users.to_csv('users_sample.csv', index=False)
df_lists.to_csv('animelists_sample.csv', index=False)

print("Campionamento completato con successo!")