import os
from langchain_openai import ChatOpenAI

def get_llm(default_model_name: str = "llama3.2", model_env_var: str = "ZERO_MODEL") -> ChatOpenAI:
    """
    Returns a configured ChatOpenAI instance for Groq.
    Strictly uses Groq as the provider.
    """
    
    # 1. Get Groq API Key
    groq_api_key = os.getenv("ZERO_GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("ZERO_GROQ_API_KEY is missing in .env. Please set it to use Groq.")

    # 2. Get Model from Env
    # User instruction: "Just use .env file variable"
    assigned_model = os.getenv(model_env_var, default_model_name)
    
    print(f"Zero: Using Groq Model: '{assigned_model}'")
    
    return ChatOpenAI(
        model=assigned_model,
        temperature=0,
        base_url="https://api.groq.com/openai/v1",
        api_key=groq_api_key
    )
