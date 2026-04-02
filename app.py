import streamlit as st
import pandas as pd

st.set_page_config(page_title="Assistenza Sanitaria", page_icon="🏥", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv('assicurazioni.csv'), pd.read_csv('prestazioni.csv'), pd.read_csv('coperture.csv')

def safe_float(val, default=0):
    """Converte sicuramente a float"""
    try:
        if pd.notna(val) and str(val).strip() not in ['', 'nan', 'NaN']:
            return float(str(val).replace('€', '').replace(',', '.').strip())
    except:
        pass
    return default

assicurazioni, prestazioni, coperture = load_data()

if 'assicurazione' not in st.session_state:
    st.session_state.assicurazione = None

# PAGINA 1
if st.session_state.assicurazione is None:
    st.title("🏥 Quale assicurazione sanitaria hai?")
    st.markdown("Scopri cosa è coperto e come ottenere il rimborso")
    st.divider()
    
    cols = st.columns(min(3, len(assicurazioni)))
    for idx, row in assicurazioni.iterrows():
        with cols[idx % 3]:
            nome = str(row[assicurazioni.columns[0]]).strip()
            st.markdown(f"### {nome}")
            if st.button("Seleziona", key=f"btn_{idx}"):
                st.session_state.assicurazione = nome
                st.rerun()

# PAGINA 2
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
    
    # Filtra
    assic_col = [c for c in coperture.columns if 'assicuraz' in c.lower()][0]
    coperture_temp = coperture.copy()
    coperture_temp['_clean'] = coperture_temp[assic_col].astype(str).str.strip().str.upper()
    df = coperture_temp[coperture_temp['_clean'] == st.session_state.assicurazione.strip().upper()].copy()
    
    # Merge
    if 'Nome Record' in df.columns and 'ID' in prestazioni.columns:
        df = df.merge(prestazioni, left_on='Nome Record', right_on='ID', how='left', suffixes=('', '_prest'))
    
    # Search
    search = st.text_input("🔍 Cerca prestazione", placeholder="es: pulizia denti, visita...")
    
    df_filtered = df.copy()
    if search:
        mask = pd.Series([False] * len(df))
        for col in ['Nome Record', 'Nome Tecnico', 'Sinonimi', 'Keywords Ricerca']:
            if col in df.columns:
                mask = mask | df[col].astype(str).str.contains(search, case=False, na=False)
        df_filtered = df[mask]
    
    st.markdown(f"##### {len(df_filtered)} prestazioni trovate")
    st.divider()
    
    if len(df_filtered) == 0:
        st.info("Nessuna prestazione trovata.")
    else:
        for idx, row in df_filtered.head(40).iterrows():
            nome = row.get('Nome Tecnico', row.get('Nome Record', 'Prestazione'))
            emoji = row.get('Icon Emoji', '📋')
            massimale = safe_float(row.get('Massimale', row.get('Massimale_EUR')))
            
            with st.expander(f"{emoji} {nome} · €{massimale:.0f}"):
                desc = row.get('Descrizione Semplice')
                if pd.notna(desc):
                    st.markdown(desc)
                    st.divider()
                
                # Metriche
                c1, c2, c3 = st.columns(3)
                compartec = safe_float(row.get('Compartecipazione', row.get('Compartecipazione_Perc')))
                rimborso = massimale * (1 - compartec/100) if massimale > 0 else 0
                
                c1.metric("Massimale", f"€{massimale:.0f}")
                c2.metric("Compartecipazione", f"{compartec:.0f}%")
                c3.metric("Rimborso teorico", f"€{rimborso:.0f}")
                
                if row.get('Coperta') == 'checked':
                    st.success("✅ Prestazione coperta")
                
                st.divider()
                
                # Frequenza
                freq_max = row.get('Frequenza Max')
                if pd.notna(freq_max):
                    st.markdown("### 📜 Regole")
                    st.info(row.get('Descrizione_Frequenza', f"Massimo {freq_max} volte"))
                
                # Alert
                c1, c2 = st.columns(2)
                with c1:
                    if row.get('Pre_Autorizzazione') or row.get('Pre Autorizzazione'):
                        st.warning("⚠️ Pre-autorizzazione")
                with c2:
                    if row.get('Prescrizione_Obbligatoria') or row.get('Prescrizione Obbligatoria'):
                        st.warning("📋 Prescrizione obbligatoria")
                
                # Documenti
                docs = row.get('Documenti_Dopo') or row.get('Documenti Dopo')
                if pd.notna(docs):
                    st.markdown("### 📄 Documenti")
                    st.text_area("", docs, height=150, disabled=True, label_visibility="collapsed", key=f"d_{idx}")
                
                # Alert
                alert = row.get('Alert_Importanti') or row.get('Alert Importanti')
                if pd.notna(alert):
                    st.markdown("### ⚠️ Attenzione")
                    st.warning(alert)

st.caption("🏥 Tool Assistenza Sanitaria")
