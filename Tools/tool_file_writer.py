import os

def save_text_file(filename: str, content: str) -> dict:
    """Save text content to a file inside the generated_files folder"""
    os.makedirs("generated_files", exist_ok=True)
    path = f"generated_files/{filename}"
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return {"status": "success", "path": path}
