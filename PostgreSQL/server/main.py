from fastapi import FastAPI, HTTPException, Request
from db import query_database, get_schema

app = FastAPI(title="PostgreSQL MCP Server")


@app.post("/query_database")
async def handle_query(request: Request):
    data = await request.json()
    query = data.get("query")
    if not query:
        raise HTTPException(status_code=400, detail="Query parameter is required")
    result = query_database(query)
    return {"result": result}

@app.post("/get_schema")
async def handle_get_schema():
    schema = get_schema()
    return {"schema": schema}