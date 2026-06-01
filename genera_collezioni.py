import pandas as pd
import numpy as np

print("Caricamento dei file di partenza...")
df_anime = pd.read_csv('anime_sample.csv')
df_lists = pd.read_csv('animelists_sample.csv')

# --- 1. CREAZIONE DELLA COLLEZIONE STUDIOS ---
print("Generazione della collezione Studios...")
# Estraiamo gli studi unici eliminando i valori nulli
studi_unici = df_anime['studio'].dropna().unique()

# Creiamo il DataFrame per gli studi con qualche info di supporto tipica dei DB documentali
df_studios = pd.DataFrame({
    'studio_id': range(1, len(studi_unici) + 1),
    'studio_name': studi_unici,
    'country': 'Japan',  # Dato di default per il miniworld degli anime
    'established_year': np.random.randint(1970, 2015, size=len(studi_unici)) # Anno fittizio per arricchire il documento
})

# --- 2. CREAZIONE DELLA COLLEZIONE REVIEWS ---
print("Generazione della collezione Reviews...")
# Prendiamo le righe della watchlist dove l'utente ha lasciato un voto alto per simulare delle recensioni
df_reviews_base = df_lists[df_lists['my_score'] >= 8].head(15000).copy()

# Aggiungiamo i campi tipici di una recensione richiesti dal professore
testi_recensioni = [
    "Un'opera straordinaria, la caratterizzazione dei personaggi è eccellente.",
    "Grafica mozzafiato e comparto sonoro da brividi. Consigliatissimo!",
    "Trama avvincente dall'inizio alla fine. Uno dei miei preferisti in assoluto.",
    "Un ottimo anime, anche se il finale lascia qualche questione in sospeso.",
    "Stile di animazione unico e ritmo incalzante. Da vedere assolutamente!"
]

# Assegniamo in modo casuale un testo di recensione a ogni riga
np.random.seed(42)
df_reviews_base['review_text'] = np.random.choice(testi_recensioni, size=len(df_reviews_base))
df_reviews_base['review_id'] = range(1, len(df_reviews_base) + 1)

# Teniamo solo le colonne utili per la collezione Reviews
df_reviews = df_reviews_base[['review_id', 'username', 'anime_id', 'my_score', 'review_text']].rename(columns={'my_score': 'score'})

# --- 3. SALVATAGGIO DEI NUOVI FILE ---
print("Salvataggio dei nuovi file in corso...")
df_studios.to_csv('studios_sample.csv', index=False)
df_reviews.to_csv('reviews_sample.csv', index=False)

print(f"Completato! Generati con successo:\n- studios_sample.csv ({len(df_studios)} righe)\n- reviews_sample.csv ({len(df_reviews)} righe)")