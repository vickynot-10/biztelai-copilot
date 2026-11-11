import re
from services.llm import ask_llm
from services.retrieval import documents, search

SAFETY_RE = re.compile(
    r"lock\s?out|tag\s?out|\bloto\b|isolat|de-?energi|stored (energy|pressure)|zero energy|accumulator",
    re.IGNORECASE,
)


def not_found():
    return {
        "found": False,
        "answer": "",
        "sources": [],
        "safety_critical": False,
        "version_notes": [],
    }


def version_notes(used_chunks):
    notes = []
    seen = set()
    for chunk in used_chunks:
        if chunk["doc_no"] in seen:
            continue
        seen.add(chunk["doc_no"])
        for document in documents:
            if (
                document["doc_no"] == chunk["doc_no"]
                and document["status"] == "superseded"
            ):
                notes.append(
                    f"{chunk['doc_no']}: this answer is from Rev {chunk['rev']:02d} (effective {chunk['effective_date']}). "
                    f"Rev {document['rev']:02d} is superseded, so don't follow old printed copies."
                )
    return notes


def build_source(chunk):
    return {
        "doc_no": chunk["doc_no"],
        "rev": f"{chunk['rev']:02d}",
        "title": chunk["title"],
        "section": chunk["section"],
        "page": chunk["page"],
        "page_end": chunk["page_end"],
        "passage": chunk["body"],
        "pdf_url": f"/pdfs/{chunk['file']}#page={chunk['page']}",
    }


def is_safety_critical(question, used_chunks):
    if SAFETY_RE.search(question):
        return True
    return any(
        chunk["doc_no"].startswith("SAF") or SAFETY_RE.search(chunk["body"])
        for chunk in used_chunks
    )


def process_request(question):
    hits = search(question)
    best = hits[0][1] if hits else 0.0
    print(f"[ask] best_score={best:.2f} question={question!r}")
    if not hits:
        return not_found()

    result = ask_llm(question, hits)
    if not result.get("found"):
        return not_found()

    numbers = [
        n for n in result.get("used", []) if isinstance(n, int) and 1 <= n <= len(hits)
    ] or [1]
    used_chunks = [hits[n - 1][0] for n in dict.fromkeys(numbers)]
    return {
        "found": True,
        "answer": result.get("answer", "").strip(),
        "sources": [build_source(chunk) for chunk in used_chunks],
        "safety_critical": is_safety_critical(question, used_chunks),
        "version_notes": version_notes(used_chunks),
    }
