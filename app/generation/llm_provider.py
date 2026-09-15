from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
import os

#GENERATIVE_MODEL = "llama3.2"
GENERATIVE_MODEL = "gemini-3.5-flash-lite"
class LLMProvider:
    def __init__(self, model: str = GENERATIVE_MODEL):
        # self.llm = ChatOllama(
        #     model=model,
        #     temperature=0,
        # )

        self.llm = ChatGoogleGenerativeAI(
        model=model,
        api_key=os.getenv("GOOGLE_API_KEY"),
        )
    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        response = self.llm.invoke(
            [
                ("system", system_prompt),
                ("user", user_prompt),
            ]
        )

        return response.content

def get_llm_provider():
    return LLMProvider()