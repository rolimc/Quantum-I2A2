# app.py

import streamlit as st
import zipfile, os, pandas as pd
from langchain_openai import ChatOpenAI
from langchain_experimental.agents import create_pandas_dataframe_agent

st.set_page_config(page_title="Agente CSV Zipado", layout="wide")
st.title("📦🔍 Pergunte aos seus dados CSV")

uploaded_file = st.file_uploader("Faça upload de um arquivo .zip com CSVs", type="zip")

if uploaded_file:
    zip_path = "temp.zip"
    with open(zip_path, "wb") as f:
        f.write(uploaded_file.read())

    extract_dir = "csvs_extraidos"
    os.makedirs(extract_dir, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_dir)

    arquivos = [f for f in os.listdir(extract_dir) if f.endswith(".csv")]

    if arquivos:
        st.success(f"{len(arquivos)} arquivos CSV extraídos:")
        st.write(arquivos)

        csv_escolhido = st.selectbox("Selecione um arquivo para análise:", arquivos)

        if csv_escolhido:
            df = pd.read_csv(os.path.join(extract_dir, csv_escolhido))
            st.dataframe(df.head())

            pergunta = st.text_input("❓ Faça uma pergunta sobre os dados:", placeholder="Ex: Qual a média das notas?")

            if pergunta:
                with st.spinner("Consultando os dados..."):
                    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
                    agente = create_pandas_dataframe_agent(
                        llm, df,
                        verbose=False,
                        agent_type="openai-tools",
                        allow_dangerous_code=True
                    )
                    resposta = agente.invoke({"input": pergunta})
                st.success("✅ Resposta:")
                st.write(resposta["output"])
    else:
        st.warning("O arquivo ZIP não contém arquivos CSV.")
else:
    st.info("Aguardando o upload de um arquivo ZIP...")

