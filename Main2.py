import streamlit as st
import pandas as pd
import requests
import json
import base64
from io import StringIO

# GitHub repo and file information
GITHUB_REPO = "Lefaun/submitform"
GITHUB_FILE_PATH = "ideas.csv"

# Access the GitHub token from secrets
GITHUB_ACCESS_TOKEN = st.secrets["general"]["GITHUB_ACCESS_TOKEN"]

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

# Other functions remain the same...

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

        # Function to get the SHA of the file (previously defined)
        sha = get_file_sha(GITHUB_REPO, GITHUB_FILE_PATH, GITHUB_ACCESS_TOKEN)
        if sha:
            update_csv_on_github(GITHUB_REPO, GITHUB_FILE_PATH, GITHUB_ACCESS_TOKEN, csv_content, sha)
    else:
        st.error("Please fill out both fields before submitting.")

# Display submitted ideas
st.subheader("Submitted Ideas:")
for i, row in df_ideas.iterrows():
    st.write(f"{i + 1}. **{row['Name']}**: {row['Idea']}")
