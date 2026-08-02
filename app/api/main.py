from fastapi import FastAPI
from app.api.models import QuestionRequest
from app.ingestion.read_repo import read_repository
from app.chunking.chunker import chunk_documents
from app.pipeline.pipeline import Pipeline
from app.llm.llm import LLM

app = FastAPI()
pipeline = Pipeline()
llm = LLM()

repo_path = "repositories/repo"

documents = read_repository(repo_path)

chunked_documents = chunk_documents(documents)

pipeline.build(chunked_documents)

print("Repository indexed successfully!")
@app.get("/")
def home():

    return {
        "message": "Welcome to CodeQuery API"
    }

@app.post("/ask")
def ask(request: QuestionRequest):

    results = pipeline.search(request.question)

    answer = llm.generate(request.question, results)

    return {
        "question": request.question,
        "answer": answer
    }