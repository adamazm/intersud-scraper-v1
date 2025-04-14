import streamlit as st
from browser_use import Browser
from config import openai_model, browser_config
from utils import get_companies
import requests
import json
import threading
import time
import traceback
import uuid

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
if 'request_id' not in st.session_state:
    st.session_state['request_id'] = None
if 'result_status' not in st.session_state:
    st.session_state['result_status'] = None


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
    st.session_state['result_status'] = None
    st.session_state['debug_info'] = []
    st.session_state['api_error'] = None
    st.session_state['request_id'] = None


def cancel_scraping():
    st.session_state['cancel'] = True
    add_debug_info("Cancellation requested")


def start_new_search():
    st.session_state['result'] = None
    st.session_state['result_status'] = None


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
        st.session_state['result_status'] = None
        st.session_state['debug_info'] = []
        st.session_state['api_error'] = None
        st.session_state['request_id'] = None
        # Mark that we should rerun on next cycle
        st.session_state['should_rerun'] = True

# First Input: Company Identification
company_id = st.text_input("Enter the Company's Identification:")

id_type = st.selectbox(
    "Identification Type:",
    ["Name", "SIREN", "SIRET", "Other"]
)

# Create containers for results and errors - these will be populated later
result_container = st.container()
error_container = st.container()

# Check if API is running
try:
    health_response = requests.get("http://127.0.0.1:5000/health", timeout=10)
    if health_response.status_code == 200:
        st.sidebar.success("✅ API is running")
    else:
        st.sidebar.warning(
            f"⚠️ API returned status {health_response.status_code}")
except Exception as e:
    st.sidebar.error("❌ API is not available. Make sure Flask API is running.")
    add_debug_info(f"API health check failed: {str(e)}")


# Handle different company identification types
if id_type == "Name":
    # Company name search flow - requires search and selection
    if 'selected_company' in st.session_state:
        # Show selected company info
        selected_company_name = st.session_state['selected_company'].get(
            'nomcommercial', 'N/A')

        # Add a new search button that will clear the selection
        if st.button("New Search", key="new_search_button"):
            # Clear selected company and any results
            if 'selected_company' in st.session_state:
                del st.session_state['selected_company']
            if 'selected_company_name' in st.session_state:
                del st.session_state['selected_company_name']
            if 'company_results' in st.session_state:
                del st.session_state['company_results']
            if 'result' in st.session_state:
                del st.session_state['result']
            st.rerun()

    else:
        # Original search functionality when no company is selected
        if (st.button("Search", key="search_button") or 'company_results' in st.session_state) and not 'selected_company' in st.session_state:
            if not company_id and 'company_results' not in st.session_state:
                st.error("Please enter a company name")
            else:
                # Store search results in session state if not already there
                if 'company_results' not in st.session_state:
                    st.session_state['company_results'] = get_companies(
                        company_id)

                # Now use the stored results from session state
                company_results = st.session_state['company_results']

                if company_results:
                    st.write("### Search Results")
                    st.write("Click on a company to select it:")

                    # Display each company as a distinct expandable section
                    for idx, company in enumerate(company_results):
                        # Extract company information
                        company_name = company.get('nomcommercial', 'N/A')
                        company_siren = company.get('siren', 'N/A')
                        company_location = company.get('cpville', 'N/A')

                        # Create an expander with the company name as title
                        with st.expander(f"{company_name}", expanded=True):
                            # Display company details in left-aligned format
                            col1, col2 = st.columns([3, 1])

                            with col1:
                                st.write(f"**SIREN:** {company_siren}")
                                st.write(f"**Location:** {company_location}")

                            with col2:
                                # Add a select button
                                if st.button(f"Select", key=f"select_btn_{idx}"):
                                    st.session_state['selected_company'] = company
                                    st.session_state['selected_company_name'] = company_name
                                    # Clear company results to hide the expanders
                                    st.rerun()
                else:
                    st.warning("No results found for the given company name.")
