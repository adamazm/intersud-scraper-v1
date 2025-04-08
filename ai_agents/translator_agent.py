from agents import Agent, Runner
from dotenv import load_dotenv
from config import example_result

load_dotenv()


class TranslatorAgent:
    def __init__(self):
        """
        Initialize the CompilerAgent with OpenAI's Agent and instructions.
        """

        self.agent = Agent(
            name="Translator Agent",
            instructions=f"Translate the result of the text given which is an appended texts from different sources to French. Make sure the accents are decoded. Then from bullet points (if they are in bullet points), transform them into paragraphs. The result should be in the same format as the example: {example_result}",
            model="gpt-4o",
        )

    async def run(self, to_translate):
        """
        Run the agent to compile the results from different sources.
        """

        result = await Runner.run(self.agent, to_translate)
        final_output = result.final_output

        return final_output
