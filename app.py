import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Assistenza Sanitaria",
    page_icon="🏥",
    layout="wide"
)

st.markdown("""
<style>
    .stButton > button {
        width: 100%;
        padding: 20px;
        text-align: left;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    assicurazioni = pd.read_csv('assicurazioni.csv')
    prestazioni = pd.read_csv('prestazioni.csv')
    coperture = pd.read_csv('coperture.csv')
    return assicurazioni, prestazioni, coperture

assicurazioni, prestazioni, coperture = load_data()

if 'assicurazione' not in st.session_state:
    st.session_state.assicurazione = None

if st.session_state.assicurazione is None:
    st.title("🏥 Quale assicurazione sanitaria hai?")
    st.markdown("Scopri cosa è coperto e come ottenere il rimborso")
    st.divider()
    
    cols = st.columns(3)
    for idx, row in assicurazioni.iterrows():
        with cols[idx % 3]:
            st.markdown(f"### {row['Nome']}")
            st.caption(str(row['Destinatari'])[:100] + "...")
            if st.button("Seleziona", key=f"btn_{idx}"):
                st.session_state.assicurazione = row['Nome']
                st.rerun()
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
    
    df = coperture[coperture['Assicurazione'] == st.session_state.assicurazione].merge(
        prestazioni, left_on='Prestazione_ID', right_on='ID', how='left'
    )
    
    search = st.text_input("🔍 Cerca", placeholder="es: pulizia denti, visita...")
    
    if search:
        df = df[
            df['Nome Tecnico'].str.contains(search, case=False, na=False) |
            df['Sinonimi'].str.contains(search, case=False, na=False) |
            df['Keywords Ricerca'].str.contains(search, case=False, na=False)
        ]
    
    st.markdown(f"**{len(df)} prestazioni**")
    
    for _, row in df.iterrows():
        with st.expander(f"{row.get('Icon Emoji', '📋')} {row['Nome Tecnico']} - €{row['Massimale_EUR']:.0f}"):
            st.markdown(row['Descrizione Semplice'])
            st.divider()
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Massimale", f"€{row['Massimale_EUR']:.0f}")
            col2.metric("Compartecipazione", f"{row['Compartecipazione_Perc']}%")
            col3.metric("Rimborso", f"€{row['Rimborso_Teorico_EUR']:.0f}")
            
            st.markdown("### 📜 Regole")
            st.info(row['Descrizione_Frequenza'])
            
            if row['Pre_Autorizzazione']:
                st.warning("⚠️ Pre-autorizzazione necessaria")
            if row['Prescrizione_Obbligatoria']:
                st.warning("📋 Prescrizione obbligatoria")
            
            st.markdown("### 📄 Documenti")
            if pd.notna(row['Documenti_Dopo']):
                st.text_area("Dopo prestazione", row['Documenti_Dopo'], height=150, disabled=True, label_visibility="collapsed")
            
            if pd.notna(row['Alert_Importanti']):
                st.markdown("### ⚠️ Attenzione")
                st.warning(row['Alert_Importanti'])
