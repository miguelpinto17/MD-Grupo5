import json
import os
import time
from Bio import Entrez
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def configure_entrez():
    email = os.getenv("EMAIL")
    api_key = os.getenv("API_KEY_PUBMED")

    if not email:
        raise ValueError("Missing EMAIL in environment variables.")

    Entrez.email = email
    if api_key:
        Entrez.api_key = api_key

def load_keywords(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("categories", {})

def fetch_papers(id_list):
    if not id_list:
        return []

    with Entrez.efetch(db="pubmed", id=",".join(id_list), rettype="abstract", retmode="xml") as handle:
        records = Entrez.read(handle)

    results = []
    for article in records.get("PubmedArticle", []):
        medline = article.get("MedlineCitation", {})
        article_data = medline.get("Article", {})

        title = article_data.get("ArticleTitle", "No Title Available")
        article_date = article_data.get("ArticleDate", [])
        if article_date:
            year = article_date[0].get("Year", "No Year Available")
        else:
            year = "No Year Available"
        abstract_data = article_data.get("Abstract", {}).get("AbstractText", ["No Abstract"])
        abstract = " ".join(abstract_data) if isinstance(abstract_data, list) else str(abstract_data)

        authors = [
            f"{author.get('ForeName', '')} {author.get('LastName', '')}".strip()
            for author in article_data.get("AuthorList", [])
            if "ForeName" in author and "LastName" in author
        ]

        journal = article_data.get("Journal", {}).get("Title", "No Journal Info")
        elocation_ids = article_data.get("ELocationID", [])
        doi = next((eid for eid in elocation_ids if eid.attributes.get("EIdType") == "doi"), "No DOI")

        results.append({
            "title": title,
            "year": year,
            "abstract": abstract,
            "authors": authors,
            "journal": journal,
            "doi": doi
        })

    return results

def search_pubmed(query, num_results=50, year_range=(2019, 3000)):
    if year_range:
        start_year, end_year = year_range
        query += f" AND ({start_year}[PDAT] : {end_year}[PDAT])"

    with Entrez.esearch(db="pubmed", term=query, retmax=num_results, sort="relevance") as handle:
        record = Entrez.read(handle)

    return record.get("IdList", [])

def fetch_all_pubmed_abstracts(keywords):
    all_articles = []
    for topic, words in keywords.items():
        for word in words:
            print(f"\n🔍 Fetching articles for: {word} (Topic: {topic})")
            id_list = search_pubmed(word)
            if not id_list:
                print(f"No articles found for {word}")
                continue
            articles = fetch_papers(id_list)
            for article in articles:
                article["topic"] = topic
                all_articles.append(article)
            time.sleep(1)
    return all_articles

def save_results_to_json(articles, filename="../JSON/pubmed_results.json"):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(articles, file, ensure_ascii=False, indent=4)
    print(f"\n📦 Saved {len(articles)} articles to {filename}")

if __name__ == "__main__":
    configure_entrez()
    keywords = load_keywords("../JSON/keywords.json")
    articles = fetch_all_pubmed_abstracts(keywords)
    save_results_to_json(articles)
