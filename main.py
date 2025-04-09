import streamlit as st
from browser_use import Browser
from config import openai_model, browser_config
import requests
import json
import threading
import time
import asyncio
import traceback  # Add this for better error tracing

# Initialize Streamlit page config
st.set_page_config(
    page_title="Company Data Scraper",
    page_icon="🔍",
    layout="wide"
)

# Title
st.title("Company Data Scraper")

# Initialize all session state variables at the top
if 'scraping' not in st.session_state:
    st.session_state['scraping'] = False
if 'cancel' not in st.session_state:
    st.session_state['cancel'] = False
if 'result' not in st.session_state:
    st.session_state['result'] = None
if 'debug_info' not in st.session_state:
    st.session_state['debug_info'] = []
if 'should_rerun' not in st.session_state:
    st.session_state['should_rerun'] = False
if 'api_error' not in st.session_state:
    st.session_state['api_error'] = None

# Functions to manage state


def add_debug_info(info):
    """Add timestamped debug info to session state"""
    timestamp = time.strftime("%H:%M:%S")
    # Make sure debug_info exists before appending
    if 'debug_info' not in st.session_state:
        st.session_state['debug_info'] = []
    st.session_state['debug_info'].append(f"[{timestamp}] {info}")
    # Print to console too for server-side debugging
    print(f"[{timestamp}] {info}")


def start_scraping():
    st.session_state['scraping'] = True
    st.session_state['cancel'] = False
    st.session_state['result'] = None
    st.session_state['debug_info'] = []
    st.session_state['api_error'] = None


def cancel_scraping():
    st.session_state['cancel'] = True
    add_debug_info("Cancellation requested")


# Process any pending rerun request
if st.session_state['should_rerun']:
    st.session_state['should_rerun'] = False

# Debug display for session state
with st.sidebar.expander("Debug Info", expanded=False):
    st.write("Session State:", st.session_state)
    if st.button("Reset Session State"):
        # Reset all state variables
        st.session_state['scraping'] = False
        st.session_state['cancel'] = False
        st.session_state['result'] = None
        st.session_state['debug_info'] = []
        st.session_state['api_error'] = None
        # Mark that we should rerun on next cycle
        st.session_state['should_rerun'] = True

# First Input: Company Identification
company_id = st.text_input("Enter the Company's Identification:")

id_type = st.selectbox(
    "Identification Type:",
    ["Name", "SIREN", "SIRET", "Other"]
)

# Check if API is running
try:
    health_response = requests.get("http://127.0.0.1:5000/health", timeout=2)
    if health_response.status_code == 200:
        st.sidebar.success("✅ API is running")
    else:
        st.sidebar.warning(
            f"⚠️ API returned status {health_response.status_code}")
except Exception as e:
    st.sidebar.error("❌ API is not available. Make sure Flask API is running.")
    add_debug_info(f"API health check failed: {str(e)}")

# Main scraping action button
if st.button("Scrape", key="scrape_button", disabled=st.session_state['scraping']):
    if not company_id:
        st.error("Please enter a company identification")
    else:
        start_scraping()

