import os
import requests
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MCP_URL = "http://localhost:8000/query_splunk"

def clean_spl(spl_text: str) -> str:
    """Remove markdown code block syntax."""
    spl = spl_text.strip()
    if spl.startswith("```"):
        spl = spl.split("\n", 1)[1]
        if spl.endswith("```"):
            spl = spl.rsplit("\n", 1)[0]
    return spl.strip()

def ask_gemini(question: str):
    schema_hint = (
        "You are a Splunk expert. Convert natural language to SPL (Search Processing Language). "
        "Do not include markdown or ```sql``` tags. Output plain SPL only."
    )
    prompt = f"{schema_hint}\nQuestion: {question}\nSPL:"
    response = client.models.generate_content( model="gemini-2.5-flash", contents=prompt)
    return clean_spl(response.text.strip())

def query_mcp(spl_query: str):
    response = requests.post(MCP_URL, json={"spl_query": spl_query})
    if response.status_code != 200:
        raise Exception(f"MCP query failed: {response.text}")
    return response.json()

if __name__ == "__main__":
    user_q = input("Ask a log question: ")
    spl_query = ask_gemini(user_q)
    print("\nGenerated SPL:\n", spl_query)

    result = query_mcp(spl_query)
    print("\nSplunk Result:\n", result)

    # # Optional: Summarize results
    # model = genai.GenerativeModel("gemini-1.5-flash")
    # summary = model.generate_content(f"Summarize the following log data in one sentence:\n{result}")
    # print("\nGemini Summary:\n", summary.text)
