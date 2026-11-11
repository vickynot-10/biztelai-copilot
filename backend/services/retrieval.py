import re
from rank_bm25 import BM25Okapi
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from services.ingest import load_corpus

MIN_SCORE = 3.0
TOP_K = 4

TOKEN_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
KEEP_WORDS = {
    "system",
    "call",
    "full",
    "top",
    "part",
    "move",
    "front",
    "side",
    "found",
    "show",
    "all",
}
STOPWORDS = set(ENGLISH_STOP_WORDS) - KEEP_WORDS

documents, chunks = load_corpus()


def tokenize(text):
    return [word for word in TOKEN_RE.findall(text.lower()) if word not in STOPWORDS]


index = BM25Okapi([tokenize(chunk["search_text"]) for chunk in chunks])


def search(question, top_k=TOP_K):
    scores = index.get_scores(tokenize(question))
    ranked = [
        (chunk, float(score))
        for chunk, score in zip(chunks, scores)
        if chunk["status"] == "current"
    ]
    ranked.sort(key=lambda pair: pair[1], reverse=True)
    if not ranked or ranked[0][1] < MIN_SCORE:
        return []
    return ranked[:top_k]


if __name__ == "__main__":
    questions = [
        "What is the recommended coolant concentration for the TX-200 CNC turning centre?",
        "The machine is showing alarm AL-104. What does it mean and what should the operator do?",
        "Who is allowed to remove a lockout lock from a machine?",
        "What is the outer diameter tolerance for the BH-220 bearing housing?",
        "How often should spindle runout be checked, and who does it?",
        "A lot of 120 pieces has one minor defect. Accept or reject?",
        "What is the maximum spindle speed of the TX-200?",
        "What PPE is required when applying a lockout lock?",
    ]
    for question in questions:
        print(question)
        results = search(question)
        if not results:
            print("   (no match, would answer: not in the documents)")
        for chunk, score in results:
            print(
                f"   {score:6.2f}  {chunk['doc_no']} Rev{chunk['rev']}  {chunk['section'][:45]}"
            )
