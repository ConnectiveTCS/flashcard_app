import io
from pdfminer.high_level import extract_text as pdf_extract
from docx import Document
import tiktoken

def extract_text(file_storage):
    """Detect extension, extract & return plain text."""
    name = file_storage.filename.lower()
    data = file_storage.read()
    if name.endswith(".pdf"):
        return pdf_extract(io.BytesIO(data))
    elif name.endswith(".docx"):
        doc = Document(io.BytesIO(data))
        return "\n".join(p.text for p in doc.paragraphs)
    else:
        raise ValueError("Unsupported file type")

def chunk_text(text, max_tokens=3000):
    """Split `text` into chunks of approx <= max_tokens tokens."""
    encoder = tiktoken.encoding_for_model("gpt-4o-mini")
    words = text.split()
    chunks, current = [], []
    count = 0
    for w in words:
        toks = len(encoder.encode(w + " "))
        if count + toks > max_tokens:
            chunks.append(" ".join(current))
            current, count = [], 0
        current.append(w)
        count += toks
    if current:
        chunks.append(" ".join(current))
    return chunks