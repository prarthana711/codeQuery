# Rules for deciding what's worth reading during ingestion.

CODE_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx",
    ".java", ".go", ".rb", ".php", ".c", ".cpp", ".h",
    ".md", ".txt", ".rst", ".json", ".yaml", ".yml",
}

EXCLUDE_DIRS = {
    "node_modules", ".git", "venv", ".venv", "__pycache__",
    "dist", "build", ".next", ".vscode", ".idea",
    "coverage", "target", "vendor", "repositories",
}

# Skip files bigger than this — usually generated/minified/vendored, not
# useful for Q&A and wasteful to embed
MAX_FILE_SIZE = 200_000  # ~200 KB


def should_include_dir(dirname: str) -> bool:
    return dirname not in EXCLUDE_DIRS and not dirname.startswith(".")


def should_include_file(filepath: str) -> bool:
    filename = filepath.rsplit("/", 1)[-1]
    if "." not in filename:
        return False
    ext = "." + filename.rsplit(".", 1)[-1]
    return ext.lower() in CODE_EXTENSIONS