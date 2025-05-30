import os
import fitz  # PyMuPDF
from tqdm import tqdm
from pymongo import MongoClient
from modules.spaCy_utils import chunk_text
from modules.mongoDB_utils import configure_mongoDB_connection

def extract_text_from_pdf(pdf_path):
    """Extrai todo o texto de um PDF usando PyMuPDF."""
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text.strip()

def save_pdfs_to_mongodb(input_folder, topic, chunk_limit=150):
    """Processa todos os PDFs de uma pasta e salva no MongoDB com hierarchical_level=1."""
    collection = configure_mongoDB_connection()
    pdf_files = [f for f in os.listdir(input_folder) if f.endswith(".pdf")]

    for idx, filename in enumerate(tqdm(pdf_files, desc="Importing PDFs to MongoDB")):
        file_path = os.path.join(input_folder, filename)
        title = os.path.splitext(filename)[0]
        text = extract_text_from_pdf(file_path)

        if not text:
            continue

        chunks = chunk_text(text, max_words=chunk_limit)

        for chunk_idx, chunk in enumerate(chunks):
            doc = {
                "chunk_id": f"{title}_Chunk{chunk_idx}",
                "chunk_text": chunk,
                "title": title,
                "link": "Local PDF",
                "year": "",  # ou extraído do título se quiseres
                "topic": topic,
                "hierarchical_level": 1
            }
            collection.insert_one(doc)

    print("Todos os PDFs foram importados com hierarchical_level = 1.")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Import PDF files into MongoDB with hierarchical_level=1.")
    parser.add_argument("--folder", required=True, help="Pasta onde estão os PDFs")
    parser.add_argument("--topic", required=True, help="Tópico geral (ex: check-up)")
    parser.add_argument("--chunk_limit", type=int, default=150, help="Máximo de palavras por chunk (default=150)")

    args = parser.parse_args()

    save_pdfs_to_mongodb(
        input_folder=args.folder,
        topic=args.topic,
        chunk_limit=args.chunk_limit
    )