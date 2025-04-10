from flask import Flask, request, jsonify
import asyncio
from ai_agents import PappersAgent, InfogreffeAgent, SocieteAgent, TranslatorAgent, GoogleAgent
from config import openai_model, browser_config
from browser_use import Browser
import time
import uuid
import threading
import concurrent.futures
import functools

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


async def scrape_and_compile(llm_model, browser, company_id: str, id_type: str, request_id: str, cancel_event=None):
    """
    Scrape data from different sources and compile the results.
    Checks for cancellation during execution.
    """
    # Create agents for scraping with the cancellation event
    agents = create_agents(
        llm_model, browser, company_id, id_type, cancel_event)

    # Create a compiler agent to compile results
    translator_agent = TranslatorAgent()

    results = []
    for agent in agents:
        # Check cancellation event
        if cancel_event and cancel_event.is_set():
            print(
                f"Request {request_id} was cancelled via event - stopping scraping")
            return "Scraping was cancelled by user"

        # Also check the old cancellation mechanism for backward compatibility
        if request_id in active_requests and active_requests[request_id]['cancelled']:
            print(
                f"Request {request_id} was cancelled via flag - stopping scraping")
            return "Scraping was cancelled by user"

        try:
            # Run each agent and collect the results
            result = await agent.run()
            if result is not None:  # Add this check
                results.append(result)
            else:
                print(
                    f"Warning: Agent {agent.__class__.__name__} returned None")
        except Exception as e:
            print(f"Error in agent {agent.__class__.__name__}: {str(e)}")

    # Check cancellation again
    if cancel_event and cancel_event.is_set():
        print(
            f"Request {request_id} was cancelled via event - stopping compilation")
        return "Scraping was cancelled by user"

    if request_id in active_requests and active_requests[request_id]['cancelled']:
        print(
            f"Request {request_id} was cancelled via flag - stopping compilation")
        return "Scraping was cancelled by user"

    # Make sure we have at least one result
    if not results:
        return "No results found from any of the scraping agents."

    try:
        compiled_result = await translator_agent.run(results[0])
        # Fix encoding issues
        if isinstance(compiled_result, str):
            # Try to fix common encoding issues
            try:
                # First approach: If the text was accidentally double-encoded
                compiled_result = compiled_result.encode(
                    'latin1').decode('utf-8')
            except (UnicodeError, UnicodeDecodeError):
                pass  # Keep original if approaches fail

        return compiled_result or "No data could be compiled."
    except Exception as e:
        return f"Error compiling results: {str(e)}"


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
    Endpoint to get company data based on company_id and id_type.
    """
    # Get the company_id and id_type from the request
    company_id = request.form.get('company_id')
    id_type = request.form.get('id_type')

    if not company_id or not id_type:
        return jsonify({"error": "Missing company_id or id_type"}), 400

    # Generate a unique ID for this request
    request_id = str(uuid.uuid4())

    try:
        # Create a cancellation event
        cancel_event = threading.Event()

        # Create a future for the scraping task
        future = executor.submit(
            run_scraper_task,
            llm_model,
            browser_config,
            company_id,
            id_type,
            request_id,
            cancel_event
        )

        # Register the request with its future and cancellation event
        active_requests[request_id] = {
            'cancelled': False,
            'start_time': time.time(),
            'company_id': company_id,
            'id_type': id_type,
            'future': future,
            'cancel_event': cancel_event
        }

        # Create a response immediately with the request ID
        response = jsonify({
            "message": "Scraping task started",
            "request_id": request_id,
            "status": "processing"
        })
        response.headers['X-Request-ID'] = request_id
        return response

    except Exception as e:
        return jsonify({"error": str(e)}), 500


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
