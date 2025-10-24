import os
import faiss
import numpy as np
from google import genai
from dotenv import load_dotenv
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


vector_dim = 768 # Gemini embeddings dimension
index = faiss.IndexFlatL2(vector_dim)
chat_memory = []  # stores {"question": ..., "answer": ..., "vector": ...}

def get_full_memory():
    return chat_memory

# store in faiss db (this is memory):
def add_to_memory(question, answer):
    text = question + " " + answer

    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
        config=types.EmbedContentConfig(output_dimensionality=768))
    
    [embedding_obj] = result.embeddings

    # Convert to NumPy array for FAISS
    vector = np.array(embedding_obj.values, dtype="float32")

    # Add to FAISS index
    index.add(np.array([vector]))

    # Store in memory
    chat_memory.append({"question": question, "answer": answer, "vector": vector})


# user query translation to embeddings
def retrieve_memory(query, top_k=5):
    if len(chat_memory) == 0:
        return []

    # Generate embedding for query
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=query,
        config=types.EmbedContentConfig(output_dimensionality=768))
    
    [embedding_obj] = result.embeddings

    # Convert to NumPy array for FAISS
    query_vector = np.array(embedding_obj.values, dtype="float32")

    # Search FAISS
    D, I = index.search(np.array([query_vector]), top_k)
    retrieved = [chat_memory[i] for i in I[0] if i < len(chat_memory)]
    return retrieved


