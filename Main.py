import streamlit as st
import pandas as pd
import requests
from io import StringIO

# GitHub raw file URL
csv_url = "https://raw.githubusercontent.com/Lefaun/submitform/main/ideas.csv"

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

# Function to save updated CSV (would need to manually upload changes back to GitHub)
def save_csv(df, filename="ideas.csv"):
    df.to_csv(filename, index=False)
    st.info("The CSV file has been updated locally. Please push the changes to GitHub manually.")

# Load ideas from GitHub CSV
df_ideas = load_csv(csv_url)

# Streamlit input form
st.title("Submit Your Idea")
name = st.text_input("Your Name:")
idea = st.text_area("Your Idea:")

# Submit button action
if st.button("Submit"):
    if name and idea:
        # Append new idea to DataFrame
        new_row = pd.DataFrame([[name, idea]], columns=["Name", "Idea"])
        df_ideas = pd.concat([df_ideas, new_row], ignore_index=True)

        # Save updated DataFrame locally (you'd need to push it to GitHub manually)
        save_csv(df_ideas)

        st.success(f"Thank you for your submission, {name}!")
    else:
        st.error("Please fill out both fields before submitting.")

# Display submitted ideas
st.subheader("Submitted Ideas:")
for i, row in df_ideas.iterrows():
    st.write(f"{i + 1}. **{row['Name']}**: {row['Idea']}")
