from fastapi import FastAPI, HTTPException, Request
import uvicorn
import json
import os
import asyncio
import uuid
import threading
from dotenv import load_dotenv
from collections import defaultdict
from enum import Enum
from scraper_agents import ScrapingAgent, EllisphereAgent, OpenAICompiler
from tasks import infogreffe_task, pappers_scrape_task, societe_scrape_task, google_task
from helpers import get_year_data, get_years_from_ellisphere, get_detailed_report_data, get_companies_from_societe_api, parse_periods_from_file, get_available_years_from_file

load_dotenv()

app = FastAPI()

# In-memory storage for task results
task_results = defaultdict(dict)

# Task execution lock
task_lock = threading.Lock()


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


def run_async(coro):
    """Helper function to run async functions"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def update_task_status(task_id, status, data=None, error=None, progress=None, scraper_statuses=None):
    """Thread-safe update of task status"""
    with task_lock:
        if data is not None:
            task_results[task_id].update({
                "status": status,
                "data": data
            })
        elif error is not None:
            task_results[task_id].update({
                "status": status,
                "error": error
            })
        else:
            task_results[task_id]["status"] = status

        if progress is not None:
            task_results[task_id]["progress"] = progress
            
        if scraper_statuses is not None:
            task_results[task_id]["scraper_statuses"] = scraper_statuses


def process_scraper(task_id, company_id, id_type):
    """Process the scraper task"""
    try:
        # Define independent scrapers (run first)
        independent_scrapers = [
            {
                "name": "infogreffe",
                "task_function": infogreffe_task,
                "display_name": "Infogreffe"
            },
            {
                "name": "pappers",
                "task_function": pappers_scrape_task,
                "display_name": "Pappers"
            },
            {
                "name": "societe",
                "task_function": societe_scrape_task,
                "display_name": "Societe"
            },
            {
                "name": "ellisphere",
                "task_function": process_ellisphere,
                "display_name": "Ellisphere"
            }
        ]

        # Define dependent scrapers (run after independent ones)
        dependent_scrapers = [
            {
                "name": "google",
                "task_function": google_task,
                "display_name": "Google",
                # Priority order for input
                "depends_on": ["infogreffe", "pappers", "societe"]
            }
            # Add more dependent scrapers here if needed
        ]

        total_scrapers = len(independent_scrapers) + len(dependent_scrapers)
        independent_progress = 80  # 80% for independent scrapers
        dependent_progress = 20    # 20% for dependent scrapers

        progress_per_independent = independent_progress / \
            len(independent_scrapers)
        progress_per_dependent = dependent_progress / len(dependent_scrapers)

        # Initialize scraper statuses - all start as running
        scraper_statuses = {}
        all_scrapers = independent_scrapers + dependent_scrapers + [{"name": "compiled_report", "display_name": "Compiled Report"}]
        for scraper in all_scrapers:
            scraper_statuses[scraper["name"]] = "running"

        # Update the task status to running with initial scraper statuses
        update_task_status(task_id, TaskStatus.RUNNING.value, progress=0, scraper_statuses=scraper_statuses)

        results = {}

        # Phase 1: Run independent scrapers
        for i, scraper_config in enumerate(independent_scrapers):
            # Update progress at start of each scraper
            current_progress = int(i * progress_per_independent)
            update_task_status(
                task_id, TaskStatus.RUNNING.value, progress=current_progress, scraper_statuses=scraper_statuses)

            # Handle different scraper types with individual error handling
            try:
                if scraper_config["name"] == "ellisphere":
                    # Ellisphere uses async functions, so use run_async helper
                    result = run_async(scraper_config["task_function"](company_id))
                else:
                    # Standard scrapers use ScrapingAgent
                    agent = ScrapingAgent(
                        scraper_config["task_function"](company_id, id_type))
                    result = run_async(agent.scrape(company_id, id_type))

                results[scraper_config["name"]] = result
                # Mark scraper as completed successfully
                scraper_statuses[scraper_config["name"]] = "completed"
            except Exception as e:
                # Log the error but continue with other scrapers
                error_msg = f"Error in {scraper_config['display_name']} scraper: {str(e)}"
                print(f"Warning: {error_msg}")
                results[scraper_config["name"]] = {"error": error_msg, "status": "failed"}
                # Mark scraper as failed
                scraper_statuses[scraper_config["name"]] = "failed"

            # Update progress after completing this scraper
            completed_progress = int((i + 1) * progress_per_independent)
            update_task_status(task_id, TaskStatus.RUNNING.value,
                               progress=completed_progress, scraper_statuses=scraper_statuses)

        # Phase 2: Run dependent scrapers
        for i, scraper_config in enumerate(dependent_scrapers):
            # Update progress at start of each dependent scraper
            current_progress = int(
                independent_progress + (i * progress_per_dependent))
            update_task_status(
                task_id, TaskStatus.RUNNING.value, progress=current_progress, scraper_statuses=scraper_statuses)

            # Get input data from dependency
            input_data = get_dependency_input(
                results, scraper_config.get("depends_on", []))

            if input_data is None:
                # No valid input found, skip this scraper or use fallback
                results[scraper_config["name"]] = None
                scraper_statuses[scraper_config["name"]] = "failed"
                continue

            try:
                # Run dependent scraper with input data
                if scraper_config["name"] == "google":
                    # Google task needs parsed data as input (only one argument)
                    agent = ScrapingAgent(
                        scraper_config["task_function"](input_data))
                    result = run_async(agent.scrape(input_data, id_type))
                else:
                    # Handle other dependent scrapers if added in future
                    agent = ScrapingAgent(
                        scraper_config["task_function"](company_id, id_type))
                    result = run_async(agent.scrape(company_id, id_type))

                results[scraper_config["name"]] = result
                scraper_statuses[scraper_config["name"]] = "completed"
            except Exception as e:
                error_msg = f"Error in {scraper_config['display_name']} scraper: {str(e)}"
                print(f"Warning: {error_msg}")
                results[scraper_config["name"]] = {"error": error_msg, "status": "failed"}
                scraper_statuses[scraper_config["name"]] = "failed"

            # Update progress after completing this scraper
            completed_progress = int(
                independent_progress + ((i + 1) * progress_per_dependent))
            update_task_status(task_id, TaskStatus.RUNNING.value,
                               progress=completed_progress, scraper_statuses=scraper_statuses)

        # Phase 3: Compile all results into human-readable document
        update_task_status(task_id, TaskStatus.RUNNING.value, progress=95, scraper_statuses=scraper_statuses)
        try:
            compiled_document = run_async(compile_results(results))
            results["compiled_report"] = compiled_document
            scraper_statuses["compiled_report"] = "completed"
        except Exception as e:
            error_msg = f"Error in compilation: {str(e)}"
            print(f"Warning: {error_msg}")
            results["compiled_report"] = {"error": error_msg, "status": "failed"}
            scraper_statuses["compiled_report"] = "failed"

        # Ensure final progress is exactly 100%
        update_task_status(task_id, TaskStatus.COMPLETED.value,
                           data=results, progress=100, scraper_statuses=scraper_statuses)

    except Exception as e:
        # Mark all scrapers as failed
        failed_statuses = {}
        all_scrapers = ["infogreffe", "pappers", "societe", "ellisphere", "google", "compiled_report"]
        for scraper in all_scrapers:
            failed_statuses[scraper] = "failed"
        update_task_status(task_id, TaskStatus.FAILED.value,
                           error=str(e), progress=0, scraper_statuses=failed_statuses)


def get_dependency_input(results, dependency_list):
    """
    Get input data from dependency scrapers in priority order.
    Returns the first successful result from the dependency list.
    """
    for dependency_name in dependency_list:
        if dependency_name in results and results[dependency_name]:
            # Check if the result has useful data
            result = results[dependency_name]
            if isinstance(result, str) and result.strip():
                return result
            elif isinstance(result, dict) and result:
                return result
            elif isinstance(result, list) and result:
                return result

    return None  # No valid dependency input found


async def compile_results(results):
    """
    Compile results from multiple scrapers into a human-readable document.
    Excludes ellisphere data and only processes: infogreffe, pappers, societe, google.
    """
    try:
        # List of scrapers to include in compilation (excluding ellisphere)
        included_scrapers = ["infogreffe", "pappers", "societe", "google"]
        
        # Prepare compilation input with results from specified scrapers only
        compilation_input = ""
        processed_count = 0

        # Add results from each included scraper
        for scraper_name, scraper_result in results.items():
            if scraper_name in included_scrapers and scraper_result:
                compilation_input += f"\n=== {scraper_name.title()} Results ===\n"
                compilation_input += str(scraper_result) + "\n"
                processed_count += 1

        # Check if we have any data to compile
        if processed_count == 0:
            return "Aucune donnée disponible pour la compilation. Les scrapers suivants sont pris en charge: " + ", ".join(included_scrapers)

        # Add a note about what was included
        header = f"=== Rapport Compilé ===\n"
        header += f"Sources incluses: {', '.join([name.title() for name in included_scrapers if name in results and results[name]])}\n"
        header += f"Note: Les données Ellisphere sont affichées séparément dans l'onglet 'Résultats'.\n\n"
        
        compilation_input = header + compilation_input

        # Use the compiler agent to create human-readable document
        compiler = OpenAICompiler()
        compiled_document = await compiler.run(compilation_input)

        return compiled_document

    except Exception as e:
        return f"Erreur lors de la compilation: {str(e)}\nNote: Les données Ellisphere sont exclues de la compilation."


async def process_ellisphere(company_id, output_format="json"):
    """Scrape from Ellisphere (XML-based, reading from local file)"""
    try:
        # Get periods data from local file
        periods_response = parse_periods_from_file(company_id)
        if not periods_response['success']:
            error_msg = f"Ellisphere file reading failed: {periods_response['error']}"
            print(f"Warning: {error_msg}")
            return {"error": error_msg, "status": "failed"}
        
        periods_data = periods_response['data']
        ellisphere_agent = EllisphereAgent()
        ellisphere_results = {}

        if not periods_data:
            print("Warning: No Ellisphere periods found in the file")
            return {"error": "No periods available", "status": "no_data"}
        
        # Process each period/year
        for year, period_xml in periods_data.items():
            try:
                print(f"Processing Ellisphere data for year {year}")
                
                # Choose operation type based on output_format
                if output_format == "json":
                    # Use new JSON parsing functionality for structured data
                    compiled_data = await ellisphere_agent.run(period_xml, operation_type="xml_to_json")
                    
                    # Try to parse as JSON to validate and provide better error handling
                    try:
                        import json
                        import re
                        
                        # Clean the response - remove markdown code blocks if present
                        cleaned_data = compiled_data.strip()
                        
                        # Remove markdown code block formatting
                        if cleaned_data.startswith('```json'):
                            # Remove opening ```json and closing ```
                            cleaned_data = re.sub(r'^```json\s*\n?', '', cleaned_data)
                            cleaned_data = re.sub(r'\n?```\s*$', '', cleaned_data)
                        elif cleaned_data.startswith('```'):
                            # Handle generic code blocks
                            cleaned_data = re.sub(r'^```[a-zA-Z]*\s*\n?', '', cleaned_data)
                            cleaned_data = re.sub(r'\n?```\s*$', '', cleaned_data)
                        
                        parsed_json = json.loads(cleaned_data)
                        ellisphere_results[year] = {
                            "format": "json",
                            "data": parsed_json,
                            "status": "success"
                        }
                    except json.JSONDecodeError as json_error:
                        print(f"Warning: JSON parsing failed for year {year}: {json_error}")
                        print(f"Raw data preview: {compiled_data[:200]}...")
                        ellisphere_results[year] = {
                            "format": "raw_text",
                            "data": compiled_data,
                            "status": "json_parse_failed",
                            "error": str(json_error)
                        }
                else:
                    # Use original French text parsing for backward compatibility
                    compiled_data = await ellisphere_agent.parse_xml(period_xml)
                    ellisphere_results[year] = {
                        "format": "french_text",
                        "data": compiled_data,
                        "status": "success"
                    }
                    
            except Exception as e:
                print(f"Warning: Failed to parse data for year {year}: {str(e)}")
                ellisphere_results[year] = {"error": f"Parsing failed: {str(e)}", "status": "failed"}
                continue  # Skip this year instead of failing completely

        if not ellisphere_results:
            return {"error": "Failed to parse any period data", "status": "no_data"}
        
        # Convert dictionary to list format for compatibility with existing frontend
        # Each entry will have year and data
        formatted_results = []
        for year, result in ellisphere_results.items():
            formatted_results.append({
                "year": year,
                "result": result
            })
        
        return formatted_results
    except Exception as e:
        error_msg = f"Ellisphere processing error: {str(e)}"
        print(f"Warning: {error_msg}")
        return {"error": error_msg, "status": "failed"}


@app.get("/get-companies")
async def get_companies(request: Request):
    """
    Get the results from the societe.com API for a given company name.
    """
    try:
        params = request.query_params
        company_name = params.get("company_name")
        print(f"Getting companies for {company_name}")

        # DEBUG:Read from the example JSON file instead of making API call
        # file_path = os.path.join(os.path.dirname(
        #     __file__), "debug", "societe_api_example_results.json")
        # with open(file_path, 'r', encoding='utf-8') as file:
        #     response_data = json.load(file)

        # TODO: Use the societe.com API to get real results
        response_data = get_companies_from_societe_api(company_name)

        return {
            "success": True,
            "data": response_data,
            "message": "Companies retrieved successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/scrape-company")
async def scrape_company(request: Request):
    """
    Scrape the company information from the website.
    """
    params = request.query_params
    company_id = params.get("company_id")
    id_type = params.get("id_type")

    task_id = str(uuid.uuid4())
    with task_lock:
        task_results[task_id] = {'status': TaskStatus.PENDING.value}

    thread = threading.Thread(
        target=process_scraper,
        args=(task_id, company_id, id_type),
        daemon=True
    )
    thread.start()

    return {
        "success": True,
        "data": {
            "task_id": task_id,
            "status": TaskStatus.PENDING.value
        },
        "message": "Scraping task started successfully"
    }


@app.get("/get-task-status/{task_id}")
async def get_task_status(task_id: str):
    """
    Get the status of a task
    """
    with task_lock:
        result = task_results.get(task_id)
        if result is None:
            raise HTTPException(status_code=404, detail="Task not found")

        return {
            "success": True,
            "data": result,
            "message": "Task status retrieved successfully"
        }


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
