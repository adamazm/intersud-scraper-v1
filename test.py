from browser_use import Agent
from config import openai_model
import asyncio
from dotenv import load_dotenv

load_dotenv()


agent = Agent(
    llm=openai_model,
    task="Go to Google and search for 'Python programming'.",
)


async def main():
    result = await agent.run()
    print(result.final_result())


if __name__ == "__main__":
    asyncio.run(main())
