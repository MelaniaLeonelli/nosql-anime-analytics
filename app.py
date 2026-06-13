import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import os

# 1. Configurazione della pagina dell'applicazione web
st.set_page_config(page_title="NoSQL Anime Analytics", layout="wide", page_icon="deku.png")

st.title("NoSQL Anime Analytics Dashboard")
st.markdown("---")

# 2. Configurazione dell'URL del Backend (il container Docker delle API)
#BACKEND_URL = "http://localhost:8000"
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# 3. Sidebar per il monitoraggio dello stato dell'infrastruttura
st.sidebar.header("🛠️ Infrastruttura")
try:
    # Facciamo un tentativo di chiamata all'endpoint di health check
    api_check = requests.get(f"{BACKEND_URL}/api/health", timeout=2)
    if api_check.status_code == 200:
        st.sidebar.success("🟢 API Backend: ONLINE")
except Exception:
    st.sidebar.error("🔴 API Backend: OFFLINE")
    st.sidebar.warning("Assicurati che i container Docker siano avviati con 'docker-compose up'")

# 4. Creazione dei Tab organizzati per la visualizzazione delle metriche
tab_generi, tab_studios, tab_utenti = st.tabs([
    "📊 Analisi Generi", 
    "🏢 Performance Studi", 
    "🌍 Distribuzione Utenti"
])

# --- TAB 1: ANALISI GENERI ---
with tab_generi:
    st.header("I Generi di Anime più Apprezzati")
    
    try:
        with st.spinner("Caricamento dati da MongoDB..."):
            response = requests.get(f"{BACKEND_URL}/api/stats/genres", timeout=5)
        
        if response.status_code == 200:
            genres_data = response.json()
            df_genres = pd.DataFrame(genres_data)
            
            if not df_genres.empty:
                # Usa i nomi esatti proiettati dal backend
                fig = px.bar(
                    df_genres, 
                    x="genere", 
                    y="total_anime",
                    title="Top 10 Generi (Voto Medio più Alto)",
                    labels={"total_anime": "Totale Anime", "genere": "Genere Anime", "voto_medio": "Voto Medio"},
                    color="voto_medio",
                    color_continuous_scale=px.colors.sequential.Plasma,
                    hover_data=["voto_medio"]
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                with st.expander("🔍 Visualizza i dati tabellari grezzi"):
                    st.dataframe(df_genres, use_container_width=True)
            else:
                st.warning("Il database è vuoto o non ha restituito dati per i generi.")
        else:
            st.error(f"Errore del server API: Codice {response.status_code}")
            
    except Exception as e:
        st.error(f"Impossibile renderizzare il grafico: {str(e)}")

# --- TAB 2: PERFORMANCE STUDI ---
with tab_studios:
    st.header("Classifica degli Studi di Animazione")
    
    try:
        with st.spinner("Recupero dati degli studi..."):
            resp_studios = requests.get(f"{BACKEND_URL}/api/stats/studios", timeout=5)
        
        if resp_studios.status_code == 200:
            df_studios = pd.DataFrame(resp_studios.json())
            
            if not df_studios.empty:
                # Creiamo un Bubble Chart altamente professionale
                fig_studios = px.scatter(
                    df_studios, 
                    x="studio", 
                    y="totale_episodi",
                    size="anime_prodotti", 
                    color="voto_medio_studio",
                    hover_name="studio", 
                    size_max=60,
                    title="Top 5 Studi: Volume di Produzione vs Qualità",
                    labels={
                        "totale_episodi": "Totale Episodi", 
                        "voto_medio_studio": "Voto Medio", 
                        "anime_prodotti": "Anime Prodotti",
                        "studio": "Studio di Animazione"
                    },
                    color_continuous_scale=px.colors.sequential.Viridis
                )
                
                st.plotly_chart(fig_studios, use_container_width=True)
                
                with st.expander("🔍 Visualizza i dati tabellari grezzi"):
                    st.dataframe(df_studios, use_container_width=True)
            else:
                st.warning("Nessun dato trovato per gli studi.")
        else:
            st.error(f"Errore del server API: Codice {resp_studios.status_code}")
            
    except Exception as e:
        st.error(f"Impossibile renderizzare il grafico: {str(e)}")


# --- TAB 3: DISTRIBUZIONE UTENTI ---
with tab_utenti:
    st.header("Geolocalizzazione della Fanbase")
    
    try:
        with st.spinner("Mappatura utenti in corso..."):
            resp_users = requests.get(f"{BACKEND_URL}/api/users/locations", timeout=5)
        
        if resp_users.status_code == 200:
            df_users = pd.DataFrame(resp_users.json())
            
            if not df_users.empty:
                # Creiamo un Donut Chart elegante
                fig_users = px.pie(
                    df_users, 
                    values="utenti_in_location", 
                    names="localita",
                    title="Top 5 Località per Concentrazione Utenti",
                    hole=0.4,  # Questo trasforma la torta in una ciambella
                    hover_data=["score_medio_location"]
                )
                
                fig_users.update_traces(textposition='inside', textinfo='percent+label')
                
                st.plotly_chart(fig_users, use_container_width=True)
                
                with st.expander("🔍 Visualizza i dati tabellari grezzi"):
                    st.dataframe(df_users, use_container_width=True)
            else:
                st.warning("Nessun dato trovato per gli utenti.")
        else:
            st.error(f"Errore del server API: Codice {resp_users.status_code}")
            
    except Exception as e:
        st.error(f"Impossibile renderizzare il grafico: {str(e)}")