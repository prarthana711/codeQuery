def chunk_text(text, chunk_size=500, overlap=100):
    chunks = []

    current_index = 0

    while current_index < len(text):

        ending_index = current_index + chunk_size

        chunk = text[current_index:ending_index]

        chunks.append(chunk)

        current_index = ending_index - overlap

    return chunks

def chunk_documents(documents):
    chunked_documents = []

    for document in documents:

        chunks = chunk_text(document["content"])

        for i, chunk in enumerate(chunks):

            chunked_documents.append({
                "path": document["path"],
                "chunk_id": i,
                "content": chunk
            })

    return chunked_documents