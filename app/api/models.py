from pydantic import BaseModel


class QuestionRequest(BaseModel):
    question: str

class RepositoryRequest(BaseModel):

    repo_url: str