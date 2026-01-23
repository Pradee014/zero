import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

# Load env
load_dotenv()

host = os.getenv("ZERO_OLLAMA_HOST")
key = os.getenv("ZERO_API_KEY")
model_name = os.getenv("ZERO_MODEL", "llama3.2")

try:
    print("Initializing ChatOpenAI...")
    chat = ChatOpenAI(
        base_url=host,
        model=model_name,
        api_key=key if key else "EMPTY",
        temperature=0
    )

    print("Sending chat request...")
    response = chat.invoke([HumanMessage(content="Hello")])
    
    print("\n--- SUCCESS ---")
    print(response.content)

except Exception as e:
    print("\n--- FAILED ---")
    # print(e)
    # Print simpler error for user
    if "401" in str(e):
        print("Error: 401 Unauthorized. The server rejected the key.")
    elif "404" in str(e):
        print("Error: 404 Not Found. The model or endpoint does not exist.")
    else:
        print(e)
