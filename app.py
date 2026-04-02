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
        
        # Trova colonna nome
        nome_col = assicurazioni.columns[0]
        
        cols = st.columns(min(3, len(assicurazioni)))
        for idx, row in assicurazioni.iterrows():
            with cols[idx % 3]:
                nome_assic = str(row[nome_col]).strip()
                st.markdown(f"### {nome_assic}")
                
                if len(assicurazioni.columns) > 1:
                    desc_col = assicurazioni.columns[3] if len(assicurazioni.columns) > 3 else assicurazioni.columns[1]
                    if pd.notna(row[desc_col]):
                        st.caption(str(row[desc_col])[:150] + "...")
                
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
        
        # Trova colonna Assicurazione in coperture
        assic_col = None
        for col in coperture.columns:
            if 'assicuraz' in col.lower():
                assic_col = col
                break
        
        if assic_col is None:
            st.error("Colonna Assicurazione non trovata in coperture.csv")
            st.stop()
        
        # FILTRO CASE-INSENSITIVE
        coperture['_assic_upper'] = coperture[assic_col].astype(str).str.strip().str.upper()
        assic_cercata = st.session_state.assicurazione.strip().upper()
        
        df = coperture[coperture['_assic_upper'] == assic_cercata].copy()
        
        if len(df) == 0:
            st.warning(f"Nessuna copertura trovata per {st.session_state.assicurazione}")
            st.info(f"Debug: Cercavo '{assic_cercata}', valori disponibili: {coperture['_assic_upper'].unique().tolist()}")
            st.stop()
        
        # Merge con prestazioni se esiste colonna Prestazione_ID
        prest_id_col = None
        for col in df.columns:
            if 'prestazion' in col.lower() and 'id' in col.lower():
                prest_id_col = col
                break
        
        if prest_id_col and 'ID' in prestazioni.columns:
            df = df.merge(prestazioni, left_on=prest_id_col, right_on='ID', how='left', suffixes=('', '_prest'))
        
        # Barra ricerca
        search = st.text_input("🔍 Cerca prestazione", placeholder="es: pulizia denti, visita cardiologica...")
        
        # Filtra per ricerca
        if search:
            mask = pd.Series([False] * len(df))
            search_cols = ['Nome Tecnico', 'Sinonimi', 'Keywords Ricerca', prest_id_col]
            for col in search_cols:
                if col in df.columns:
                    mask |= df[col].astype(str).str.contains(search, case=False, na=False)
            df = df[mask]
        
        st.markdown(f"##### {len(df)} prestazioni trovate")
        st.divider()
        
        if len(df) == 0:
            st.info("Nessuna prestazione trovata con questi criteri di ricerca.")
        else:
            # Mostra prestazioni
            for idx, row in df.iterrows():
                nome_prest = row.get('Nome Tecnico', row.get(prest_id_col, f"Prestazione #{idx}"))
                emoji = row.get('Icon Emoji', '📋')
                massimale = row.get('Massimale_EUR', 0)
                
                with st.expander(f"{emoji} {nome_prest} · €{massimale:.0f}"):
                    # Descrizione
                    if 'Descrizione Semplice' in row and pd.notna(row['Descrizione Semplice']):
                        st.markdown(row['Descrizione Semplice'])
                        st.divider()
                    
                    # Metriche
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Massimale", f"€{row.get('Massimale_EUR', 0):.0f}")
                    col2.metric("Compartecipazione", f"{row.get('Compartecipazione_Perc', 0)}%")
                    col3.metric("Rimborso teorico", f"€{row.get('Rimborso_Teorico_EUR', 0):.0f}")
                    
                    st.divider()
                    
                    # Regole
                    if 'Descrizione_Frequenza' in row and pd.notna(row['Descrizione_Frequenza']):
                        st.markdown("### 📜 Regole")
                        st.info(row['Descrizione_Frequenza'])
                    
                    # Alert prescrizione
                    col1, col2 = st.columns(2)
                    with col1:
                        if row.get('Pre_Autorizzazione'):
                            st.warning("⚠️ Pre-autorizzazione necessaria")
                    with col2:
                        if row.get('Prescrizione_Obbligatoria'):
                            st.warning("📋 Prescrizione obbligatoria")
                    
                    # Documenti
                    if 'Documenti_Dopo' in row and pd.notna(row['Documenti_Dopo']):
                        st.markdown("### 📄 Documenti per rimborso")
                        st.text_area("Documenti", row['Documenti_Dopo'], height=150, disabled=True, label_visibility="collapsed", key=f"doc_{idx}")
                    
                    # Alert
                    if 'Alert_Importanti' in row and pd.notna(row['Alert_Importanti']):
                        st.markdown("### ⚠️ Attenzione")
                        st.warning(row['Alert_Importanti'])
                    
                    # Note
                    if 'Note_Speciali' in row and pd.notna(row['Note_Speciali']):
                        st.markdown("### 📝 Note")
                        st.info(row['Note_Speciali'])

except Exception as e:
    st.error(f"Errore: {e}")
    import traceback
    st.code(traceback.format_exc())
