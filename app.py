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

def safe_float(val, default=0):
    """Converte a float in modo sicuro"""
    try:
        if pd.notna(val):
            val_str = str(val).replace('€', '').replace(',', '.').strip()
            if val_str:
                return float(val_str)
    except:
        pass
    return default

# Carica dati
assicurazioni, prestazioni, coperture = load_data()

# Session state
if 'assicurazione' not in st.session_state:
    st.session_state.assicurazione = None

# PAGINA 1: Selezione Assicurazione
if st.session_state.assicurazione is None:
    st.title("🏥 Quale assicurazione sanitaria hai?")
    st.markdown("**Scopri cosa è coperto e come ottenere il rimborso**")
    st.divider()
    
    cols = st.columns(3)
    for idx, row in assicurazioni.iterrows():
        with cols[idx % 3]:
            nome = str(row['nome']).strip()
            st.markdown(f"### {nome}")
            
            if pd.notna(row['destinatari']):
                st.caption(str(row['destinatari'])[:120] + "...")
            
            if st.button("Seleziona →", key=f"sel_{idx}", use_container_width=True):
                st.session_state.assicurazione = nome
                st.rerun()

# PAGINA 2: Ricerca
else:
    col1, col2 = st.columns([5, 1])
    with col1:
        st.title("Di cosa hai bisogno?")
        st.caption(f"Assicurazione: **{st.session_state.assicurazione}**")
    with col2:
        if st.button("← Cambia"):
            st.session_state.assicurazione = None
            st.rerun()
    
    st.divider()
    
    # Filtra coperture per assicurazione (case-insensitive)
    mask_assic = coperture['assicurazione'].str.strip().str.upper() == st.session_state.assicurazione.strip().upper()
    df_coperture = coperture[mask_assic].copy()
    
    if len(df_coperture) == 0:
        st.warning(f"Nessuna copertura per {st.session_state.assicurazione}")
        st.stop()
    
    # Merge con prestazioni usando nome_record = id
    df = df_coperture.merge(
        prestazioni,
        left_on='nome_record',
        right_on='id',
        how='left'
    )
    
    # Search bar
    search = st.text_input(
        "🔍 Cerca prestazione",
        placeholder="es: pulizia denti, visita cardiologica, risonanza..."
    )
    
    # Filtra per search
    df_filtered = df.copy()
    if search:
        search_lower = search.lower()
        mask = (
            df['nome_tecnico'].astype(str).str.lower().str.contains(search_lower, na=False) |
            df['sinonimi'].astype(str).str.lower().str.contains(search_lower, na=False) |
            df['keywords_ricerca'].astype(str).str.lower().str.contains(search_lower, na=False) |
            df['nome_record'].astype(str).str.lower().str.contains(search_lower, na=False)
        )
        df_filtered = df[mask]
    
    st.markdown(f"##### 🔍 {len(df_filtered)} prestazioni trovate")
    st.divider()
    
    if len(df_filtered) == 0:
        st.info("💡 Nessuna prestazione trovata. Prova altri termini.")
    else:
        # Mostra prestazioni
        for idx, row in df_filtered.head(40).iterrows():
            nome = row.get('nome_tecnico', row.get('nome_record', 'Prestazione'))
            categoria = row.get('categoria', '')
            massimale = safe_float(row.get('massimale'))
            
            # Emoji per categoria
            emoji_dict = {
                'Odontoiatria': '🦷',
                'Visite Specialistiche': '👨‍⚕️',
                'Diagnostica': '🔬',
                'Terapie': '💊'
            }
            emoji = emoji_dict.get(categoria, '📋')
            
            with st.expander(f"{emoji} **{nome}** · €{massimale:.0f}"):
                # Descrizione
                desc = row.get('descrizione_semplice')
                if pd.notna(desc):
                    st.markdown(desc)
                    st.divider()
                
                # Metriche
                c1, c2, c3 = st.columns(3)
                compartec = safe_float(row.get('compartecipazione'))
                rimborso = massimale * (1 - compartec/100) if massimale > 0 and compartec > 0 else massimale
                
                c1.metric("💰 Massimale", f"€{massimale:.2f}")
                c2.metric("📊 Compartecipazione", f"{compartec:.1f}%")
                c3.metric("✅ Rimborso teorico", f"€{rimborso:.2f}")
                
                # Coperta
                if row.get('coperta') == 'checked':
                    st.success("✅ Prestazione coperta")
                
                st.divider()
                
                # Frequenza
                freq_max = safe_float(row.get('frequenza_max'), 0)
                if freq_max > 0 and freq_max < 900:
                    st.markdown("### 📜 Limiti di Frequenza")
                    st.info(f"**Massimo {int(freq_max)} {'volta' if freq_max == 1 else 'volte'} per anno**")
                elif freq_max >= 900:
                    st.success("✅ **Nessun limite di frequenza**")
                
                # Sinonimi
                sinonimi = row.get('sinonimi')
                if pd.notna(sinonimi) and len(str(sinonimi)) > 5:
                    with st.expander("💡 Conosciuta anche come:"):
                        sin_list = str(sinonimi).split(',')
                        st.markdown(", ".join([f"`{s.strip()}`" for s in sin_list[:8]]))
                
                # Footer
                st.caption(f"**Categoria:** {categoria}")

st.divider()
st.caption("🏥 Tool Assistenza Sanitaria · v1.0")
