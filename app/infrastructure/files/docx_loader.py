from docx import Document


def load_docx_text(file_path: str) -> str:
    doc = Document(file_path)
    text_chunks: list[str] = []

    for para in doc.paragraphs:
        line = para.text.strip()
        if line:
            text_chunks.append(line)

    return "\n".join(text_chunks)
