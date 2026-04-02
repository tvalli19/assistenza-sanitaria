import streamlit as st
import pandas as pd

st.set_page_config(page_title="Assistenza Sanitaria", page_icon="🏥", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv('assicurazioni.csv'), pd.read_csv('prestazioni.csv'), pd.read_csv('coperture.csv')

assicurazioni, prestazioni, coperture = load_data()

if 'assicurazione' not in st.session_state:
    st.session_state.assicurazione = None

if st.session_state.assicurazione is None:
    st.title("🏥 Quale assicurazione sanitaria hai?")
    st.divider()
    
    cols = st.columns(3)
    for idx, row in assicurazioni.iterrows():
        with cols[idx % 3]:
            st.markdown(f"### {row['nome']}")
            if st.button("Seleziona", key=idx):
                st.session_state.assicurazione = row['nome']
                st.rerun()
else:
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title("Di cosa hai bisogno?")
    with col2:
        if st.button("← Cambia"):
            st.session_state.assicurazione = None
            st.rerun()
    
    st.divider()
    
    df_cov = coperture[coperture['assicurazione'].str.upper() == st.session_state.assicurazione.upper()].copy()
    df = df_cov.merge(prestazioni, left_on='nome_record', right_on='id', how='left')
    
    search = st.text_input("🔍 Cerca", placeholder="es: pulizia denti")
    
    if search:
        mask = (
            df['nome_tecnico'].str.contains(search, case=False, na=False) |
            df['sinonimi'].str.contains(search, case=False, na=False)
        )
        df = df[mask]
    
    st.write(f"**{len(df)} prestazioni**")
    
    for idx, row in df.head(30).iterrows():
        massimale = float(str(row['massimale']).replace('€','').replace(',','.'))
        with st.expander(f"{row['nome_tecnico']} · €{massimale:.0f}"):
            st.write(row['descrizione_semplice'])
            c1,c2,c3 = st.columns(3)
            c1.metric("Massimale", f"€{massimale:.0f}")
            c2.metric("Compartecipazione", f"{row['compartecipazione']}%")
            c3.metric("Rimborso", f"€{massimale * (1-row['compartecipazione']/100):.0f}")
