import requests
import time
from dotenv import load_dotenv
import os

load_dotenv()

ENV = os.getenv("ENV", "production")  # or "development"
if ENV == "development":
    BACKEND_URL = "http://localhost:8000"
else:
    BACKEND_URL = "/api"


class ApiClient:
    def __init__(self, base_url=BACKEND_URL):
        self.base_url = base_url

    def get_societe_api_results(self, company_name: str):
        """
        Get the results from the societe.com API for a given company name.
        """
        url = f"{self.base_url}/get-companies"
        params = {
            "company_name": company_name
        }
        response = requests.get(url, params=params)
        return response

    def scrape_company(self, company_id: str, id_type: str):
        """
        Scrape the company information from the website.
        """
        url = f"{self.base_url}/scrape-company"
        params = {
            "company_id": company_id,
            "id_type": id_type
        }

        response = requests.post(url, params=params)
        return response

    def poll_task_status(self, task_id: str, progress_container, progress_bar=None):
        """
        Poll the status of a task
        """
        url = f"{self.base_url}/get-task-status/{task_id}"
        while True:
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    result = response.json()
                    task_data = result.get("data", {})
                    status = task_data.get("status")
                    progress = task_data.get("progress", 0)

                    # Update progress bar if provided
                    if progress_bar is not None:
                        progress_bar.progress(progress / 100.0)

                    if status == "completed":
                        progress_container.success("Scraping completed")
                        return task_data
                    elif status == "failed":
                        error_message = task_data.get("error", "Unknown error")
                        progress_container.error(error_message)
                        return False
                    elif status == "cancelled":
                        progress_container.error("Task cancelled")
                        return False

                    time.sleep(2)
                else:
                    raise Exception(
                        f"Failed to get task status: {response.status_code}")
            except Exception as e:
                progress_container.error(f"Scraping failed: {str(e)}")
                return False
