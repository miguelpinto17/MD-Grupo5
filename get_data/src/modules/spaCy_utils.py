import spacy
from spacy.matcher import PhraseMatcher
import re

# Load the SciBERT model from spaCy
nlp = spacy.load("en_core_sci_scibert")

# Function to normalize text
def normalize_text(text):
    """
    Normalizes text: removes punctuation, extra spaces, and converts to lowercase.
    """
    text = text.lower()  # Convert to lowercase
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    text = re.sub(r'\s+', ' ', text)  # Remove extra spaces
    return text.strip()

preventive_terms = [
    "medical check-up", "annual physical", "preventive screening", "blood test",
    "cholesterol test", "blood pressure monitoring", "cancer screening",
    "health risk assessment", "vaccination", "routine exam", "wellness visit",
    "preventive care", "colonoscopy", "mammogram", "pap smear", "check-up"
]

'''
# Lists of biomedical terms (diseases, supplements, pharmaceuticals, and medical concepts)
disease_terms = [
    "cardiovascular diseases", "cancer", "diabetes", "hypertension", "obesity", 
    "asthma", "alzheimer's disease", "parkinson's disease", "rheumatoid arthritis", 
    "osteoporosis", "stroke", "copd", "depression", "anxiety", "insomnia", "migraine", 
    "epilepsy", "ibd", "hepatitis", "tuberculosis", "malaria", "hiv/aids", "mental health disorders", "disease prevention"
]

supplement_terms = [
    "vitamin c", "vitamin d", "vitamin e", "vitamin b12", "calcium", "magnesium", 
    "omega-3 fatty acids", "probiotics", "fiber", "zinc", "iron", "turmeric", 
    "coenzyme q10", "glucosamine", "chondroitin", "ginseng", "echinacea", "green tea extract", 
    "garcinia cambogia", "spirulina", "aloe vera", "ashwagandha", "l-carnitine", "resveratrol", 
    "melatonin", "elderberry", "fish oil", "flaxseed oil", "beta-glucan", "biotin", "collagen", "nutritional supplements"
]

pharmaceutical_terms = [
    "aspirin", "paracetamol", "ibuprofen", "metformin", "atorvastatin", 
    "omeprazole", "simvastatin", "amlodipine", "losartan", "metoprolol"
]

medical_concept_terms = [
    "immune function", "oxidative stress", "antioxidant properties", "cellular health", "immune response"
]

# Normalize all terms
disease_terms = set(normalize_text(term) for term in disease_terms)
supplement_terms = set(normalize_text(term) for term in supplement_terms)
pharmaceutical_terms = set(normalize_text(term) for term in pharmaceutical_terms)
medical_concept_terms = set(normalize_text(term) for term in medical_concept_terms)

'''

preventive_terms = set(normalize_text(term) for term in preventive_terms)


# Function to create a PhraseMatcher
def create_matcher(nlp, terms):
    """Creates a PhraseMatcher with normalized terms."""
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")  # Case-insensitive matching
    patterns = [nlp.make_doc(term) for term in terms]
    matcher.add("TERM_MATCHER", patterns)
    return matcher
'''
# Create matchers for diseases, supplements, pharmaceuticals, and medical concepts
disease_matcher = create_matcher(nlp, disease_terms)
supplement_matcher = create_matcher(nlp, supplement_terms)
pharmaceutical_matcher = create_matcher(nlp, pharmaceutical_terms)
medical_concept_matcher = create_matcher(nlp, medical_concept_terms)
'''

preventive_matcher = create_matcher(nlp, preventive_terms)

# Function to process the text and extract entities and corresponding terms
def process_text(text):
    """Processes the text and extracts entities and corresponding terms."""
    # Normalize the input text
    normalized_text = normalize_text(text)
    doc = nlp(normalized_text)

    # Extract named entities (NER)
    entities = [(ent.text, ent.label_) for ent in doc.ents]

    # Extract matched terms
    matches = {
        '''
        "DISEASE": [doc[start:end].text for _, start, end in disease_matcher(doc)],
        "SUPPLEMENT": [doc[start:end].text for _, start, end in supplement_matcher(doc)],
        "PHARMACEUTICAL": [doc[start:end].text for _, start, end in pharmaceutical_matcher(doc)],
        "MEDICAL_CONCEPT": [doc[start:end].text for _, start, end in medical_concept_matcher(doc)]
        '''
        
        "PREVENTIVE": [doc[start:end].text for _, start, end in preventive_matcher(doc)]
    }

    # Categorize entities with priority
    categorized_entities = []
    for ent_text, ent_label in entities:
        for category, matched_terms in matches.items():
            if ent_text in matched_terms:
                categorized_entities.append((ent_text, category))
                break

    return {
        "entities": categorized_entities,
        "matched_terms": matches
    }

def chunk_text(text, max_words=150):
    """
    Retorna um único chunk de texto com até max_words palavras, sem cortar frases a meio.
    """
    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents]

    chunk = ""
    word_count = 0

    for sentence in sentences:
        sentence_word_count = len(sentence.split())
        if word_count + sentence_word_count > max_words:
            break
        chunk += " " + sentence
        word_count += sentence_word_count

    return chunk.strip()
