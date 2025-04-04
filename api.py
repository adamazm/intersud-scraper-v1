from flask import Flask, request, jsonify
from scraper import Scraper
from config import openai_model, browser_config
from browser_use import Browser
import asyncio
import time

app = Flask(__name__)


async def scrape_and_compile(company_id, id_type):
    """
    Scrape data from different sources and compile the results.

    :param company_id: The identification of the company to scrape data for.
    :param id_type: The type of ID (e.g. Name, SIREN, SIRET) to be used for scraping.
    :return: The compiled result from all agents.
    """

    # Initialize the browser and scraper
    browser = Browser(browser_config)
    scraper = Scraper(
        llm_model=openai_model,
        browser=browser,
    )

    agents = scraper.create_agents(company_id, id_type)
    time.sleep(2)  # Allow time for the agents to initialize

    results = []
    for agent in agents:
        result = await agent.run()
        results.append(result)

    return results


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

    try:
        time.sleep(10)  # Allow time for the browser to initialize
        response = asyncio.run(scrape_and_compile(company_id, id_type))

        # If response is a list or dict, return it as JSON
        if isinstance(response, (list, dict)):
            return jsonify(response)

        # Otherwise, return it as plain text
        return str(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5001, use_reloader=False)
