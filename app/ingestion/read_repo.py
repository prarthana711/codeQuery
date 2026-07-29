import os
from app.chunking.chunker import chunk_text

documents = []
repo_path = "repositories/repo"

for root, dirs, files in os.walk(repo_path):
    for file in files:
        if file.endswith((".py", ".md", ".txt")):

            full_path = os.path.join(root, file)
            #print(full_path)
            try:
                with open(full_path, "r",encoding="utf-8",errors="ignore") as f:
                    content = f.read()
                chunks=chunk_text(content)
                for chunk in chunks:
                    documents.append(
                        {
                            "path": full_path,
                            "content": chunk
                        }
                    )
            except Exception as e:
                print(e)
print(len(documents))

                