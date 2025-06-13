from config.model import llm
from browser_use import Agent, BrowserSession


class ScrapingAgent:
    def __init__(self, task):
        self.task = task

    async def scrape(self, company_id, id_type):
        browser_session = BrowserSession(
            headless=False,
        )

        agent = Agent(
            task=self.task,
            llm=llm,
            browser_session=browser_session,
        )

        history = await agent.run()
        await browser_session.close()
        result = history.final_result()
        return result
