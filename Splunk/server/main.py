from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from splunk_client import run_splunk_query

app = FastAPI(title="Splunk MCP Server")

class QueryRequest(BaseModel):
    spl_query: str

@app.post("/query_splunk")
def query_splunk(req: QueryRequest):
    try:
        result = run_splunk_query(req.spl_query)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
