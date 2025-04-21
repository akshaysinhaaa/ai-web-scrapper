import streamlit as st
from scrape import (
    scrape_website, 
    spilt_dom_content, 
    clean_body_content, 
    extract_body_content,
)

st.title('Scrape the web with AI')
url = st.text_input('Enter the URL of the website you want to scrape')

if st.button("Scrape Site"):
    st.write(f"Scraping {url}...")
    result = scrape_website(url)
    

