import streamlit as st
import requests

BACKEND_URL = "http://127.0.0.1:5000"

st.title("Investment Analyst Dashboard")

ticker = st.text_input("Enter stock ticker:")
if st.button("Get Stock Performance"):
    response = requests.get(f"{BACKEND_URL}/stock", params={"ticker": ticker})
    if response.status_code == 200:
        st.json(response.json())
    else:
        st.error("Error fetching stock data")

query = st.text_input("Enter news topic:")
if st.button("Get News"):
    response = requests.get(f"{BACKEND_URL}/news", params={"query": query})
    if response.status_code == 200:
        news_list = response.json()
        for news in news_list:
            st.markdown(f"[{news['title']}]({news['link']})")
    else:
        st.error("Error fetching news")
