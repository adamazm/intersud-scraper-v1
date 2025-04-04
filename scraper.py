from ai_agents import PappersAgent, InfogreffeAgent, SocieteAgent, GoogleAgent, CompilerAgent


class Scraper:
    """
    Scraper class to manage the scraping process using different agents.
    """

    def __init__(self, llm_model, browser):
        """
        Initialize the Scraper with a language model and browser instance.

        :param llm_model: The language model to be used for processing.
        :param browser: browser-use's Browser.
        """
        self.llm_model = llm_model
        self.browser = browser

    def create_agents(self, company_id, id_type):
        """
        Create a list of agents to scrape data from different sources.

        :param company_id: The identification of the company to scrape data for.
        :param id_type: The type of ID (e.g. Name, SIREN, SIRET) to be used for scraping.
        :return: A list of agent instances.
        """

        return [
            PappersAgent(self.llm_model, self.browser, company_id, id_type),
            InfogreffeAgent(self.llm_model, self.browser, company_id, id_type),
            SocieteAgent(self.llm_model, self.browser, company_id, id_type),
            # GoogleAgent(self.llm_model, self.browser, company_id, id_type),
        ]

    async def scrape_and_compile(self, company_id: str, id_type):
        """
        Scrape data from different sources and compile the results.

        :param company_id: The identification of the company to scrape data for.
        :param id_type: The type of ID (e.g. Name, SIREN, SIRET) to be used for scraping.

        :return: The compiled result from all agents.
        """

        # Create agents for scraping
        agents = self.create_agents(company_id, id_type)

        # Create a compiler agent to compile results
        compiler_agent = CompilerAgent()

        results = []
        for agent in agents:
            # Run each agent and collect the results
            result = await agent.run()
            results.append(result)

        compiled_result = await compiler_agent.run(results)

        return compiled_result
