import os

def read_repository(repo_path):

    documents = []

    for root, dirs, files in os.walk(repo_path):

        for file in files:

            if file.endswith((".py", ".md", ".txt")):

                full_path = os.path.join(root, file)

                try:

                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:

                        content = f.read()

                    documents.append(
                        {
                            "path": full_path,
                            "content": content
                        }
                    )

                except Exception as e:
                    print(e)

    return documents