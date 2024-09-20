import streamlit as st
import pandas as pd
import requests
import base64
from io import StringIO

# Informações do repositório e do arquivo
GITHUB_REPO = "Lefaun/submitform"
GITHUB_FILE_PATH = "ideas.csv"

# Acesso ao token do GitHub a partir do arquivo de segredos
GITHUB_ACCESS_TOKEN = st.secrets["general"]["GITHUB_ACCESS_TOKEN"]

# Função para carregar o arquivo CSV do GitHub
def load_csv(url):
    headers = {
        "Authorization": f"token {GITHUB_ACCESS_TOKEN}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = StringIO(response.text)
        df = pd.read_csv(data)
        return df
    else:
        st.error(f"Falha ao carregar dados do GitHub. Código de Status: {response.status_code}")
        return pd.DataFrame(columns=["Name", "Idea"])

# Função para obter o SHA do arquivo
def get_file_sha(repo, path, token):
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    headers = {"Authorization": f"token {token}"}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        file_info = response.json()
        return file_info['sha']
    else:
        st.error(f"Falha ao buscar SHA do arquivo. Código de Status: {response.status_code}")
        return None

# Função para atualizar o CSV no GitHub
def update_csv_on_github(repo, path, token, content, sha):
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    headers = {
        "Authorization": f"token {token}",
        "Content-Type": "application/json"
    }

    message = "Atualizando CSV com nova submissão de ideia"
    content_encoded = base64.b64encode(content.encode()).decode("utf-8")

    data = {
        "message": message,
        "content": content_encoded,
        "sha": sha
    }

    response = requests.put(url, headers=headers, json=data)

    if response.status_code == 200:
        st.success("Arquivo CSV atualizado com sucesso no GitHub.")
    else:
        st.error(f"Falha ao atualizar o CSV no GitHub: {response.status_code}")
        st.error(response.json())

# URL para carregar o CSV
csv_url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/{GITHUB_FILE_PATH}"
df_ideas = load_csv(csv_url)

# Formulário Streamlit para enviar ideias
st.title("Envie Sua Ideia")
name = st.text_input("Seu Nome:")
idea = st.text_area("Sua Ideia:")

# Manipulação da submissão do formulário
if st.button("Enviar"):
    if name and idea:
        new_row = pd.DataFrame([[name, idea]], columns=["Name", "Idea"])
        df_ideas = pd.concat([df_ideas, new_row], ignore_index=True)

        csv_content = df_ideas.to_csv(index=False)

        sha = get_file_sha(GITHUB_REPO, GITHUB_FILE_PATH, GITHUB_ACCESS_TOKEN)
        if sha:
            update_csv_on_github(GITHUB_REPO, GITHUB_FILE_PATH, GITHUB_ACCESS_TOKEN, csv_content, sha)
    else:
        st.error("Por favor, preencha ambos os campos antes de enviar.")

# Exibir ideias submetidas
st.subheader("Ideias Submetidas:")
for i, row in df_ideas.iterrows():
    st.write(f"{i + 1}. **{row['Name']}**: {row['Idea']}")
