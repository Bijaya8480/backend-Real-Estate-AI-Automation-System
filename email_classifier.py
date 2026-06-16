import re
from typing import Dict

# Avoid any network calls/import-time downloads in Lambda.
# NLTK corpora may be unavailable in serverless environments.
try:
    import nltk
    from nltk.corpus import stopwords
except Exception:  # pragma: no cover
    nltk = None
    stopwords = None

# Try to import spacy, but make it optional
try:
    import spacy

    spacy_available = True
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        spacy_available = False
        nlp = None
except Exception:
    spacy_available = False
    nlp = None


def _load_stop_words() -> set[str]:
    if stopwords is None:
        return set()
    try:
        # If corpus is missing, do NOT attempt nltk.download (no internet).
        # Instead, fall back to empty set.
        return set(stopwords.words("english"))
    except LookupError:
        return set()


stop_words = _load_stop_words()


CATEGORIES = {
    'Sales': ['property', 'house', 'apartment', 'viewing', 'buy', 'rent', 'bhk', 'square', 'price', 'offer', 'deal', 'buyer', 'seller'],
    'Support': ['maintenance', 'repair', 'issue', 'complaint', 'leak', 'problem', 'tenant', 'landlord'],
    'Finance': ['payment', 'invoice', 'rent due', 'bill', 'refund', 'fee'],
    'HR': ['job', 'resume', 'interview', 'employee', 'vacancy', 'agent'],
    'Spam': ['free', 'win', 'click', 'urgent loan']
}

def classify_email(email_text: str) -> Dict[str, str]:
    """
    Classify Real Estate email.
    """
    scores = {cat: 0 for cat in CATEGORIES}
    
    # Keyword scoring
    words = re.findall(r'\\b\\w+\\b', email_text.lower())
    filtered = [w for w in words if w not in stop_words]
    
    for word in filtered:
        for cat, keywords in CATEGORIES.items():
            if any(kw in word for kw in keywords):
                scores[cat] += 1
    
    # NER boost (only if spacy is available)
    if spacy_available and nlp is not None:
        doc = nlp(email_text.lower())
        for ent in doc.ents:
            if ent.label_ in ['MONEY', 'ORG', 'PERSON']:
                scores['Sales'] += 1  # Likely lead
    
    top_cat = max(scores, key=scores.get)
    
    confidence = scores[top_cat] / max(1, len(filtered))
    
    return {
        'category': top_cat,
        'confidence': f"{confidence:.2f}",
        'scores': scores
    }

# Demo
if __name__ == "__main__":
    sample_sales = "Interested in viewing the 2BHK apartment. Budget 500k. Can we schedule?"
    print(classify_email(sample_sales))

