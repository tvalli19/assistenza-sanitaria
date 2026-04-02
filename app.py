import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Debug Assistenza Sanitaria",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Debug: Analisi CSV")

# Carica i file
try:
    assicurazioni = pd.read_csv('assicurazioni.csv')
    prestazioni = pd.read_csv('prestazioni.csv')
    coperture = pd.read_csv('coperture.csv')
    
    st.success("✅ Tutti i CSV caricati correttamente!")
    
    # ANALISI ASSICURAZIONI
    st.write("## 📋 Assicurazioni.csv")
    st.write(f"**Numero righe:** {len(assicurazioni)}")
    st.write(f"**Colonne:** {list(assicurazioni.columns)}")
    st.dataframe(assicurazioni)
    
    st.divider()
    
    # ANALISI PRESTAZIONI
    st.write("## 🏥 Prestazioni.csv")
    st.write(f"**Numero righe:** {len(prestazioni)}")
    st.write(f"**Colonne:** {list(prestazioni.columns)}")
    st.dataframe(prestazioni.head(10))
    st.caption(f"Mostrando prime 10 di {len(prestazioni)} righe totali")
    
    st.divider()
    
    # ANALISI COPERTURE (IMPORTANTE!)
    st.write("## 💰 Coperture.csv")
    st.write(f"**Numero righe:** {len(coperture)}")
    st.write(f"**Colonne:** {list(coperture.columns)}")
    st.dataframe(coperture.head(20))
    st.caption(f"Mostrando prime 20 di {len(coperture)} righe totali")
    
    st.divider()
    
    # ANALISI COLONNA ASSICURAZIONE IN COPERTURE
    st.write("## 🎯 Analisi Colonna Assicurazione")
    
    # Trova colonne che contengono "assicuraz"
    assic_cols = [col for col in coperture.columns if 'assicuraz' in col.lower()]
    
    if assic_cols:
        st.write(f"**Colonne trovate con 'assicuraz':** {assic_cols}")
        
        for col in assic_cols:
            st.write(f"### Valori nella colonna `{col}`:")
            valori_unici = coperture[col].value_counts()
            st.write(valori_unici)
            
            st.write("**Esempi di valori:**")
            for val in coperture[col].head(5):
                st.code(f"'{val}' (tipo: {type(val).__name__}, lunghezza: {len(str(val))})")
    else:
        st.warning("⚠️ Nessuna colonna trovata con 'assicuraz' nel nome!")
        st.write("**Tutte le colonne disponibili:**")
        for col in coperture.columns:
            st.write(f"- `{col}`")
    
    st.divider()
    
    # TEST MATCHING
    st.write("## 🧪 Test Matching QUAS")
    
    if assic_cols:
        col_assic = assic_cols[0]
        st.write(f"Usando colonna: `{col_assic}`")
        
        # Prova a filtrare per QUAS
        test_quas = coperture[coperture[col_assic] == 'QUAS']
        st.write(f"**Righe con valore esatto 'QUAS':** {len(test_quas)}")
        
        # Prova varianti
        test_quas_strip = coperture[coperture[col_assic].astype(str).str.strip() == 'QUAS']
        st.write(f"**Righe con 'QUAS' (dopo strip):** {len(test_quas_strip)}")
        
        # Prova contains
        test_quas_contains = coperture[coperture[col_assic].astype(str).str.contains('QUAS', na=False)]
        st.write(f"**Righe che contengono 'QUAS':** {len(test_quas_contains)}")
        
        if len(test_quas_contains) > 0:
            st.success("✅ Trovate coperture QUAS!")
            st.dataframe(test_quas_contains.head(5))

except FileNotFoundError as e:
    st.error(f"❌ File non trovato: {e}")
    st.write("**File nella directory:**")
    import os
    st.write(os.listdir('.'))
    
except Exception as e:
    st.error(f"❌ Errore generico: {e}")
    st.write("**Dettagli:**")
    import traceback
    st.code(traceback.format_exc())
