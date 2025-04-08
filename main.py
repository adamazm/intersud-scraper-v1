import streamlit as st
from browser_use import Browser
from config import openai_model, browser_config
import requests
import json

# Initialize the browser and scraper
browser = Browser(browser_config)

url = "http://127.0.0.1:5000"

# Title
st.title("Company Data Scraper")

# First Input: Company Identification
company_id = st.text_input("Enter the Company's Identification:")

id_type = st.selectbox(
    "Identification Type:",
    ["Name", "SIREN", "SIRET", "Other"]  # Add more options as needed
)

# If button is clicked
if st.button("Scrape"):

    # Spinner loading animation
    with st.spinner("Scraping in progress..."):
        st.info(
            f"Searching the company info for '{company_id}' using it's {id_type}...")

        # Make a POST request to the Flask API
        response = requests.post(
            f'{url}/get-company-data',
            data={'company_id': company_id, 'id_type': id_type}
        )

        # Parse the JSON response
        try:
            result_json = response.json()
            # Extract just the data part
            if "data" in result_json:
                display_text = result_json["data"]
            else:
                display_text = str(result_json)
        except json.JSONDecodeError:
            # Fallback if response isn't valid JSON
            display_text = response.text

    # Display the result in a text area
    with st.expander("Scraped Data", expanded=True):
        st.text_area("Compiled Info", value=display_text, height=300)
