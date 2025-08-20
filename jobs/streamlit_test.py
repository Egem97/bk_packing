import streamlit as st
import pandas as pd
from etl.extraer import transform_onedrive_files

st.title("Hello World")

# Obtener registros
records = transform_onedrive_files()

# Extraer y normalizar processed_data
processed_list = [r["processed_data"] for r in records]
df = pd.json_normalize(processed_list)

# Expandir la subclave 'data' en columnas planas si existe
if "data" in df.columns:
    data_cols = pd.json_normalize(df["data"]).add_prefix("")
    df = pd.concat([df.drop(columns=["data"]), data_cols], axis=1)

#dff = df.groupby(["data.EMPRESA"]).agg({"data.EMPRESA": "count"}).reset_index()
#st.dataframe(dff)

st.dataframe(df)