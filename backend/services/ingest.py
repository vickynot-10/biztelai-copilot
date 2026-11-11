import re
from pathlib import Path
import pymupdf

FOLDER = Path(__file__).parent.parent / "data"

META_RE = re.compile(r"(\S+)\s*\|\s*Rev (\d+)")
EFFECTIVE_RE = re.compile(r"Effective Date\s+(\d{2}-\w{3}-\d{4})")
HEADER_RE = re.compile(r"^\S+\s*\|\s*Rev \d+\s*\|\s*Uncontrolled")
PAGE_RE = re.compile(r"^Page \d+$")
HEADING_RE = re.compile(r"^(\d+)\.\s+(.*)$")


def read_meta(doc):
    text = doc[0].get_text()
    meta_match = META_RE.search(text)
    date_match = EFFECTIVE_RE.search(text)
    return {
        "doc_no": meta_match.group(1),
        "rev": int(meta_match.group(2)),
        "effective_date": date_match.group(1) if date_match else "",
    }


def read_lines(page, page_number):
    lines = []
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            text = "".join(span["text"] for span in line["spans"]).strip()
            if not text or HEADER_RE.match(text) or PAGE_RE.match(text):
                continue
            first = line["spans"][0]
            lines.append(
                {
                    "text": text,
                    "size": first["size"],
                    "bold": bool(first["flags"] & 16),
                    "y": round(line["bbox"][1]),
                    "page": page_number,
                }
            )
    return lines


def merge_rows(lines):
    rows = []
    for line in lines:
        previous = rows[-1] if rows else None
        same_row = (
            previous
            and previous["page"] == line["page"]
            and abs(previous["y"] - line["y"]) <= 2
            and not previous["bold"]
            and not line["bold"]
        )
        if same_row:
            previous["text"] = f"{previous['text']} | {line['text']}"
        else:
            rows.append(dict(line))
    return rows


def read_all_lines(doc):
    all_lines = []
    for page_number, page in enumerate(doc, start=1):
        all_lines.extend(read_lines(page, page_number))
    return merge_rows(all_lines)


def read_title(lines):
    for line in lines:
        if line["bold"] and line["size"] >= 14:
            return line["text"]
    return ""


def has_heading_style(line):
    return line["bold"] and 11.5 <= line["size"] < 14


def is_heading(line):
    return has_heading_style(line) and HEADING_RE.match(line["text"]) is not None


def new_section(heading, page):
    return {"heading": heading, "page": page, "page_end": page, "body": []}


def split_sections(lines):
    sections = []
    current = new_section("Document details", 1)
    after_heading = False
    for line in lines:
        if is_heading(line):
            sections.append(current)
            current = new_section(line["text"], line["page"])
            after_heading = True
        elif after_heading and has_heading_style(line):
            current["heading"] = f"{current['heading']} {line['text']}"
        else:
            if not current["body"]:
                current["page"] = line["page"]
            after_heading = False
            current["body"].append(line["text"])
            current["page_end"] = line["page"]
    sections.append(current)
    return sections


def mark_status(documents):
    latest = {}
    for document in documents:
        doc_no = document["doc_no"]
        latest[doc_no] = max(latest.get(doc_no, 0), document["rev"])
    for document in documents:
        is_latest = document["rev"] == latest[document["doc_no"]]
        document["status"] = "current" if is_latest else "superseded"


def load_corpus():
    documents = []
    for pdf_file in sorted(FOLDER.glob("*.pdf")):
        doc = pymupdf.open(pdf_file)
        try:
            meta = read_meta(doc)
        except AttributeError:
            print("skipped (no revision header):", pdf_file.name)
            continue
        lines = read_all_lines(doc)
        documents.append(
            {
                "file": pdf_file.name,
                "title": read_title(lines),
                "sections": split_sections(lines),
                **meta,
            }
        )
    mark_status(documents)

    chunks = []
    for document in documents:
        for section in document["sections"]:
            body = "\n".join(section["body"])
            chunks.append(
                {
                    "file": document["file"],
                    "doc_no": document["doc_no"],
                    "rev": document["rev"],
                    "title": document["title"],
                    "effective_date": document["effective_date"],
                    "status": document["status"],
                    "section": section["heading"],
                    "page": section["page"],
                    "page_end": section["page_end"],
                    "body": body,
                    "search_text": f"{document['doc_no']} {document['title']} {section['heading']} {body}",
                }
            )
    return documents, chunks


if __name__ == "__main__":
    documents, chunks = load_corpus()
    print(len(documents), "documents,", len(chunks), "chunks")
    for chunk in chunks:
        print(
            f"{chunk['doc_no']} Rev{chunk['rev']} {chunk['status']:10} p{chunk['page']}-{chunk['page_end']}  {chunk['section'][:50]}"
        )
