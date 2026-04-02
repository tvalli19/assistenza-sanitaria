import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Assistenza Sanitaria",
    page_icon="🏥",
    layout="wide"
)

@st.cache_data
def load_data():
    assicurazioni = pd.read_csv('assicurazioni.csv')
    prestazioni = pd.read_csv('prestazioni.csv')
    coperture = pd.read_csv('coperture.csv')
    return assicurazioni, prestazioni, coperture

assicurazioni, prestazioni, coperture = load_data()

# Inizializza session state
if 'assicurazione' not in st.session_state:
    st.session_state.assicurazione = None

# PAGINA 1: Selezione Assicurazione
if st.session_state.assicurazione is None:
    st.title("🏥 Quale assicurazione sanitaria hai?")
    st.markdown("Scopri cosa è coperto e come ottenere il rimborso")
    st.divider()
    
    nome_col = assicurazioni.columns[0]
    
    cols = st.columns(min(3, len(assicurazioni)))
    for idx, row in assicurazioni.iterrows():
        with cols[idx % 3]:
            nome_assic = str(row[nome_col]).strip()
            st.markdown(f"### {nome_assic}")
            
            if len(assicurazioni.columns) >
