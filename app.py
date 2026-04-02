import streamlit as st
import pandas as pd

st.title("🔍 Debug Colonne CSV")

# Carica e mostra colonne
assicurazioni = pd.read_csv('Assicurazioni.csv')
prestazioni = pd.read_csv('Prestazioni.csv')
coperture = pd.read_csv('Coperture.csv')

st.write("### Assicurazioni.csv")
st.write("**Colonne:**", list(assicurazioni.columns))
st.dataframe(assicurazioni.head())

st.write("### Prestazioni.csv")
st.write("**Colonne:**", list(prestazioni.columns))
st.dataframe(prestazioni.head())

st.write("### Coperture.csv")
st.write("**Colonne:**", list(coperture.columns))
st.dataframe(coperture.head())
