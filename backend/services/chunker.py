def chunk_text(text, chunk_size=800):
    words = text.split()
    chunks = []
    current = []

    for word in words:
        if len(" ".join(current + [word])) > chunk_size:
            chunks.append(" ".join(current))
            current = [word]
        else:
            current.append(word)

    if current:
        chunks.append(" ".join(current))

    return chunks
