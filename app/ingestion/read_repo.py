import os

from app.ingestion.filters import (
    should_include_dir,
    should_include_file,
    MAX_FILE_SIZE,
)


def read_repository(repo_path):
    documents = []

    for root, dirs, files in os.walk(repo_path):
        # Prune excluded directories in place so os.walk never descends into them
        dirs[:] = [d for d in dirs if should_include_dir(d)]

        for file in files:
            full_path = os.path.join(root, file)

            if not should_include_file(full_path):
                continue

            try:
                if os.path.getsize(full_path) > MAX_FILE_SIZE:
                    continue
            except OSError:
                continue

            try:
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            except Exception as e:
                print(f"Skipping {full_path}: {e}")
                continue

            if not content.strip():
                continue

            documents.append({
                "path": full_path,
                "content": content,
            })

    return documents