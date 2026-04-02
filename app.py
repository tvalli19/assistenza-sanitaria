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
    
    nome_col = assicurazioni.columns[0]
    
    cols = st.columns(3)
    for idx, row in assicurazioni.iterrows():
        with cols[idx % 3]:
            st.markdown(f"### {row[nome_col]}")
            if st.button("Seleziona", key=idx):
                st.session_state.assicurazione = row[nome_col]
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
    
    assic_col = [c for c in coperture.columns if 'assic' in c.lower()][0]
    df_cov = coperture[coperture[assic_col].str.upper() == st.session_state.assicurazione.upper()].copy()
    df = df_cov.merge(prestazioni, left_on='nome_record', right_on='id', how='left')
    
    search = st.text_input("🔍 Cerca", placeholder="es: pulizia")
    
    if search:
        nome_col = [c for c in df.columns if 'nome_tec' in c.lower()][0]
        sin_col = [c for c in df.columns if 'sinon' in c.lower()][0]
        mask = (
            df[nome_col].str.contains(search, case=False, na=False) |
            df[sin_col].str.contains(search, case=False, na=False)
        )
        df = df[mask]
    
    st.write(f"**{len(df)} prestazioni**")
    
    for idx, row in df.head(30).iterrows():
        nome = row[nome_col] if 'nome_col' in locals() else row['nome_record']
        mass_col = [c for c in df.columns if 'massim' in c.lower()][0]
        comp_col = [c for c in df.columns if 'compart' in c.lower()][0]
        
        try:
            massimale = float(str(row[mass_col]).replace('€','').replace(',','.'))
            compartec = float(row[comp_col])
        except:
            massimale = 0
            compartec = 0
        
        with st.expander(f"{nome} · €{massimale:.0f}"):
            desc_col = [c for c in df.columns if 'descriz' in c.lower() and 'sempl' in c.lower()]
            if desc_col and pd.notna(row[desc_col[0]]):
                st.write(row[desc_col[0]])
            
            c1,c2,c3 = st.columns(3)
            c1.metric("Massimale", f"€{massimale:.0f}")
            c2.metric("Compartecipazione", f"{compartec:.0f}%")
            rimb = massimale * (1-compartec/100) if massimale > 0 else 0
            c3.metric("Rimborso", f"€{rimb:.0f}")
