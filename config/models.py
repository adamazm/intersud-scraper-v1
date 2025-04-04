from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

# Initialize the OpenAI model with the specified parameters
openai_model = ChatOpenAI(
    model="gpt-4o",
    max_completion_tokens=500,
)
