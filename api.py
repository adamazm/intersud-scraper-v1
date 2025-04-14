from flask import Flask, request, jsonify
import asyncio
from ai_agents import PappersAgent, InfogreffeAgent, SocieteAgent, WebCompilerAgent, GoogleAgent, EllisphereAgent, EllisphereCompilerAgent
from config import openai_model, browser_config
from utils import get_years_from_ellisphere, get_year_data, get_detailed_report_data
from browser_use import Browser
import time
import uuid
import threading
import concurrent.futures

app = Flask(__name__)

llm_model = openai_model

# Track active requests with thread executors
active_requests = {}
# Thread pool executor for managing scraping tasks
executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)


def create_agents(llm_model, browser, company_id, id_type, cancel_event=None):
    """
    Create a list of agents to scrape data from different sources.
    Pass the cancellation event to each agent.
    """
    # Create agents with cancellation event
    return [
        PappersAgent(llm_model, browser, company_id, id_type, cancel_event),
        InfogreffeAgent(llm_model, browser, company_id, id_type, cancel_event),
        SocieteAgent(llm_model, browser, company_id, id_type, cancel_event),
        # GoogleAgent(llm_model, browser, company_id, id_type, cancel_event),
    ]


async def ellisphere_get_data(company_id, agent, results):

    xml_content = get_year_data(company_id)

    available_reports = get_years_from_ellisphere(xml_content)
    # Do API call for every year present
    for year in available_reports:

        xml_result = get_detailed_report_data(company_id, year)

        compiled_xml = await agent.run(xml_result)
        results.append(compiled_xml)


async def scrape_and_compile(llm_model, browser, company_id: str, id_type: str, request_id: str, cancel_event=None):
    """
    Scrape data from different sources and compile the results.
    Returns separate results for web scraping and Ellisphere API.
    """
    # Create agents for scraping with the cancellation event
    agents = create_agents(
        llm_model, browser, company_id, id_type, cancel_event)

    ellisphere_agent = EllisphereAgent(cancel_event)

    # Create a compiler agent to compile results
    web_compiler_agent = WebCompilerAgent()
    ellisphere_compiler_agent = EllisphereCompilerAgent()

    # Store web scraping results separately
    web_results = []
    ellisphere_results = []

    # Process web scraping agents
    for agent in agents:
        # Check cancellation event
        if cancel_event and cancel_event.is_set():
            print(
                f"Request {request_id} was cancelled via event - stopping scraping")
            return {"web_data": "Scraping was cancelled by user", "ellisphere_data": "Scraping was cancelled by user"}

        # Also check the old cancellation mechanism for backward compatibility
        if request_id in active_requests and active_requests[request_id]['cancelled']:
            print(
                f"Request {request_id} was cancelled via flag - stopping scraping")
            return {"web_data": "Scraping was cancelled by user", "ellisphere_data": "Scraping was cancelled by user"}

        try:
            # Run each agent and collect the results
            result = await agent.run()
            if result is not None:
                web_results.append(result)
            else:
                print(
                    f"Warning: Agent {agent.__class__.__name__} returned None")
        except Exception as e:
            print(f"Error in agent {agent.__class__.__name__}: {str(e)}")

    # Check cancellation again
    if cancel_event and cancel_event.is_set():
        print(
            f"Request {request_id} was cancelled via event - stopping compilation")
        return {"web_data": "Scraping was cancelled by user", "ellisphere_data": "Scraping was cancelled by user"}

    if request_id in active_requests and active_requests[request_id]['cancelled']:
        print(
            f"Request {request_id} was cancelled via flag - stopping compilation")
        return {"web_data": "Scraping was cancelled by user", "ellisphere_data": "Scraping was cancelled by user"}

    # Process Ellisphere data separately
    try:
        # Call the ellisphere agent to get data
        await ellisphere_get_data(company_id, ellisphere_agent, ellisphere_results)
    except Exception as e:
        print(f"Error in ellisphere agent: {str(e)}")

    # Compile results separately
    web_compiled_result = None
    ellisphere_compiled_result = None

    # Compile web scraped data if available
    if web_results:
        try:
            print(f"Web results before compilation: {web_results}")
            web_compiled_result = await web_compiler_agent.run(web_results[0])
            # Fix encoding issues
            if isinstance(web_compiled_result, str):
                try:
                    web_compiled_result = web_compiled_result.encode(
                        'latin1').decode('utf-8')
                except (UnicodeError, UnicodeDecodeError):
                    pass
        except Exception as e:
            print(f"Error compiling web results: {str(e)}")
            web_compiled_result = f"Error compiling web results: {str(e)}"
    else:
        web_compiled_result = "No results found from web scraping agents."

    # Use Ellisphere data directly without translator if available
    if ellisphere_results:
        try:
            print(
                f"Ellisphere results available: {len(ellisphere_results)} items")
            # Combine all Ellisphere results
            ellisphere_compiled_result = "\n\n".join(ellisphere_results)
            # print(ellisphere_compiled_result)
            # ellisphere_compiled_result = await ellisphere_compiler_agent.run(
            #     ellisphere_compiled_result)
            if isinstance(ellisphere_compiled_result, str):
                try:
                    ellisphere_compiled_result = ellisphere_compiled_result.encode(
                        'latin1').decode('utf-8')
                except (UnicodeError, UnicodeDecodeError):
                    pass
        except Exception as e:
            print(f"Error processing ellisphere results: {str(e)}")
            ellisphere_compiled_result = f"Error processing ellisphere results: {str(e)}"
    else:
        ellisphere_compiled_result = "No results found from Ellisphere API."

    # Return both sets of results
    return {
        "web_data": web_compiled_result or "No web data could be compiled.",
        "ellisphere_data": ellisphere_compiled_result or "No Ellisphere data could be compiled."
    }


