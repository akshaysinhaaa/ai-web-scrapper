import streamlit as st

st.title('Scrape the web with AI')
url = st.text_input('Enter the URL of the website you want to scrape')

if st.button("Scrape Site"):
    st.write(f"Scraping {url}...")

