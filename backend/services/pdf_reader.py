from pypdf import PdfReader

def extract_text_from_pdg(file):
    reader= PdfReader(file)
    text=""

    for page in reader.pages:
        text+=page.extract_xform_text()
        return text