# Wrapper function to run in thread
def run_scraper_task(llm_model, browser_config, company_id, id_type, request_id, cancel_event=None):
    """
    Function to run in a separate thread that handles the scraping process.
    Monitors the cancellation event.
    """
    browser = None
    try:
        # Check for cancellation before creating the browser
        if cancel_event and cancel_event.is_set():
            return "Scraping was cancelled before browser initialization"

        # Create a browser instance for this thread
        browser = Browser(browser_config)

        # Small delay to allow browser initialization
        for i in range(5):  # 5 seconds in 1-second increments
            if cancel_event and cancel_event.is_set():
                return "Scraping was cancelled during browser initialization"
            time.sleep(1)

        # Run the scraping process with the cancellation event
        result = asyncio.run(scrape_and_compile(
            llm_model, browser, company_id, id_type, request_id, cancel_event))

        return result
    except Exception as e:
        print(f"Error in scraper thread: {str(e)}")
        return f"Error: {str(e)}"
    finally:
        # Close the browser in the finally block to ensure proper cleanup
        if browser:
            try:
                browser.close()
                print(f"Browser closed for request {request_id}")
            except Exception as e:
                print(f"Error closing browser: {str(e)}")


@app.route('/get-company-data', methods=['POST'])
def get_company_data():
    """
    Start a new scraping request for a company.
    Returns a request ID that can be used to check the status and get results.
    """
    # Get parameters from request
    company_id = request.form.get('company_id')
    id_type = request.form.get('id_type', 'SIREN')

    if not company_id:
        return jsonify({"error": "Missing company_id parameter"}), 400

    # Generate a unique request ID
    request_id = str(uuid.uuid4())

    # Create a cancellation event for this task
    cancel_event = threading.Event()

    # Submit the task to the thread pool
    future = executor.submit(
        run_scraper_task,
        llm_model,
        browser_config,
        company_id,
        id_type,
        request_id,
        cancel_event
    )

    # Store request details and future
    active_requests[request_id] = {
        'future': future,
        'start_time': time.time(),
        'company_id': company_id,
        'id_type': id_type,
        'cancelled': False,
        'cancel_event': cancel_event
    }

    # Return the request ID to the client
    return jsonify({
        "message": "Scraping started",
        "request_id": request_id
    })


@app.route('/get-result/<request_id>', methods=['GET'])
def get_result(request_id):
    """
    Check the status of a scraping request and get the result if it's completed.
    """
    if request_id not in active_requests:
        return jsonify({
            "error": "Request not found. It may have completed or never existed."
        }), 404

    request_data = active_requests[request_id]
    future = request_data['future']

    # Check if the task is done
    if future.done():
        try:
            # Get the result
            result = future.result()

            # Clean up
            del active_requests[request_id]

            # Return the result
            if isinstance(result, (list, dict)):
                return jsonify(result)
            else:
                return jsonify({"data": str(result)})

        except Exception as e:
            # Clean up
            del active_requests[request_id]
            return jsonify({"error": str(e)}), 500
    else:
        # Task is still running
        return jsonify({
            "status": "processing",
            "cancelled": request_data['cancelled'],
            "runtime": time.time() - request_data['start_time']
        })


@app.route('/cancel-request', methods=['POST'])
def cancel_request():
    """
    Cancel an in-progress scraping request by setting the cancellation event.
    """
    request_id = request.form.get('request_id')
    if not request_id:
        return jsonify({"error": "Missing request_id parameter"}), 400

    if request_id in active_requests:
        request_data = active_requests[request_id]

        # Set the cancellation event
        if 'cancel_event' in request_data:
            request_data['cancel_event'].set()
            print(f"Cancellation event set for request {request_id}")

        # Mark as cancelled in our tracking dict too (for backward compatibility)
        request_data['cancelled'] = True

        # Try to cancel the future (only works if not started yet)
        future = request_data['future']
        cancel_result = future.cancel()

        if cancel_result:
            message = f"Request {request_id} was cancelled before execution"
        else:
            message = f"Request {request_id} is marked for cancellation and will stop at next checkpoint"

        return jsonify({
            "success": True,
            "message": message
        })

    return jsonify({
        "success": False,
        "message": f"Request {request_id} not found or already completed"
    })


@app.route('/active-requests', methods=['GET'])
def list_active_requests():
    """
    List all active requests (for debugging)
    """
    return jsonify({
        "active_requests": len(active_requests),
        "requests": [{
            "id": req_id,
            "cancelled": details['cancelled'],
            "runtime": time.time() - details['start_time'],
            "company_id": details['company_id'],
            "id_type": details['id_type'],
            "is_done": details['future'].done()
        } for req_id, details in active_requests.items()]
    })


@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint to verify if the server is running.
    """
    return jsonify({"status": "running"})


if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=False)
