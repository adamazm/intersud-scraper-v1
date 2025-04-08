from agents import Agent, Runner
from dotenv import load_dotenv
from config import example_result

load_dotenv()


class CompilerAgent:
    def __init__(self):
        """
        Initialize the CompilerAgent with OpenAI's Agent and instructions.
        """

        self.agent = Agent(
            name="Compiler Agent",
            instructions=f"Compile the results from the text given which is an appended texts from different sources to this format which is an example of a company called Air Liquide: {example_result}. It is important to translate the result to French and make it as paragraphs instead of bullet points. The result should be in the same format as the example.",
            model="gpt-4o",
        )

    async def run(self, to_compile):
        """
        Run the agent to compile the results from different sources.
        """

        result = await Runner.run(self.agent, to_compile)

        return result.final_output
