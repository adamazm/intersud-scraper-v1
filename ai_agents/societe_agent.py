from .scraper_agent import ScraperAgent
from tasks import societe_scrape_task


class SocieteAgent(ScraperAgent):
    def __init__(self, llm_model, browser, company_id, id_type):
        super().__init__(llm_model, browser)
        self.company_id = company_id
        self.id_type = id_type

    def create_task(self):
        """
        Create a scraping task for the SocieteAgent.
        """
        return societe_scrape_task(
            company_id=self.company_id,
            id_type=self.id_type,
        )
