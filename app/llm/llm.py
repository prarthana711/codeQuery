import ollama


class LLM:

    def generate(self, question, contexts):

        prompt = """
You are CodeQuery, an AI assistant for understanding GitHub repositories.

Rules:

1. Use ONLY the provided repository context.
2. Mention file names whenever possible.
3. If the answer is missing, say so.
4. Do not invent functions or classes.
5. Explain the code like you're teaching a beginner.

Repository Context:

"""

        for context in contexts:

            prompt += f"File: {context['document']['path']}\n"

            prompt += f"Chunk: {context['document']['chunk_id']}\n\n"

            prompt += context["document"]["content"]

            prompt += "\n"

            prompt += "=" * 60

            prompt += "\n\n"
        prompt += f"Question:\n{question}\n\nAnswer:"

        response = ollama.chat(
            model="llama3.2",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response["message"]["content"]