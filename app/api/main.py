from fastapi import FastAPI
from app.api.models import QuestionRequest, RepositoryRequest
from app.ingestion.read_repo import read_repository
from app.chunking.chunker import chunk_documents
from app.pipeline.pipeline import Pipeline
from app.llm.llm import LLM
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
from git import Repo

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
pipeline = Pipeline()
llm = LLM()



def build_repository(repo_path):

    pipeline.store.reset()

    documents = read_repository(repo_path)

    chunked_documents = chunk_documents(documents)

    pipeline.build(chunked_documents)

    return {
        "files": len(documents),
        "chunks": len(chunked_documents)
    }

if os.path.exists("repositories/active_repo"):

    build_repository("repositories/active_repo")

    print("Repository indexed successfully!")
@app.get("/")
def home():

    return {
        "message": "Welcome to CodeQuery API"
    }

@app.post("/clone")
def clone_repository(request: RepositoryRequest):

    repo_directory = "repositories/repo"

    if os.path.exists(repo_directory):
        shutil.rmtree(repo_directory)

    Repo.clone_from(request.repo_url, repo_directory)

    stats = build_repository(repo_directory)

    repo_name = request.repo_url.rstrip("/").split("/")[-1]
    owner = request.repo_url.rstrip("/").split("/")[-2]

    return {
        "message": "Repository analyzed successfully!",
        "repository": repo_name,
        "owner": owner,
        "files": stats["files"],
        "chunks": stats["chunks"]
    }


@app.post("/ask")
def ask(request: QuestionRequest):

    results = pipeline.search(request.question)

    answer = llm.generate(request.question, results)
    sources = []

    for result in results:
        sources.append(result["document"]["path"])
    sources = list(set(sources))
    return {
        "question": request.question,
        "answer": answer,
        "sources":sources
    }