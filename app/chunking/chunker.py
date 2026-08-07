import ast

# If a single function/class is bigger than this, sub-chunk it further
MAX_CHUNK_CHARS = 1500

# For non-Python files (or Python that fails to parse), chunk by lines instead
LINE_CHUNK_SIZE = 40
LINE_OVERLAP = 5


def _chunk_by_lines(content, base_line=1, size=LINE_CHUNK_SIZE, overlap=LINE_OVERLAP):
    """
    Fallback chunker: splits by whole lines (never mid-line/mid-word) with a
    small overlap so context isn't lost at chunk boundaries.
    """
    lines = content.splitlines()
    chunks = []
    i = 0
    while i < len(lines):
        block_lines = lines[i:i + size]
        block = "\n".join(block_lines).strip()
        if block:
            chunks.append({
                "content": block,
                "start_line": base_line + i,
                "end_line": base_line + i + len(block_lines) - 1,
            })
        if i + size >= len(lines):
            break
        i += size - overlap
    return chunks


def _chunk_python(content):
    """
    Splits Python source at function/class boundaries using the ast module,
    so a chunk is always a complete, meaningful unit of code instead of an
    arbitrary character slice. Falls back to line-based chunking if the file
    doesn't parse (e.g. syntax errors) or has no top-level def/class.
    """
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return _chunk_by_lines(content)

    lines = content.splitlines()
    nodes = [
        n for n in tree.body
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    ]

    if not nodes:
        return _chunk_by_lines(content)

    chunks = []
    covered_end = 0

    for node in nodes:
        start = node.lineno - 1
        end = getattr(node, "end_lineno", start + 1)

        # Capture any code between the previous node and this one
        # (imports, module-level constants, etc.) as its own chunk
        if start > covered_end:
            leading = "\n".join(lines[covered_end:start]).strip()
            if leading:
                chunks.append({
                    "content": leading,
                    "start_line": covered_end + 1,
                    "end_line": start,
                })

        block = "\n".join(lines[start:end])

        if len(block) > MAX_CHUNK_CHARS:
            # Huge function/class (rare) — sub-chunk so embeddings stay meaningful
            chunks.extend(_chunk_by_lines(block, base_line=start + 1))
        else:
            chunks.append({
                "content": block,
                "start_line": start + 1,
                "end_line": end,
            })

        covered_end = end

    if covered_end < len(lines):
        trailing = "\n".join(lines[covered_end:]).strip()
        if trailing:
            chunks.append({
                "content": trailing,
                "start_line": covered_end + 1,
                "end_line": len(lines),
            })

    return chunks


def chunk_documents(documents):
    chunked_documents = []

    for document in documents:
        path = document["path"]
        content = document["content"]

        if path.endswith(".py"):
            raw_chunks = _chunk_python(content)
        else:
            raw_chunks = _chunk_by_lines(content)

        for i, chunk in enumerate(raw_chunks):
            if not chunk["content"].strip():
                continue

            chunked_documents.append({
                "path": path,
                "chunk_id": i,
                "content": chunk["content"],
                "start_line": chunk["start_line"],
                "end_line": chunk["end_line"],
            })

    return chunked_documents