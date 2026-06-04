# 1. Immagine ufficiale di Python leggera
FROM python:3.11-slim

# 2. Impostiamo la cartella di lavoro all'interno del container
WORKDIR /app

# 3. Copiamo il file delle dipendenze dentro il container
COPY requirements.txt .

# 4. Installiamo tutte le librerie Python elencate nel file
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiamo tutto il resto del codice del progetto nella cartella /app
COPY . .

# 6. Esponiamo la porta 8000 (quella standard usata da FastAPI/Uvicorn)
EXPOSE 8000

# 7. Comando per avviare il server delle REST API quando il container si accende
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]