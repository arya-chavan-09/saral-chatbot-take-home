from langchain_ollama import ChatOllama

class LLMProvider:
    def __init__(self, model: str = "llama3.2"):
        self.llm = ChatOllama(
            model=model,
            temperature=0,
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