from pymongo import MongoClient
from tqdm import tqdm
from modules.spaCy_utils import chunk_text

def configure_mongoDB_connection():
    """Configure MongoDB connection."""
    client = MongoClient("mongodb://localhost:27017/")  
    db = client["preventive_checkups_agent"]  
    collection = db["papers"] 
    return collection





def save_to_mongo(papers, source, topic):
    """Save articles to MongoDB in chunked format with dynamic topic."""
    if not papers:
        print("No articles to save.")
        return

    collection = configure_mongoDB_connection()
    chunk_limit = 150  

    for idx, paper in enumerate(tqdm(papers, desc=f"Saving {source} articles to MongoDB")):
        title = paper.get("title", "")
        abstract = paper.get("abstract", "") or paper.get("abstractText", "")
        year = str(paper.get("year", ""))
        link = paper.get("doi", "") or paper.get("externalIds", {}).get("DOI", "")
        if link and not link.startswith("http"):
            link = f"https://doi.org/{link}"
        if not link:
            link = paper.get("pub_url", "") or paper.get("url", "") or "No link available"

        if not abstract.strip():
            continue

        # ➕ Alteração aqui: múltiplos chunks
        chunks = chunk_text(abstract, max_words=chunk_limit)

        for chunk_idx, chunk in enumerate(chunks):
            doc = {
                "chunk_id": f"Paper{idx + 1}Chunk{chunk_idx}",
                "chunk_text": chunk,
                "title": title,
                "link": link,
                "year": year,
                "topic": topic,
                "hierarchical_level": 2
            }
            collection.insert_one(doc)

    print("All chunked articles have been saved with the required structure!")

