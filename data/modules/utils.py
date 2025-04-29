import json
import os
from Bio import Entrez
from dotenv import load_dotenv

def configure_entrez():
    load_dotenv()
    email = os.getenv("EMAIL")
    api_key = os.getenv("API_KEY_PUBMED")

    if not email:
        raise ValueError("Missing EMAIL in .env file.")

    Entrez.email = email
    if api_key:
        Entrez.api_key = api_key

def load_keywords(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def save_results_to_json(data, filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"\n📦 Saved {len(data)} articles to {filename}")
