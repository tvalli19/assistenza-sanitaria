import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Assistenza Sanitaria",
    page_icon="🏥",
    layout="wide"
)

@st.cache_data
def load_data():
    # Carica i CSV e rinomina le colonne per sicurezza
    assicurazioni = pd.read_csv('assicurazioni.csv')
    prestazioni = pd.read_csv('prestazioni.csv')
    coperture = pd.read_csv('coperture.csv')
    
    # Debug: stampa nomi colonne nei logs
    print("Colonne Assicurazioni:", assicurazioni.columns.tolist())
    print("Colonne Prestazioni:", prestazioni.columns.tolist())
    print("Colonne Coperture:", coperture.columns.tolist())
    
    return assicurazioni, prestazioni, coperture

try:
    assicurazioni, prestazioni, coperture = load_data()
    
    # Inizializza session state
    if 'assicurazione' not in st.session_state:
        st.session_state.assicurazione = None
    
    # PAGINA 1: Selezione Assicurazione
    if st.session_state.assicurazione is None:
        st.title("🏥 Quale assicurazione sanitaria hai?")
        st.markdown("Scopri cosa è coperto e come ottenere il rimborso")
        st.divider()
        
        # Mostra assicurazioni (usando prima colonna come nome)
        nome_col = assicurazioni.columns[0]  # Prende prima colonna qualunque sia il nome
        
        cols = st.columns(min(3, len(assicurazioni)))
        for idx, row in assicurazioni.iterrows():
            with cols[idx % 3]:
                nome_assic = row[nome_col]
                st.markdown(f"### {nome_assic}")
                # Mostra descrizione se esiste seconda colonna
                if len(assicurazioni.columns) > 1:
                    desc_col = assicurazioni.columns[1]
                    st.caption(str(row[desc_col])[:100] + "...")
                
                if st.button("Seleziona", key=f"btn_{idx}"):
                    st.session_state.assicurazione = nome_assic
                    st.rerun()
    
    # PAGINA 2: Ricerca Prestazione
    else:
        col1, col2 = st.columns([4, 1])
        with col1:
            st.title("Di cosa hai bisogno?")
            st.caption(f"Assicurazione: {st.session_state.assicurazione}")
        with col2:
            if st.button("← Cambia"):
                st.session_state.assicurazione = None
                st.rerun()
        
        st.divider()
        
        # Trova colonne dinamicamente
        assic_col_coperture = None
        for col in coperture.columns:
            if 'assicuraz' in col.lower():
                assic_col_coperture = col
                break
        
        if assic_col_coperture is None:
            st.error("Colonna Assicurazione non trovata in Coperture.csv")
            st.write("Colonne disponibili:", coperture.columns.tolist())
            st.stop()
        
        # DEBUG: Mostra cosa c'è nel CSV
st.write("### 🔍 DEBUG INFO")
st.write(f"**Cerco assicurazione:** `{st.session_state.assicurazione}`")
st.write(f"**Colonna usata:** `{assic_col_coperture}`")
st.write(f"**Valori unici in colonna:**")
st.write(coperture[assic_col_coperture].unique())
st.divider()

# Filtra per assicurazione
df = coperture[coperture[assic_col_coperture] == st.session_state.assicurazione].copy()

if len(df) == 0:
    st.warning(f"Nessuna copertura trovata per {st.session_state.assicurazione}")
    st.write("**Tutte le coperture nel CSV:**")
    st.dataframe(coperture[[assic_col_coperture]].head(20))
    st.stop()
