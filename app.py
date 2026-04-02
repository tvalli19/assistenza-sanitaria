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
    try:
        if pd.notna(val):
            val_str = str(val).replace('€', '').replace(',', '.').strip()
            if val_str:
                return float(val_str)
    except:
        pass
    return default

assicurazioni, prestazioni, coperture = load_data()

if 'assicurazione' not in st.session_state:
    st.session_state.assicurazione = None

# PAGINA 1
if st.session_state.assicurazione is None:
    st.title("🏥 Quale assicurazione sanitaria hai?")
    st.markdown("**Scopri cosa è coperto e come ottenere il rimborso**")
    st.divider()
    
    # Usa prima colonna qualunque sia il nome
    col_nome = assicurazioni.columns[0]
    col_dest = assicurazioni.columns[4] if len(assicurazioni.columns) > 4 else None
    
    cols = st.columns(3)
    for idx, row in assicurazioni.iterrows():
        with cols[idx % 3]:
            nome = str(row[col_nome]).strip()
            st.markdown(f"### {nome}")
            
            if col_dest and pd.notna(row[col_dest]):
                st.caption(str(row[col_dest])[:120] + "...")
            
            if st.button("Seleziona →", key=f"sel_{idx}", use_container_width=True):
                st.session_state.assicurazione = nome
                st.rerun()

# PAGINA 2
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
    
    # Trova colonna assicurazione in coperture
    col_assic = [c for c in coperture.columns if 'assic' in c.lower()][0]
    
    mask = coperture[col_assic].str.strip().str.upper() == st.session_state.assicurazione.strip().upper()
    df_cov = coperture[mask].copy()
    
    if len(df_cov) == 0:
        st.warning(f"Nessuna copertura per {st.session_state.assicurazione}")
        st.stop()
    
    # Trova colonne per merge
    col_record = [c for c in df_cov.columns if 'record' in c.lower()][0]
    col_id_prest = [c for c in prestazioni.columns if c.lower() == 'id'][0]
    
    df = df_cov.merge(prestazioni, left_on=col_record, right_on=col_id_prest, how='left')
    
    search = st.text_input("🔍 Cerca prestazione", placeholder="es: pulizia denti")
    
    df_filtered = df.copy()
    if search:
        search_lower = search.lower()
        mask = pd.Series([False] * len(df))
        
        for col in df.columns:
            if df[col].dtype == 'object':
                mask = mask | df[col].astype(str).str.lower().str.contains(search_lower, na=False)
        
        df_filtered = df[mask]
    
    st.markdown(f"##### 🔍 {len(df_filtered)} prestazioni trovate")
    st.divider()
    
    if len(df_filtered) == 0:
        st.info("💡 Nessuna prestazione trovata.")
    else:
        # Trova colonne dinamicamente
        col_nome_tec = [c for c in df.columns if 'nome' in c.lower() and 'tec' in c.lower()]
        col_nome_tec = col_nome_tec[0] if col_nome_tec else col_record
        
        col_categ = [c for c in df.columns if 'categ' in c.lower()]
        col_categ = col_categ[0] if col_categ else None
        
        col_mass = [c for c in df.columns if 'massim' in c.lower()][0]
        col_comp = [c for c in df.columns if 'compart' in c.lower()][0]
        
        for idx, row in df_filtered.head(40).iterrows():
            nome = str(row[col_nome_tec]) if col_nome_tec else f"Prestazione {idx}"
            categoria = str(row[col_categ]) if col_categ and pd.notna(row[col_categ]) else ""
            massimale = safe_float(row[col_mass])
            
            emoji_dict = {'Odontoiatria': '🦷', 'Visite Specialistiche': '👨‍⚕️', 'Diagnostica': '🔬'}
            emoji = emoji_dict.get(categoria, '📋')
            
            with st.expander(f"{emoji} **{nome}** · €{massimale:.0f}"):
                col_desc = [c for c in df.columns if 'descriz' in c.lower() and 'sempl' in c.lower()]
                if col_desc and pd.notna(row[col_desc[0]]):
                    st.markdown(row[col_desc[0]])
                    st.divider()
                
                c1, c2, c3 = st.columns(3)
                compartec = safe_float(row[col_comp])
                rimborso = massimale * (1 - compartec/100) if massimale > 0 else 0
                
                c1.metric("💰 Massimale", f"€{massimale:.2f}")
                c2.metric("📊 Compartecipazione", f"{compartec:.1f}%")
                c3.metric("✅ Rimborso", f"€{rimborso:.2f}")
                
                col_coperta = [c for c in df.columns if 'copert' in c.lower()]
                if col_coperta and row[col_coperta[0]] == 'checked':
                    st.success("✅ Coperta")
                
                st.caption(f"**Categoria:** {categoria}")

st.caption("🏥 Tool Assistenza Sanitaria")
