import streamlit as st
from scraper import Scraper
from browser_use import Browser
from config import openai_model, browser_config
import requests

# Initialize the browser and scraper
browser = Browser(browser_config)
scraper = Scraper(llm_model=openai_model, browser=browser)

# Title
st.title("Company Data Scraper")

# First Input: Company Identification
company_id = st.text_input("Enter the Company's Identification:")

# Second Input: Identification Type (e.g. Name, SIREN, SIRET, etc.)
id_type = st.text_input("Identification Type:")

# If button is clicked
if st.button("Scrape"):

    # Spinner loading animation
    with st.spinner("Scraping in progress..."):

        # Make a POST request to the Flask API
        response = requests.post(
            'http://127.0.0.1:5001/get-company-data',
            data={'company_id': company_id, 'id_type': id_type}
        )

        # Decode the Unicode escape sequences
        decoded_result = response.text.encode().decode('unicode_escape')

    # Display the result in a text area
    with st.expander("Scraped Data", expanded=True):
        st.text_area("Compiled Info", value=str(decoded_result), height=300)
