import fitz  # PyMuPDF
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

class PDFRag:
    def __init__(self, pdf_path, chunk_size=1000, overlap=200):
        self.pdf_path = pdf_path
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

        self.text = self._extract_pdf_text()
        self.chunks = self._chunk_text()
        self.embeddings = self._embed_chunks()
        self.index = self._create_faiss_index()

    def _extract_pdf_text(self):
        doc = fitz.open(self.pdf_path)
        return "".join(page.get_text() for page in doc)

    def _chunk_text(self):
        chunks = []
        start = 0
        while start < len(self.text):
            end = min(len(self.text), start + self.chunk_size)
            chunks.append(self.text[start:end])
            start += self.chunk_size - self.overlap
        return chunks

    def _embed_chunks(self):
        return self.model.encode(self.chunks, convert_to_numpy=True)

    def _create_faiss_index(self):
        dim = self.embeddings.shape[1]
        index = faiss.IndexFlatL2(dim)
        index.add(self.embeddings)
        return index

    def get_rag_context(self, prompt, num_chunks=5):
        prompt_vec = self.model.encode([prompt])[0].astype('float32').reshape(1, -1)
        _, indices = self.index.search(prompt_vec, num_chunks)
        return [self.chunks[i] for i in indices[0]]
