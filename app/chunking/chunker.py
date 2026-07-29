def chunk_text(text, chunk_size=500, overlap=100):
    chunks = []

    current_index = 0

    while current_index < len(text):

        ending_index = current_index + chunk_size

        chunk = text[current_index:ending_index]

        chunks.append(chunk)

        current_index = ending_index - overlap

    return chunks

text = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

chunks = chunk_text(text, chunk_size=5, overlap=2)

for chunk in chunks:
    print(chunk)