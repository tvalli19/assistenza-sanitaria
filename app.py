import streamlit as st
import pandas as pd

st.set_page_config(page_title="Assistenza Sanitaria", page_icon="🏥", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv('assicurazioni.csv'), pd.read_csv('prestazioni.csv'), pd.read_csv('coperture.csv')

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
    
    # Trova colonna Assicurazione
    assic_col = [c for c in coperture.columns if 'assicuraz' in c.lower()][0]
    
    # Filtro
    coperture_temp = coperture.copy()
    coperture_temp['_clean'] = coperture_temp[assic_col].astype(str).str.strip().str.upper()
    df = coperture_temp[coperture_temp['_clean'] == st.session_state.assicurazione.strip().upper()]
    
    # MOSTRA TUTTE LE PRESTAZIONI (senza search per ora)
    st.markdown(f"##### {len(df)} prestazioni disponibili")
    st.info("📌 Search temporaneamente disabilitata - mostro tutte le prestazioni")
    st.divider()
    
    # Mostra
    for idx, row in df.head(30).iterrows():
        prest_id = None
        for col in df.columns:
            if 'prestazion' in col.lower() and 'id' in col.lower():
                prest_id = row[col]
                break
        
        massimale = row.get('Massimale_EUR', 0)
        nome = prest_id if prest_id else f"Prestazione #{idx}"
        
        with st.expander(f"📋 {nome} · €{massimale:.0f}"):
            # Metriche
            c1, c2, c3 = st.columns(3)
            c1.metric("Massimale", f"€{massimale:.0f}")
            c2.metric("Compartecipazione", f"{row.get('Compartecipazione_Perc', 0)}%")
            c3.metric("Rimborso", f"€{row.get('Rimborso_Teorico_EUR', 0):.0f}")
            
            st.divider()
            
            # Frequenza
            if pd.notna(row.get('Descrizione_Frequenza')):
                st.markdown("### 📜 Regole")
                st.info(row['Descrizione_Frequenza'])
            
            # Documenti
            if pd.notna(row.get('Documenti_Dopo')):
                st.markdown("### 📄 Documenti")
                st.text_area("Dopo prestazione", row['Documenti_Dopo'], height=150, disabled=True, label_visibility="collapsed", key=f"d_{idx}")
            
            # Alert
            if pd.notna(row.get('Alert_Importanti')):
                st.markdown("### ⚠️ Attenzione")
                st.warning(row['Alert_Importanti'])
            
            # Debug
            with st.expander("🔧 Tutti i dati"):
                for col in df.columns:
                    if pd.notna(row[col]):
                        st.write(f"**{col}:** {row[col]}")

st.caption("Tool informativo · v1.0")
