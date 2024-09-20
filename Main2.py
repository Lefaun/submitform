import streamlit as st
import pandas as pd
import requests
import os
from io import StringIO
import base64
import json

# GitHub repo and file information
GITHUB_REPO = "Lefaun/submitform"
GITHUB_FILE_PATH = "main/ideas.csv"

#GITHUB_ACCESS_TOKEN = "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"

# Use environment variable or Streamlit secrets for the token
#GITHUB_ACCESS_TOKEN = os.getenv("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")  # For local use
#GITHUB_ACCESS_TOKEN = st.secrets["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"]  # For Streamlit sharing

# Function to load CSV file from GitHub
def load_csv(url):
    response = requests.get(url)
    if response.status_code == 200:
        data = StringIO(response.text)
        df = pd.read_csv(data)
        return df
    else:
        st.error("Failed to load data from GitHub.")
        return pd.DataFrame(columns=["Name", "Idea"])

# Function to get the SHA of the file
def get_file_sha(repo, path, token):
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    headers = {"Authorization": f"token {token}"}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        file_info = response.json()
        return file_info['sha']
    else:
        st.error(f"Failed to fetch file SHA. Status Code: {response.status_code}")
        st.error(f"Response: {response.text}")
        return None

# Function to update CSV on GitHub
def update_csv_on_github(repo, path, token, content, sha):
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    headers = {
        "Authorization": f"token {token}",
        "Content-Type": "application/json"
    }

    message = "Updating CSV with new idea submission"
    content_encoded = base64.b64encode(content.encode()).decode("utf-8")

    data = {
        "message": message,
        "content": content_encoded,
        "sha": sha
    }

    response = requests.put(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        st.success("CSV file updated successfully on GitHub.")
    else:
        st.error(f"Failed to update the CSV on GitHub: {response.status_code}")
        st.error(response.json())

# Load existing ideas from GitHub CSV
csv_url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/{GITHUB_FILE_PATH}"
df_ideas = load_csv(csv_url)

# Streamlit form to submit ideas
st.title("Submit Your Idea")
name = st.text_input("Your Name:")
idea = st.text_area("Your Idea:")

# Handle form submission
if st.button("Submit"):
    if name and idea:
        new_row = pd.DataFrame([[name, idea]], columns=["Name", "Idea"])
        df_ideas = pd.concat([df_ideas, new_row], ignore_index=True)

        csv_content = df_ideas.to_csv(index=False)

        sha = get_file_sha(GITHUB_REPO, GITHUB_FILE_PATH, GITHUB_ACCESS_TOKEN)
        if sha:
            update_csv_on_github(GITHUB_REPO, GITHUB_FILE_PATH, GITHUB_ACCESS_TOKEN, csv_content, sha)
    else:
        st.error("Please fill out both fields before submitting.")

# Display submitted ideas
st.subheader("Submitted Ideas:")
for i, row in df_ideas.iterrows():
    st.write(f"{i + 1}. **{row['Name']}**: {row['Idea']}")
