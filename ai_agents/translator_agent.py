from agents import Agent, Runner
from dotenv import load_dotenv
from config import result_instruction

load_dotenv()


class TranslatorAgent:
    def __init__(self):
        """
        Initialize the CompilerAgent with OpenAI's Agent and instructions.
        """

        self.agent = Agent(
            name="Translator Agent",
            instructions=result_instruction,
            model="gpt-4o",
        )

    async def run(self, to_translate):
        """
        Run the agent to compile the results from different sources.
        """

        result = await Runner.run(self.agent, to_translate)
        final_output = result.final_output

        return final_output