else:
    # Direct ID flow (SIREN, SIRET, Other) - skip search step
    if company_id:
        # Create a direct company entry if not already selected
        if 'selected_company' not in st.session_state or (
            'selected_company' in st.session_state and
            st.session_state['selected_company'].get('direct_id') != company_id
        ):
            # Create a new direct-ID based selection
            st.session_state['selected_company'] = {
                'nomcommercial': f"Company with {id_type}: {company_id}",
                'siren': company_id if id_type == "SIREN" else "",
                'siret': company_id if id_type == "SIRET" else "",
                'cpville': "N/A",
                'direct_id': company_id  # Mark as direct ID entry
            }
            st.session_state['selected_company_name'] = f"Company with {id_type}: {company_id}"

        # Add a button to change the ID
        if st.button("Change ID", key="change_id_button"):
            if 'selected_company' in st.session_state:
                del st.session_state['selected_company']
            if 'selected_company_name' in st.session_state:
                del st.session_state['selected_company_name']
            if 'result' in st.session_state:
                del st.session_state['result']
            st.rerun()
    else:
        st.error(f"Please enter a valid {id_type}")


# Show selected company information
if 'selected_company' in st.session_state:
    selected_company_name = st.session_state['selected_company'].get(
        'nomcommercial', 'N/A')
    selected_company_siren = st.session_state['selected_company'].get(
        'siren', 'N/A')
    selected_company_location = st.session_state['selected_company'].get(
        'cpville', 'N/A')

    # Display full company details for Name search, simplified for direct ID
    st.write("## Selected Company")
    st.write(f"**Name:** {selected_company_name}")

    if id_type == "Name":
        st.write(f"**SIREN:** {selected_company_siren}")
        st.write(f"**Location:** {selected_company_location}")
    elif id_type == "SIREN":
        st.write(f"**SIREN:** {company_id}")
    elif id_type == "SIRET":
        st.write(f"**SIRET:** {company_id}")
    else:
        st.write(f"**{id_type}:** {company_id}")

    # Determine which ID to use for scraping
    scrape_id = selected_company_siren if id_type == "Name" else company_id
    scrape_id_type = "SIREN" if id_type == "Name" else id_type

    # Scrape Action
    if st.button("Scrape", key="scrape_button", disabled=st.session_state['scraping']):
        start_scraping()

    # Scraping process
    if st.session_state['scraping']:
        # Show cancel button
        st.button("Cancel", key="cancel_button", on_click=cancel_scraping)

        # Initialize the API parameters
        url = "http://127.0.0.1:5000"
        timeout = 60*20  # maximum seconds to wait

        # Spinner and info message
        with st.spinner("Scraping in progress..."):
            add_debug_info(
                f"Starting scrape for '{selected_company_name}' using {scrape_id_type}")
            info_container = st.info(
                f"Searching company info for '{selected_company_name}' using {scrape_id_type}...")

            try:
                # If we don't have a request ID yet, start a new request
                if not st.session_state['request_id']:
                    add_debug_info("Starting new API request")
                    start_response = requests.post(
                        f'{url}/get-company-data',
                        data={'company_id': scrape_id,
                              'id_type': scrape_id_type},
                        timeout=5  # Short timeout for initial request
                    )

                    if start_response.status_code == 200:
                        result_json = start_response.json()
                        st.session_state['request_id'] = result_json.get(
                            'request_id')
                        add_debug_info(
                            f"Received request ID: {st.session_state['request_id']}")
                    else:
                        raise Exception(
                            f"Failed to start scraping: {start_response.text}")

                # Now poll for results
                start_time = time.time()
                progress_bar = st.progress(0)
                status_text = st.empty()

                polling = True
                while polling:
                    # Update progress
                    elapsed = time.time() - start_time
                    progress = min(elapsed / timeout, 1.0)
                    progress_bar.progress(progress)
                    status_text.text(f"Elapsed time: {int(elapsed)} seconds")

                    # Check for cancellation
                    if st.session_state['cancel']:
                        add_debug_info("Cancellation requested during polling")

                        # Try to cancel the request
                        try:
                            cancel_response = requests.post(
                                f'{url}/cancel-request',
                                data={
                                    'request_id': st.session_state['request_id']},
                                timeout=5
                            )
                            if cancel_response.status_code == 200:
                                cancel_json = cancel_response.json()
                                add_debug_info(
                                    f"Cancellation response: {cancel_json}")
                                if cancel_json.get('success'):
                                    add_debug_info(
                                        f"Cancellation success: {cancel_json.get('message')}")
                                    st.session_state['result_status'] = "cancelled"
                                else:
                                    add_debug_info(
                                        f"Cancellation failed: {cancel_json.get('message')}")
                            else:
                                add_debug_info(
                                    f"Cancellation request failed: {cancel_response.text}")
                        except Exception as e:
                            add_debug_info(
                                f"Error sending cancellation: {str(e)}")

                        # Mark as cancelled and break the loop
                        st.session_state['scraping'] = False
                        st.session_state['result_status'] = "cancelled"
                        polling = False
                        break

                    # Poll for result
                    try:
                        add_debug_info(
                            f"Polling for result with request ID: {st.session_state['request_id']}")
                        result_response = requests.get(
                            f'{url}/get-result/{st.session_state["request_id"]}',
                            timeout=5
                        )

                        if result_response.status_code == 200:
                            # Task is either still processing or complete with success
                            result_json = result_response.json()
                            add_debug_info(
                                f"Poll response: {str(result_json)[:200]}...")

                            # Check if still processing
                            if result_json.get('status') == 'processing':
                                add_debug_info(
                                    f"Still processing - runtime: {result_json.get('runtime', 0):.1f}s")
                                # Still running, wait before next poll
                                time.sleep(1)
                                continue
                            else:
                                # We have a result!
                                add_debug_info("Received final result")
                                st.session_state['result'] = result_json
                                add_debug_info(
                                    f"Result keys: {str(result_json.keys())}")

                                # Mark as complete
                                st.session_state['scraping'] = False
                                st.session_state['result_status'] = "success"
                                polling = False
                                break

                        elif result_response.status_code == 404:
                            # Request not found
                            add_debug_info(
                                "Request not found, it may have completed or been deleted")
                            st.session_state['api_error'] = "Request not found on server. It may have been deleted or expired."
                            st.session_state['scraping'] = False
                            st.session_state['result_status'] = "error"
                            polling = False
                            break

                        else:
                            # Error occurred
                            error_text = result_response.text
                            add_debug_info(
                                f"Error checking result: {error_text}")
                            st.session_state['api_error'] = f"Error: {error_text}"
                            st.session_state['scraping'] = False
                            st.session_state['result_status'] = "error"
                            polling = False
                            break

                    except Exception as e:
                        add_debug_info(f"Error polling for result: {str(e)}")
                        time.sleep(1)  # Wait before retry

                    # Check for timeout
                    if elapsed > timeout:
                        add_debug_info("Timeout detected")
                        st.session_state['scraping'] = False
                        st.session_state['api_error'] = "Scraping timed out"
                        st.session_state['result_status'] = "timeout"
                        polling = False
                        break

                    # Small sleep to prevent too frequent polling
                    time.sleep(1)

                # Clear progress elements
                progress_bar.empty()
                status_text.empty()
                info_container.empty()

            except Exception as e:
                error_msg = str(e)
                error_traceback = traceback.format_exc()
                add_debug_info(f"Exception: {error_msg}")
                add_debug_info(f"Traceback: {error_traceback}")
                st.session_state['api_error'] = error_msg
                st.session_state['scraping'] = False
                st.session_state['result_status'] = "error"

    # Handle displaying result or errors based on status - RESULT DISPLAY SECTION
    with result_container:
        # Show API errors
        if st.session_state.get('api_error'):
            with st.expander("API Error Details", expanded=True):
                st.error(f"API Error: {st.session_state['api_error']}")
                if st.button("Clear Error"):
                    st.session_state['api_error'] = None
                    st.session_state['result_status'] = None

        # Show result if available
        if st.session_state['result']:
            # Different header based on status
            if st.session_state['result_status'] == "success":
                st.success("✅ Scraping completed successfully")
            elif st.session_state['result_status'] == "cancelled":
                st.warning(
                    "⚠️ Scraping was cancelled but partial results available")
            else:
                st.info("Previously scraped data")

            # Display the results in tabs for better organization
            tab1, tab2 = st.tabs(["Web Data", "Ellisphere Data"])

            # Parse the result
            result_data = st.session_state['result']

            with tab1:
                # Display web scraped data
                st.subheader("Web Scraped Data")
                if isinstance(result_data, dict) and "web_data" in result_data:
                    st.text_area(
                        "Web Sources (Pappers, Infogreffe, Societe.com)",
                        value=result_data["web_data"],
                        height=400,
                        key="web_result_text"
                    )
                else:
                    # Fallback if not in expected format
                    st.text_area(
                        "Web Sources (All Data)",
                        value=str(result_data),
                        height=400,
                        key="fallback_result_text"
                    )
                    st.info("Data format doesn't contain separate web data section")

            with tab2:
                # Display Ellisphere data
                st.subheader("Ellisphere Financial Data")
                if isinstance(result_data, dict) and "ellisphere_data" in result_data:
                    st.text_area(
                        "Ellisphere API Data",
                        value=result_data["ellisphere_data"],
                        height=400,
                        key="ellisphere_result_text"
                    )
                else:
                    st.info("No specific Ellisphere data available")

            # Show buttons for navigation
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Back to Search Results"):
                    if 'selected_company' in st.session_state:
                        del st.session_state['selected_company']
                    if 'selected_company_name' in st.session_state:
                        del st.session_state['selected_company_name']
                    st.rerun()

            with col2:
                if st.button("Clear All & Start New"):
                    if 'selected_company' in st.session_state:
                        del st.session_state['selected_company']
                    if 'selected_company_name' in st.session_state:
                        del st.session_state['selected_company_name']
                    if 'company_results' in st.session_state:
                        del st.session_state['company_results']
                    if 'result' in st.session_state:
                        del st.session_state['result']
                    st.rerun()

    # Display debug info in sidebar
    with st.sidebar.expander("Debug Log", expanded=True):
        if 'debug_info' in st.session_state and st.session_state['debug_info']:
            for info in st.session_state['debug_info']:
                st.write(info)
        else:
            st.write("No debug information available")

    # Show active requests for debugging
    with st.sidebar.expander("Active Requests", expanded=False):
        url = "http://127.0.0.1:5000"  # Define URL here to avoid reference errors
        if st.button("Refresh Active Requests"):
            try:
                active_response = requests.get(
                    f"{url}/active-requests", timeout=2)
                if active_response.status_code == 200:
                    active_data = active_response.json()
                    st.write(
                        f"Active requests: {active_data['active_requests']}")
                    if active_data['active_requests'] > 0:
                        for req in active_data['requests']:
                            st.write(f"ID: {req['id']}")
                            st.write(f"Runtime: {req['runtime']:.1f}s")
                            st.write(f"Cancelled: {req['cancelled']}")
                            st.write(
                                f"Company: {req['company_id']} ({req['id_type']})")
                            st.write(
                                f"Status: {'Done' if req['is_done'] else 'Running'}")
                            st.write("---")
                else:
                    st.write(
                        f"Error retrieving active requests: {active_response.status_code}")
            except Exception as e:
                st.write(f"Error: {str(e)}")
