from agents import Agent, Runner, ModelSettings
from dotenv import load_dotenv
from config import ellisphere_result_instruction

load_dotenv()


class EllisphereCompilerAgent:
    def __init__(self):
        """
        Initialize the CompilerAgent with OpenAI's Agent and instructions.
        """

        self.agent = Agent(
            name="Translator And Compiler Agent",
            instructions=ellisphere_result_instruction,
            model="gpt-4o",
            model_settings=ModelSettings(
                max_tokens=30000,
                truncation="disabled",
            )
        )

    async def run(self, to_translate):
        """
        Run the agent to compile the results from different sources.
        """

        result = await Runner.run(self.agent, to_translate)
        final_output = result.final_output

        return final_output
