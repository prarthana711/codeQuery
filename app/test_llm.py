from app.llm.llm import LLM

llm = LLM()

contexts = [
    {
        "document": {
            "content": "Python is a programming language."
        }
    }
]

answer = llm.generate(
    "What is Python?",
    contexts
)

print(answer)