# Scraping process and result display
if st.session_state['scraping']:
    # Show cancel button
    st.button("Cancel", key="cancel_button", on_click=cancel_scraping)

    # Initialize the API parameters
    url = "http://127.0.0.1:5000"
    timeout = 60*10  # maximum seconds to wait
    response_container = {'response': None, 'error': None}

    # Spinner and info message
    with st.spinner("Scraping in progress..."):
        add_debug_info(f"Starting scrape for '{company_id}' using {id_type}")
        info_container = st.info(
            f"Searching company info for '{company_id}' using {id_type}...")

        try:
            # Define the API call function
            def make_api_call():
                try:
                    add_debug_info("API call started")
                    response_container['response'] = requests.post(
                        f'{url}/get-company-data',
                        data={'company_id': company_id, 'id_type': id_type},
                        timeout=timeout
                    )
                    add_debug_info(
                        f"API call completed with status {response_container['response'].status_code}")
                except Exception as e:
                    error_traceback = traceback.format_exc()
                    add_debug_info(f"API call failed: {str(e)}")
                    add_debug_info(f"Traceback: {error_traceback}")
                    response_container['error'] = str(e)

            # Start API call in a thread
            thread = threading.Thread(target=make_api_call)
            thread.start()
            add_debug_info("API thread started")

            # Wait for thread to complete or for cancel button to be clicked
            start_time = time.time()
            progress_bar = st.progress(0)
            status_text = st.empty()

            while thread.is_alive():
                # Update progress
                elapsed = time.time() - start_time
                progress = min(elapsed / timeout, 1.0)
                progress_bar.progress(progress)
                status_text.text(f"Elapsed time: {int(elapsed)} seconds")

                # Check for cancellation
                if st.session_state['cancel']:
                    add_debug_info("Cancellation detected in wait loop")
                    status_text.text("Canceling...")
                    break

                # Check for timeout
                if elapsed > timeout:
                    add_debug_info("Timeout detected")
                    break

                # Small sleep to prevent UI freeze
                time.sleep(0.2)

            # Clear the progress elements
            progress_bar.empty()
            status_text.empty()
            info_container.empty()

            # Check if there was an error in the thread
            if response_container['error']:
                raise Exception(response_container['error'])

            # Handle the response
            if response_container['response'] is not None and not st.session_state['cancel']:
                response = response_container['response']
                add_debug_info(
                    f"Processing response with status {response.status_code}")

                # Display raw response for debugging
                add_debug_info(f"Raw response text: {response.text[:500]}...")

                if response.status_code != 200:
                    st.error(
                        f"API returned status code {response.status_code}")
                    st.session_state['api_error'] = f"Status code: {response.status_code}, Response: {response.text}"
                    st.session_state['scraping'] = False
                    add_debug_info(
                        f"API error: {response.status_code} - {response.text}")
                else:
                    try:
                        # Try to parse as JSON
                        result_json = response.json()
                        add_debug_info(
                            f"JSON parsed successfully: {str(result_json)[:200]}...")

                        # Extract just the data part
                        if "data" in result_json:
                            st.session_state['result'] = result_json["data"]
                            add_debug_info(
                                f"Found data field: {str(st.session_state['result'])[:200]}...")
                        else:
                            st.session_state['result'] = str(result_json)
                            add_debug_info(f"No data field, using full result")

                    except json.JSONDecodeError as json_err:
                        # Handle non-JSON response
                        add_debug_info(
                            f"Response is not valid JSON: {str(json_err)}")
                        st.session_state['result'] = response.text
                        add_debug_info(
                            f"Using raw text: {response.text[:200]}...")

                    # Mark scraping as complete and display result immediately
                    st.session_state['scraping'] = False
                    add_debug_info("Scraping completed successfully")

                    # Display the result right away
                    st.success("✅ Scraping completed successfully")
                    with st.expander("Scraped Data", expanded=True):
                        st.text_area(
                            "Company Information",
                            value=st.session_state['result'],
                            height=400
                        )

            elif st.session_state['cancel']:
                # Handle cancellation
                st.warning("Scraping was canceled")
                st.session_state['scraping'] = False
                add_debug_info("Scraping canceled by user")

            else:
                # Handle no response case
                st.error("No response received from the API")
                st.session_state['api_error'] = "No response from API"
                st.session_state['scraping'] = False
                add_debug_info("No response received from API call")

        except Exception as e:
            # Handle unexpected errors
            error_msg = str(e)
            error_traceback = traceback.format_exc()
            st.error(f"Error during scraping: {error_msg}")
            add_debug_info(f"Exception: {error_msg}")
            add_debug_info(f"Traceback: {error_traceback}")
            st.session_state['api_error'] = error_msg
            st.session_state['scraping'] = False

# Display API error if any
if st.session_state.get('api_error'):
    # First text_area (when displaying immediate results)
    with st.expander("Scraped Data", expanded=True):
        st.text_area(
            "Company Information",
            value=st.session_state['result'],
            height=400,
            key="result_text_area_immediate"  # Add this unique key
        )

# Second text_area (when displaying previous results)
elif st.session_state['result']:
    # st.success("✅ Scraping completed successfully 2")

    # with st.expander("Scraped Data", expanded=True):
    #     st.text_area(
    #         "Company Information",
    #         value=st.session_state['result'],
    #         height=400,
    #         key="result_text_area_previous"  # Add this unique key
    #     )

    # Button to start a new search
    if st.button("Start New Search"):
        st.session_state['result'] = None

# Display debug info in sidebar
with st.sidebar.expander("Debug Log", expanded=True):
    if 'debug_info' in st.session_state and st.session_state['debug_info']:
        for info in st.session_state['debug_info']:
            st.write(info)
    else:
        st.write("No debug information available")
