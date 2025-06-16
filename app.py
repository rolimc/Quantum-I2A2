import streamlit as st
import zipfile
import os
import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_experimental.agents import create_pandas_dataframe_agent

# Configuração da página
st.set_page_config(page_title="Agente CSV Zipado", layout="wide")
st.title("📦🔍 Pergunte aos seus dados CSV")

# Upload do arquivo ZIP
uploaded_file = st.file_uploader("Faça upload de um arquivo .zip com CSVs", type="zip")

if uploaded_file:
    # Salva o arquivo ZIP temporariamente
    zip_path = "temp.zip"
    with open(zip_path, "wb") as f:
        f.write(uploaded_file.read())

    # Extrai o conteúdo
    extract_dir = "csvs_extraidos"
    os.makedirs(extract_dir, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_dir)

    # Lista os arquivos CSV extraídos
    arquivos = [f for f in os.listdir(extract_dir) if f.endswith(".csv")]

    if arquivos:
        st.success(f"{len(arquivos)} arquivos CSV extraídos:")
        st.write(arquivos)

        # Seleciona um dos arquivos CSV
        csv_escolhido = st.selectbox("Selecione um arquivo para análise:", arquivos)

        if csv_escolhido:
            df = pd.read_csv(os.path.join(extract_dir, csv_escolhido))
            st.dataframe(df.head())

            # Entrada da pergunta
            pergunta = st.text_input("❓ Faça uma pergunta sobre os dados:", placeholder="Ex: Qual a média das notas?")

            if pergunta:
                with st.spinner("Consultando os dados..."):
                    llm = ChatOpenAI(
                        model="gpt-3.5-turbo",
                        temperature=0,
                        openai_api_key=os.getenv("OPENAI_API_KEY")  # 🔑 Segura e compatível com Streamlit Cloud
                    )
                    agente = create_pandas_dataframe_agent(
                        llm,
                        df,
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


