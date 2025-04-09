from .scraper_agent import ScraperAgent
from tasks import infogreffe_scrape_task


class InfogreffeAgent(ScraperAgent):
    """
    InfogreffeAgent class to scrape data from Infogreffe website.
    """

    def __init__(self, llm_model, browser, company_id, id_type, cancel_event=None):
        """
        Initialize the InfogreffeAgent with a language model, browser instance, company ID, and ID type.

        :param llm_model: The language model to be used for processing.
        :param browser: browser-use's Browser.
        :param company_id: The identification of the company to scrape data for.
        :param id_type: The type of ID (e.g. Name, SIREN, SIRET) to be used for scraping.
        """

        super().__init__(llm_model, browser, cancel_event)
        self.company_id = company_id
        self.id_type = id_type

    def create_task(self):
        """
        Create a scraping task for the InfogreffeAgent.
        """

        return infogreffe_scrape_task(
            company_id=self.company_id,
            id_type=self.id_type,
        )
