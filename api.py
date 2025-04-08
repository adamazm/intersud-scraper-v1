from flask import Flask, request, jsonify
import asyncio
from ai_agents import PappersAgent, InfogreffeAgent, SocieteAgent, TranslatorAgent
from config import openai_model, browser_config
from browser_use import Browser
import time

app = Flask(__name__)

llm_model = openai_model


def create_agents(llm_model, browser, company_id, id_type):
    """
    Create a list of agents to scrape data from different sources.

    :param company_id: The identification of the company to scrape data for.
    :param id_type: The type of ID (e.g. Name, SIREN, SIRET) to be used for scraping.
    :return: A list of agent instances.
    """

    return [
        PappersAgent(llm_model, browser, company_id, id_type),
        InfogreffeAgent(llm_model, browser, company_id, id_type),
        SocieteAgent(llm_model, browser, company_id, id_type),
    ]


async def scrape_and_compile(llm_model, browser, company_id: str, id_type: str):
    """
    Scrape data from different sources and compile the results.

    :param company_id: The identification of the company to scrape data for.
    :param id_type: The type of ID (e.g. Name, SIREN, SIRET) to be used for scraping.

    :return: The compiled result from all agents.
    """

    # Create agents for scraping
    agents = create_agents(llm_model, browser, company_id, id_type)

    # Create a compiler agent to compile results
    translator_agent = TranslatorAgent()

    results = []
    for agent in agents:
        # Run each agent and collect the results
        result = await agent.run()
        results.append(result)

    compiled_result = await translator_agent.run(results[0])

    # Fix encoding issues
    if isinstance(compiled_result, str):
        # Try to fix common encoding issues
        try:
            # First approach: If the text was accidentally double-encoded
            compiled_result = compiled_result.encode('latin1').decode('utf-8')
        except (UnicodeError, UnicodeDecodeError):
            try:
                # Second approach: Force utf-8 encoding
                compiled_result = compiled_result.encode(
                    'utf-8', errors='ignore').decode('utf-8')
            except:
                pass  # Keep original if both approaches fail

    return compiled_result


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
        browser = Browser(browser_config)
        time.sleep(5)  # Allow time for the browser to initialize
        result = asyncio.run(scrape_and_compile(
            llm_model, browser, company_id, id_type))

        # Create a Flask response object
        if isinstance(result, (list, dict)):
            response = jsonify(result)
        else:
            response = jsonify({"data": str(result)})

        # Set headers on the response object
        response.headers['Content-Type'] = 'application/json; charset=utf-8'

        return response

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=False)
