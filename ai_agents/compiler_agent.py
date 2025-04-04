from agents import Agent, Runner
from dotenv import load_dotenv

load_dotenv()


class CompilerAgent:
    def __init__(self):
        """
        Initialize the CompilerAgent with OpenAI's Agent and instructions.
        """

        self.agent = Agent(
            name="Compiler Agent",
            instructions="Compile the results from the text given which is an appended texts from different sources.",
            model="gpt-4o",
        )

    async def run(self, to_compile):
        """
        Run the agent to compile the results from different sources.
        """

        result = await Runner.run(self.agent, to_compile)

        return result.final_output
