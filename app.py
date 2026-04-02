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
    df = coperture_temp[coperture_temp['_clean'] == st.session_state.assicurazione.strip().upper()].copy()
    
    # Merge con prestazioni usando "Nome Record" come ID
    if 'Nome Record' in df.columns and 'ID' in prestazioni.columns:
        df = df.merge(
            prestazioni,
            left_on='Nome Record',
            right_on='ID',
            how='left',
            suffixes=('', '_prest')
        )
        st.success(f"✅ {len(df)} prestazioni caricate con dettagli completi")
    else:
        st.info(f"📋 {len(df)} prestazioni (solo dati copertura)")
    
    # Barra ricerca
    search = st.text_input(
        "🔍 Cerca prestazione",
        placeholder="es: pulizia denti, visita cardiologica, risonanza..."
    )
    
    # Filtra per ricerca
    df_filtered = df.copy()
    if search:
        mask = pd.Series([False] * len(df))
        search_cols = ['Nome Record', 'Nome Tecnico', 'Sinonimi', 'Keywords Ricerca', 'Categoria']
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
        for idx, row in df_filtered.head(40).iterrows():
            # Titolo
            nome = row.get('Nome Tecnico', row.get('Nome Record', f"Prestazione #{idx}"))
            emoji = row.get('Icon Emoji', '📋')
            
            # Massimale (può essere in diverse colonne)
            massimale = row.get('Massimale', row.get('Massimale_EUR', 0))
            if pd.notna(massimale):
                # Rimuovi simbolo € se presente
                if isinstance(massimale, str):
                    massimale = massimale.replace('€', '').replace(',', '.').strip()
                massimale = float(massimale)
            else:
                massimale = 0
            
            with st.expander(f"{emoji} {nome} · €{massimale:.0f}"):
                # Descrizione
                desc = row.get('Descrizione Semplice')
                if pd.notna(desc):
                    st.markdown(desc)
                    st.divider()
                
                # Metriche
                c1, c2, c3 = st.columns(3)
                
                compartec = row.get('Compartecipazione', row.get('Compartecipazione_Perc', 0))
                if pd.notna(compartec):
                    compartec = float(compartec) if compartec != 'nan' else 0
                else:
                    compartec = 0
                
                rimborso = massimale * (1 - compartec/100) if massimale > 0 else 0
                
                c1.metric("Massimale", f"€{massimale:.0f}")
                c2.metric("Compartecipazione", f"{compartec:.0f}%")
                c3.metric("Rimborso teorico", f"€{rimborso:.0f}")
                
                # Coperta
                if row.get('Coperta') == 'checked':
                    st.success("✅ Prestazione coperta")
                
                st.divider()
                
                # Frequenza
                freq_max = row.get('Frequenza Max')
                if pd.notna(freq_max):
                    st.markdown("### 📜 Regole di Rimborso")
                    freq_desc = row.get('Descrizione_Frequenza', f"Massimo {freq_max} volte per anno")
                    st.info(freq_desc)
                
                # Alert prescrizione
                c1, c2 = st.columns(2)
                with c1:
                    if row.get('Pre_Autorizzazione') or row.get('Pre Autorizzazione'):
                        st.warning("⚠️ Pre-autorizzazione necessaria")
                    else:
                        st.success("✓ Senza pre-autorizzazione")
                
                with c2:
                    if row.get('Prescrizione_Obbligatoria') or row.get('Prescrizione Obbligatoria'):
                        st.warning("📋 Prescrizione obbligatoria")
                    else:
                        st.success("✓ Prescrizione non necessaria")
                
                st.divider()
                
                # Documenti
                docs = row.get('Documenti_Dopo') or row.get('Documenti Dopo')
                if pd.notna(docs):
                    st.markdown("### 📄 Documenti per Rimborso")
                    st.text_area("", docs, height=150, disabled=True, label_visibility="collapsed", key=f"doc_{idx}")
                
                # Alert
                alert = row.get('Alert_Importanti') or row.get('Alert Importanti')
                if pd.notna(alert):
                    st.markdown("### ⚠️ Attenzione")
                    st.warning(alert)
                
                # Note
                note = row.get('Note_Speciali') or row.get('Note Speciali')
                if pd.notna(note):
                    st.markdown("### 📝 Note Speciali")
                    st.info(note)

st.divider()
st.caption("🏥 Tool Assistenza Sanitaria · Dati aggiornati 2026")
