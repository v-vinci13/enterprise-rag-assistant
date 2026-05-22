from fastapi import FastAPI
from pydantic import BaseModel

from rag_pipeline import generate_answer

app = FastAPI()

class QueryRequest(BaseModel):
    username: str
    query: str

@app.post("/query")
def query_rag(request: QueryRequest):

    answer = generate_answer(
        request.query,
        request.username
    )

    return {
        "answer": answer
    }