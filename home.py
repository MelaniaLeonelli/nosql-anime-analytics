import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="NoSQL Anime Home", layout="wide", page_icon="deku.png")

# Custom CSS per la sidebar
st.markdown(
    """
    <style>
        [data-testid="stSidebarNavItems"] a span {
            font-size: 24px !important;
            font-weight: bold !important;
        }
        [data-testid="stSidebarNavItems"] li {
            padding-top: 10px !important;
            padding-bottom: 10px !important;
        }
        .sidebar-spacer {
            margin-top: 150px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Catalogo Esplorativo Anime")
st.markdown("Esplora l'intero catalogo estratto da MyAnimeList, effettua ricerche testuali avanzate e naviga i blocchi di dati.")
st.markdown("---")

BACKEND_URL = "http://localhost:8000"

st.sidebar.markdown('<div class="sidebar-spacer"></div>', unsafe_allow_html=True)
st.sidebar.header("Infrastruttura")
try:
    api_check = requests.get(f"{BACKEND_URL}/api/health", timeout=2)
    if api_check.status_code == 200:
        st.sidebar.success("API Backend: ONLINE")
except Exception:
    st.sidebar.error("API Backend: OFFLINE")

if "current_page" not in st.session_state:
    st.session_state.current_page = 1

col_search, col_sort, col_limit = st.columns([2, 1, 1])

with col_search:
    search_query = st.text_input("Cerca un anime per titolo o trama (Full-Text)...", key="search_input")

with col_sort:
    sort_labels = {"Voto più alto": "score", "Ordine alfabetico": "title"}
    user_choice = st.selectbox("Ordina per:", list(sort_labels.keys()), index=0)
    sort_option = sort_labels[user_choice]

with col_limit:
    limit_option = st.slider("Elementi per pagina:", min_value=10, max_value=50, value=20, step=10)

if "last_query" not in st.session_state or st.session_state.last_query != search_query or st.session_state.last_sort != sort_option or st.session_state.last_limit != limit_option:
    st.session_state.current_page = 1
    st.session_state.last_query = search_query
    st.session_state.last_sort = sort_option
    st.session_state.last_limit = limit_option

try:
    params = {
        "q": search_query if search_query else None,
        "page": st.session_state.current_page,
        "limit": limit_option,
        "sort_by": sort_option
    }
    
    with st.spinner("Recupero record da MongoDB..."):
        response = requests.get(f"{BACKEND_URL}/api/anime/catalog", params=params, timeout=5)
        
    if response.status_code == 200:
        catalog_data = response.json()
        total_anime = catalog_data["total"]
        results = catalog_data["results"]
        
        total_pages = (total_anime // limit_option) + (1 if total_anime % limit_option > 0 else 0)
        if total_pages == 0: total_pages = 1

        st.metric(label="Totale Anime Trovati", value=f"{total_anime:,}")

        if results:
            df_catalog = pd.DataFrame(results)
            available_cols = ["title", "type", "score", "genres", "studio", "episodes", "synopsis"]
            cols_to_show = [c for c in available_cols if c in df_catalog.columns]
            
            st.dataframe(df_catalog[cols_to_show], use_container_width=True, height=500)
            
            st.markdown("---")
            col_prev, col_info, col_next = st.columns([1, 2, 1])
            
            def go_prev():
                st.session_state.current_page -= 1

            def go_next():
                st.session_state.current_page += 1
            
            with col_prev:
                st.button("Precedente", disabled=(st.session_state.current_page == 1), on_click=go_prev)
                    
            with col_info:
                st.markdown(f"<p style='text-align: center;'>Pagina <b>{st.session_state.current_page}</b> di <b>{total_pages}</b></p>", unsafe_allow_html=True)
                
            with col_next:
                st.button("Successiva", disabled=(st.session_state.current_page >= total_pages), on_click=go_next)
        else:
            st.warning("Nessun anime corrisponde ai criteri di ricerca inseriti.")
    else:
        st.error(f"Errore del backend: Codice {response.status_code}")

except Exception as e:
    st.error(f"Errore di connessione o rendering: {str(e)}")