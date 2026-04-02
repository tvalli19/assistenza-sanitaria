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
            suffixes=('_cov', '_prest')
        )
    
    # Barra ricerca
    search = st.text_input(
        "🔍 Cerca prestazione",
        placeholder="es: pulizia denti, visita cardiologica, risonanza..."
    )
    
    # Filtra per ricerca
    df_filtered = df.copy()
    if search:
        mask = pd.Series([False] * len(df))
        search_cols = ['Nome Tecnico', 'Sinonimi', 'Keywords Ricerca', prest_id_col]
        for col in search_cols:
            if col in df.columns:
                mask = mask | df[col].astype(str).str.contains(search, case=False, na=False)
        df_filtered = df[mask]
    
    st.markdown(f"##### {len(df_filtered)} prestazioni trovate")
    st.divider()
    
    if len(df_filtered) == 0:
        st.info("Nessuna prestazione trovata. Prova altri termini di ricerca.")
    else:
        # Mostra prestazioni
        for idx, row in df_filtered.head(20).iterrows():
            # Titolo
            nome = row.get('Nome Tecnico', row.get(prest_id_col, f"Prestazione {idx}"))
            emoji = row.get('Icon Emoji', '📋')
            massimale = row.get('Massimale_EUR', 0)
            
            with st.expander(f"{emoji} {nome} · €{massimale:.0f}"):
                # Descrizione
                if 'Descrizione Semplice' in row:
                    desc = row['Descrizione Semplice']
                    if pd.notna(desc):
                        st.markdown(desc)
                        st.divider()
                
                # Metriche
                c1, c2, c3 = st.columns(3)
                c1.metric("Massimale", f"€{row.get('Massimale_EUR', 0):.0f}")
                c2.metric("Compartecipazione", f"{row.get('Compartecipazione_Perc', 0)}%")
                c3.metric("Rimborso", f"€{row.get('Rimborso_Teorico_EUR', 0):.0f}")
                
                st.divider()
                
                # Regole
                freq = row.get('Descrizione_Frequenza')
                if pd.notna(freq):
                    st.markdown("### 📜 Regole")
                    st.info(freq)
                
                # Alert
                c1, c2 = st.columns(2)
                with c1:
                    if row.get('Pre_Autorizzazione'):
                        st.warning("⚠️ Pre-autorizzazione")
                with c2:
                    if row.get('Prescrizione_Obbligatoria'):
                        st.warning("📋 Prescrizione necessaria")
                
                # Documenti
                docs = row.get('Documenti_Dopo')
                if pd.notna(docs):
                    st.markdown("### 📄 Documenti")
                    st.text_area(
                        "Dopo prestazione",
                        docs,
                        height=150,
                        disabled=True,
                        label_visibility="collapsed",
                        key=f"doc_{idx}"
                    )
                
                # Alert importanti
                alert = row.get('Alert_Importanti')
                if pd.notna(alert):
                    st.markdown("### ⚠️ Attenzione")
                    st.warning(alert)
                
                # Note
                note = row.get('Note_Speciali')
                if pd.notna(note):
                    st.markdown("### 📝 Note")
                    st.info(note)

st.divider()
st.caption("Tool informativo · Dati aggiornati 2026")
