from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from git import Repo, GitCommandError
import os
import shutil

from app.api.models import QuestionRequest, RepositoryRequest
from app.ingestion.read_repo import read_repository
from app.chunking.chunker import chunk_documents
from app.pipeline.pipeline import Pipeline
from app.llm.llm import LLM

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = Pipeline()
llm = LLM()

# Always clone into the same path. Previously /clone used a fresh uuid folder
# each time, which (a) left every old clone sitting on disk forever, and
# (b) didn't match the frontend's `source.replace("repositories/active_repo", "")`
# call, so cleaned-up file paths never actually matched and users saw the
# full raw path instead.
REPO_PATH = "repositories/active_repo"


def build_repository(repo_path):
    pipeline.store.reset()
    documents = read_repository(repo_path)
    chunked_documents = chunk_documents(documents)
    pipeline.build(chunked_documents)
    return {
        "files": len(documents),
        "chunks": len(chunked_documents),
    }


if os.path.exists(REPO_PATH):
    build_repository(REPO_PATH)
    print("Repository indexed successfully!")


@app.get("/")
def home():
    return {"message": "Welcome to CodeQuery API"}


@app.post("/clone")
def clone_repository(request: RepositoryRequest):

    if os.path.exists(REPO_PATH):
        shutil.rmtree(REPO_PATH)

    try:
        Repo.clone_from(request.repo_url, REPO_PATH)
    except GitCommandError:
        raise HTTPException(
            status_code=400,
            detail="Couldn't clone that repository. Check that the URL is correct and the repo is public.",
        )

    stats = build_repository(REPO_PATH)

    if stats["files"] == 0:
        raise HTTPException(
            status_code=400,
            detail="No readable files found in this repository (check supported file types and size limits).",
        )

    repo_name = request.repo_url.rstrip("/").split("/")[-1]
    owner = request.repo_url.rstrip("/").split("/")[-2]

    return {
        "message": "Repository analyzed successfully!",
        "repository": repo_name,
        "owner": owner,
        "files": stats["files"],
        "chunks": stats["chunks"],
    }


@app.post("/ask")
def ask(request: QuestionRequest):
    if not os.path.exists(REPO_PATH):
        raise HTTPException(
            status_code=400,
            detail="No repository has been analyzed yet. Clone one first.",
        )

    results = pipeline.search(request.question)
    answer = llm.generate(request.question, results)

    sources = []
    for result in results:
        doc = result["document"]
        clean_path = doc["path"].replace(f"{REPO_PATH}/", "")
        if "start_line" in doc:
            clean_path += f" (lines {doc['start_line']}-{doc['end_line']})"
        sources.append(clean_path)

    sources = list(dict.fromkeys(sources))  # dedupe while preserving order

    return {
        "question": request.question,
        "answer": answer,
        "sources": sources,
    }