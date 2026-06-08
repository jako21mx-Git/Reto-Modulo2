import pandas as pd
import streamlit as st
from google.cloud import firestore
from google.oauth2 import service_account
import json

# CACHE de conexión (solo se crea una vez)
@st.cache_resource
def init_connection():
    credentials = service_account.Credentials.from_service_account_info(
        json.loads(st.secrets["FIREBASE_CREDENTIALS"])
    )
    return firestore.Client(credentials=credentials)


client = init_connection()


# CACHE de datos (se actualiza cada cierto tiempo)
@st.cache_data(ttl=600)
def get_dataframe():
    docs = client.collection("Movies").stream()

    data = []

    for doc in docs:
        movie = doc.to_dict()
        movie["id"] = doc.id
        data.append(movie)

    df = pd.DataFrame(data)

    # eliminar id
    if "id" in df.columns:
        df = df.drop(columns=["id"])

    # reordenar
    df = df[["name", "genre", "director", "company"]]

    return df