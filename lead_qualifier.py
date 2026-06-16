from typing import Dict
import re

# Avoid any network calls/import-time downloads in Lambda.
try:
    import nltk
    from nltk.sentiment import SentimentIntensityAnalyzer
except Exception:  # pragma: no cover
    nltk = None
    SentimentIntensityAnalyzer = None


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


def _build_sentiment_analyzer():
    if SentimentIntensityAnalyzer is None:
        return None
    try:
        # If vader_lexicon is missing, do NOT attempt nltk.download (no internet).
        return SentimentIntensityAnalyzer()
    except LookupError:
        return None


sia = _build_sentiment_analyzer()


LEAD_KEYWORDS = {
    'hot': ['urgent', 'asap', 'ready', 'immediate', 'now', 'today', 'tomorrow', 'budget', '$', 'committed', 'serious'],
    'warm': ['interested', 'looking', 'considering', 'maybe', 'perhaps', 'view'],
    'cold': ['info', 'general', 'brochure']
}

def qualify_lead(lead_text: str) -> Dict[str, any]:
    """
    Qualify Real Estate lead: Hot/Warm/Cold.
    """
    score = 0
    words = lead_text.lower().split()
    
    # Keyword score
    for word in words:
        if any(hot in word for hot in LEAD_KEYWORDS['hot']):
            score += 3
        elif any(warm in word for warm in LEAD_KEYWORDS['warm']):
            score += 2
        elif any(cold in word for cold in LEAD_KEYWORDS['cold']):
            score -= 1
    
    # Sentiment boost
    sent = sia.polarity_scores(lead_text)
    score += sent['compound'] * 2  # Positive intent
    
    # Entities (money/person high score) - only if spacy is available
    entity_count = 0
    if spacy_available and nlp is not None:
        doc = nlp(lead_text.lower())
        if any(ent.label_ in ['MONEY', 'PERSON', 'DATE'] for ent in doc.ents):
            score += 2
        entity_count = len([e for e in doc.ents if e.label_ in ['MONEY','PERSON']])
    
    if score >= 7:
        qual = 'Hot'
    elif score >= 3:
        qual = 'Warm'
    else:
        qual = 'Cold'
    
    return {
        'qualification': qual,
        'score': round(score, 2),
        'reasoning': f"Keyword matches, sentiment {sent['compound']:.2f}, entities: {entity_count}"
    }

if __name__ == "__main__":
    sample_hot = "Ready to buy 3BHK now, budget $600k, call me ASAP."
    print(qualify_lead(sample_hot))

