import ollama


class LLM:

    def generate(self, question, contexts):

        if not contexts:
            return (
                "I couldn't find anything in this repository relevant to that question. "
                "Try rephrasing, or ask about a specific file or feature you know exists."
            )

        prompt = """You are CodeQuery, an AI assistant that explains GitHub repositories accurately.

Rules:
1. Use ONLY the provided repository context below — never invent functions, classes, or behavior that isn't shown.
2. Always mention the specific file name (and line numbers, if given) that supports each part of your answer.
3. If the provided context doesn't fully answer the question, say so explicitly rather than guessing.
4. Explain code clearly, as if teaching a beginner, but stay precise about what the code actually does.

Repository Context:

"""

        for context in contexts:
            doc = context["document"]
            location = doc["path"]
            if "start_line" in doc:
                location += f" (lines {doc['start_line']}-{doc['end_line']})"

            prompt += f"--- {location} ---\n"
            prompt += doc["content"]
            prompt += "\n\n"

        prompt += f"Question:\n{question}\n\nAnswer:"

        response = ollama.chat(
            model="llama3.2",
            messages=[
                {"role": "user", "content": prompt}
            ],
            options={
                "temperature": 0.2  # lower = more literal/grounded, less prone to filling gaps with guesses
            },
        )

        return response["message"]["content"]