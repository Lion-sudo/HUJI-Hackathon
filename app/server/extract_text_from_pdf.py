import fitz  # PyMuPDF

###### 1. EXTRACT THE TEXT ######
def extract_pdf_text(path):
    doc = fitz.open(path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text


###### 2. CHUNK THE TEXT ######
def chunk_text(text, max_length=1000, overlap=200):
    chunks = []
    start = 0
    while start < len(text):
        end = start + max_length
        chunks.append(text[start:end])
        start += max_length - overlap
    return chunks

###### 3. EMBEDD THE CHUNKS ######
from sentence_transformers import SentenceTransformer

embedder = SentenceTransformer('all-MiniLM-L6-v2')

def embed_chunks(chunks):
    return embedder.encode(chunks)


###### 4. STORE IN VECTOR DATA BASE ######

import faiss
import numpy as np

def create_faiss_index(embeddings):
    dim = len(embeddings[0])
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings).astype('float32'))
    return index