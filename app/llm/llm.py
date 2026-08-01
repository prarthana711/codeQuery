import ollama


class LLM:

    def generate(self, question, contexts):

        prompt = """
You are an expert software engineer.

Answer ONLY using the provided repository context.

If the answer cannot be found in the context,
say that you couldn't find it.

Repository Context:

"""

        for context in contexts:

            prompt += context["document"]["content"]

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