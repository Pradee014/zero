import sys
import os
sys.path.append(os.path.abspath("src"))

from orchestrator.llm_utils import get_llm

# Simulate User Env
os.environ["ZERO_GROQ_API_KEY"] = "gsk_test"
os.environ["ZERO_MODEL"] = "gpt-oss:120b"

llm = get_llm()
print(f"Assigned Model: {llm.model_name}")

if llm.model_name == "llama3-70b-8192":
    print("SUCCESS: Legacy model overridden.")
else:
    print(f"FAILURE: Model is {llm.model_name}")
