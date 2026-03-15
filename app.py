import streamlit as st
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # loads .env file

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)