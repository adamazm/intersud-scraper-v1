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
from helpers import get_year_data, get_years_from_ellisphere, get_detailed_report_data, get_companies_from_societe_api

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


def update_task_status(task_id, status, data=None, error=None, progress=None):
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

        # Update the task status to running
        update_task_status(task_id, TaskStatus.RUNNING.value, progress=0)

        results = {}

        # Phase 1: Run independent scrapers
        for i, scraper_config in enumerate(independent_scrapers):
            # Update progress at start of each scraper
            current_progress = int(i * progress_per_independent)
            update_task_status(
                task_id, TaskStatus.RUNNING.value, progress=current_progress)

            # Handle different scraper types
            if scraper_config["name"] == "ellisphere":
                # Ellisphere uses async functions, so use run_async helper
                result = run_async(scraper_config["task_function"](company_id))
            else:
                # Standard scrapers use ScrapingAgent
                agent = ScrapingAgent(
                    scraper_config["task_function"](company_id, id_type))
                result = run_async(agent.scrape(company_id, id_type))

            results[scraper_config["name"]] = result

            # Update progress after completing this scraper
            completed_progress = int((i + 1) * progress_per_independent)
            update_task_status(task_id, TaskStatus.RUNNING.value,
                               progress=completed_progress)

        # Phase 2: Run dependent scrapers
        for i, scraper_config in enumerate(dependent_scrapers):
            # Update progress at start of each dependent scraper
            current_progress = int(
                independent_progress + (i * progress_per_dependent))
            update_task_status(
                task_id, TaskStatus.RUNNING.value, progress=current_progress)

            # Get input data from dependency
            input_data = get_dependency_input(
                results, scraper_config.get("depends_on", []))

            if input_data is None:
                # No valid input found, skip this scraper or use fallback
                results[scraper_config["name"]] = None
                continue

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

            # Update progress after completing this scraper
            completed_progress = int(
                independent_progress + ((i + 1) * progress_per_dependent))
            update_task_status(task_id, TaskStatus.RUNNING.value,
                               progress=completed_progress)

        # Phase 3: Compile all results into human-readable document
        update_task_status(task_id, TaskStatus.RUNNING.value, progress=95)
        compiled_document = run_async(compile_results(results))
        results["compiled_report"] = compiled_document

        # Ensure final progress is exactly 100%
        update_task_status(task_id, TaskStatus.COMPLETED.value,
                           data=results, progress=100)

    except Exception as e:
        update_task_status(task_id, TaskStatus.FAILED.value,
                           error=str(e), progress=0)


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
    Compile results from multiple scrapers into a human-readable document
    """
    try:
        # Prepare compilation input with JSON results
        compilation_input = ""

        # Add results from each scraper
        for scraper_name, scraper_result in results.items():
            if scraper_result and scraper_name != "ellisphere":  # Ellisphere handled separately
                compilation_input += f"\n=== {scraper_name.title()} Results ===\n"
                compilation_input += str(scraper_result) + "\n"

        # Handle ellisphere separately (list of reports)
        if "ellisphere" in results and results["ellisphere"]:
            compilation_input += "\n=== Ellisphere Results ===\n"
            ellisphere_data = results["ellisphere"]
            if isinstance(ellisphere_data, list):
                for i, report in enumerate(ellisphere_data):
                    compilation_input += f"Report {i+1}:\n{report}\n\n"
            else:
                compilation_input += str(ellisphere_data) + "\n"

        # Use the compiler agent to create human-readable document
        compiler = OpenAICompiler()
        compiled_document = await compiler.run(compilation_input)

        return compiled_document

    except Exception as e:
        return f"Error during compilation: {str(e)}"


async def process_ellisphere(company_id):
    """Scrape from Ellisphere (XML-based, no browser needed)"""
    try:
        xml_content = get_year_data(company_id)
        ellisphere_agent = EllisphereAgent()
        ellisphere_results = []

        available_reports = get_years_from_ellisphere(xml_content)
        for year in available_reports:
            xml_result = get_detailed_report_data(company_id, year)
            compiled_xml = await ellisphere_agent.parse_xml(xml_result)
            ellisphere_results.append(compiled_xml)

        return ellisphere_results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
