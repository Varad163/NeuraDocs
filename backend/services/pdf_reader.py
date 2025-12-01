from pypdf import PdfReader
from io import BytesIO

def extract_text_from_pdf(pdf_bytes: bytes):
    reader = PdfReader(BytesIO(pdf_bytes))
    full_text = ""

    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            full_text += extracted + "\n"

    return full_text
