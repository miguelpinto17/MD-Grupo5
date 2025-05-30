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

screening_terms = [
    "blood test", "cholesterol test", "fasting glucose test", "cancer screening", "colonoscopy",
    "mammogram", "pap smear", "prostate exam", "psa test", "bone density scan",
    "abdominal ultrasound", "chest x-ray", "eye screening", "hearing test", "skin cancer screening",
    "lung cancer screening", "cervical cancer screening", "stool test", "fecal occult blood test",
    "ct colonography", "breast ultrasound", "digital rectal exam", "thyroid screening",
    "hepatitis screening", "hiv test", "std screening", "cardiac stress test", "electrocardiogram",
    "retinal screening", "spirometry test"
]

preventive_care_terms = [
    "medical check-up", "annual physical", "routine exam", "wellness visit", "preventive care visit",
    "comprehensive health assessment", "baseline health evaluation", "occupational health check",
    "pre-employment screening", "post-travel medical review", "health counseling session",
    "lifestyle assessment", "nutritional evaluation", "risk factor analysis", "general physical exam",
    "age-specific screening", "adolescent health check", "men's health exam", "women's health exam",
    "geriatric assessment", "preventive medicine visit", "student health assessment",
    "workplace health assessment", "driver medical examination", "military physical",
    "sports clearance exam", "school entry physical", "immigration medical exam",
    "chronic disease follow-up", "early intervention assessment"
]

vaccination_terms = [
    "vaccination", "flu shot", "influenza vaccine", "covid-19 vaccine", "hepatitis b vaccine",
    "hepatitis a vaccine", "measles vaccine", "mumps vaccine", "rubella vaccine", "varicella vaccine",
    "tdap vaccine", "tetanus shot", "diphtheria vaccine", "polio vaccine", "meningitis vaccine",
    "pneumococcal vaccine", "shingles vaccine", "hpv vaccine", "rabies vaccine", "yellow fever vaccine",
    "typhoid vaccine", "bcg vaccine", "japanese encephalitis vaccine", "malaria prophylaxis",
    "booster dose", "childhood immunization", "travel vaccinations", "vaccine catch-up schedule",
    "immunization record", "post-exposure prophylaxis"
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

screening_terms = set(normalize_text(term) for term in screening_terms)
preventive_care_terms = set(normalize_text(term) for term in preventive_care_terms)
vaccination_terms = set(normalize_text(term) for term in vaccination_terms)

# Function to create a PhraseMatcher
def create_matcher(nlp, terms):
    """Creates a PhraseMatcher with normalized terms."""
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")  # Case-insensitive matching
    patterns = [nlp.make_doc(term) for term in terms]
    matcher.add("TERM_MATCHER", patterns)
    return matcher

screening_matcher = create_matcher(nlp, screening_terms)
preventive_care_matcher = create_matcher(nlp, preventive_care_terms)
vaccination_matcher = create_matcher(nlp, vaccination_terms)

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
        
        "SCREENING": [doc[start:end].text for _, start, end in screening_matcher(doc)],
        "PREVENTIVE_CARE": [doc[start:end].text for _, start, end in preventive_care_matcher(doc)],
        "VACCINATION": [doc[start:end].text for _, start, end in vaccination_matcher(doc)]
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
    Divide o texto em vários chunks de até max_words palavras, respeitando os limites de frases.
    Retorna uma lista de strings (chunks).
    """
    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents]

    chunks = []
    current_chunk = ""
    word_count = 0

    for sentence in sentences:
        sentence_word_count = len(sentence.split())

        # Se a frase sozinha excede max_words, corta-a à força
        if sentence_word_count > max_words:
            words = sentence.split()
            for i in range(0, len(words), max_words):
                chunks.append(" ".join(words[i:i + max_words]))
            continue

        if word_count + sentence_word_count > max_words:
            chunks.append(current_chunk.strip())
            current_chunk = sentence
            word_count = sentence_word_count
        else:
            current_chunk += " " + sentence
            word_count += sentence_word_count

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks
