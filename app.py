import streamlit as st
from dotenv import load_dotenv
import os
import openai

# Load .env
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

st.title("AI Article Summarizer")

# Text input
article = st.text_area("Paste your article here:")

if st.button("Summarize"):
    if article:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"Summarize this article:\n{article}",
            max_tokens=150
        )
        st.subheader("Summary:")
        st.write(response.choices[0].text.strip())
    else:
        st.warning("Please enter an article to summarize.")