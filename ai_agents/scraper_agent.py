from abc import ABC, abstractmethod
from browser_use import Agent


class ScraperAgent(ABC):
    def __init__(self, llm_model, browser, cancel_event=None):
        """
        Initialize the ScraperAgent with a language model and browser instance.

        :param llm_model: The language model to be used for processing.
        :param browser: browser-use's Browser.
        """

        self.llm_model = llm_model
        self.browser = browser
        self.agent = None
        self.cancel_event = cancel_event

    @abstractmethod
    def create_task(self):
        """
        Abstract method to create a task for the agent to perform.
        """
        pass

    def initialize_agent(self):
        """
        Initialize the agent with the language model, task, and browser instance.
        """

        # Create the task for the agent
        # This method should be implemented in the subclasses
        task = self.create_task()
        self.agent = Agent(
            llm=self.llm_model,
            task=task,
            browser=self.browser,
        )

    async def run(self):
        """
        Run the agent to perform the scraping task.

        :return: The final result from the agent after running the task.
        """

        if self.cancel_event and self.cancel_event.is_set():
            print("Agent cancelled before starting")
            return None

        if not self.agent:
            self.initialize_agent()
        result = await self.agent.run()
        return result.final_result()

    async def save_output(self, output_path):
        """
        Save the output of the agent to a specified file.
        """

        result = await self.run()
        with open(output_path, "w") as file:
            file.write(result)
