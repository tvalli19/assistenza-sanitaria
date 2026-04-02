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

# Session state
if 'assicurazione' not in st.session_state:
    st.session_state.assicurazione = None

# PAGINA 1: Selezione
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
            
            # Descrizione (terza colonna se esiste)
            if len(assicurazioni.columns) > 2:
                desc = str(row[assicurazioni.columns[2]])
                if desc != 'nan':
                    st.caption(desc[:150] + "...")
            
            if st.button("Seleziona", key=f"btn_{idx}"):
                st.session_state.assicurazione = nome_assic
                st.rerun()

# PAGINA 2: Ricerca
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
    
    # Trova colonna Assicurazione
    assic_col = None
    for col in coperture.columns:
        if 'assicuraz' in col.lower():
            assic_col = col
            break
    
    if not assic_col:
        st.error("Colonna Assicurazione non trovata")
        st.write("Colonne disponibili:", coperture.columns.tolist())
        st.stop()
    
    # Filtro case-insensitive
    coperture_temp = coperture.copy()
    coperture_temp['_assic_clean'] = coperture_temp[assic_col].astype(str).str.strip().str.upper()
    assic_cercata = st.session_state.assicurazione.strip().upper()
    
    df = coperture_temp[coperture_temp['_assic_clean'] == assic_cercata].copy()
    
    if len(df) == 0:
        st.warning(f"Nessuna copertura per {st.session_state.assicurazione}")
        st.stop()
    
    # Trova colonna ID prestazione
    prest_id_col = None
    for col in df.columns:
        if 'prestazion' in col.lower() and 'id' in col.lower():
            prest_id_col = col
            break
    
    # Merge con prestazioni
    if prest_id_col and 'ID' in prestazioni.columns:
        df = df.merge(
            prestazioni,
            left_on=prest_id_col,
            right_on='ID',
            how='left',
            suffixes=
