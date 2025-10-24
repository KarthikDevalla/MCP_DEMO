import os
from google import genai
from dotenv import load_dotenv
import requests
import json
import re
import chainlit as cl
from vectordb import retrieve_memory, add_to_memory, get_full_memory

load_dotenv()


@cl.on_chat_start
async def init_chat():
    await cl.Message(
        content="Welcome! Ask me anything about your database. Your past chats are in the sidebar."
    ).send()


# Initialize Gemini client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MCP_SERVER_URL = "http://localhost:8001"

def query_mcp(sql_query: str):
    response = requests.post(f"{MCP_SERVER_URL}/query_database", json={"query": sql_query})
    if response.status_code == 200:
        return response.json()["result"]
    else:
        raise Exception(f"MCP query failed: {response.text}")

def get_db_schema():
    response = requests.post(f"{MCP_SERVER_URL}/get_schema")
    return response.json()["schema"]


def ask_gemini(question: str):
    relevant_history = retrieve_memory(question)
    history_prompt = ""
    for h in relevant_history:
        history_prompt += f"Q: {h['question']}\nA: {h['answer']}\n"

    schema = get_db_schema()

    sql_prompt = f"""
    Use the relevant context from past conversations:
    {history_prompt}  if it is relevant to the question the user asked.
    You are a SQL expert. The database schema is:{json.dumps(schema, indent=2)}
    Generate a SQL query to answer the following question:
    Question: {question}
    Respond ONLY with the SQL query. The user might not give you the exact name of the column or entity you need to go check the schema and data to understand what the user is talking about.
    Remove backticks, ```sql blocks, and extra whitespace from the SQL output.
    """
    gemini_response = client.models.generate_content( model="gemini-2.5-flash", contents=sql_prompt)
    sql_query = gemini_response.text.strip()
    print("Generated SQL:", sql_query)

    result = query_mcp(sql_query)
   
    summarize_prompt = f"""
    You are a helpful assistant. The SQL query result is: {json.dumps(result)}.
    Answer the user's question in natural language based on this result.
    Question: {question}
    """
    final_response = client.models.generate_content( model="gemini-2.5-flash", contents=summarize_prompt)
    add_to_memory(question, final_response.text)
    return final_response.text

@cl.on_message
async def main_chat(message: cl.Message):
    user_q = message.content
    msg=await cl.Message(content="Thinking...").send()
    try:
        answer = ask_gemini(user_q)
        msg.content=answer
        await msg.update()
    except Exception as e:
        error=f"Error: {e}"
        msg.content=error
        await msg.update()