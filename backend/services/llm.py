import json
import os
import re
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
client = OpenAI(
    base_url=os.getenv("LLM_BASE_URL", "https://api.openai.com/v1"),
    api_key=os.getenv("LLM_API_KEY", "missing"),
    max_retries=0,
    timeout=30,
)

SYSTEM_PROMPT = """You answer questions for shop-floor supervisors using ONLY the numbered excerpts provided.

Rules:
1. If the excerpts do not contain the answer, set found to false. Never use outside knowledge. Never guess numbers, names or steps.
2. Lead with the direct answer in short, plain sentences. Use numbered lines for procedures.
3. Include any condition or exception in the excerpts that changes the answer (who, when, unless).
4. Keep values, units and document numbers exactly as written.
5. If excerpts disagree, say so instead of picking one.

Reply with JSON only: {"found": true or false, "answer": "text", "used": [numbers of the excerpts you relied on]}"""


def build_context(hits):
    blocks = []
    for number, (chunk, _) in enumerate(hits, start=1):
        header = f"[{number}] {chunk['doc_no']} Rev {chunk['rev']:02d}, {chunk['section']}, page {chunk['page']}"
        blocks.append(f"{header}\n{chunk['body']}")
    return "\n\n".join(blocks)


def parse_json(text):
    try:
        return json.loads(text)
    except (TypeError, json.JSONDecodeError):
        match = re.search(r"\{.*\}", text or "", re.DOTALL)
        if not match:
            raise ValueError("The model did not return JSON")
        return json.loads(match.group(0))


def ask_llm(question, hits):
    response = client.chat.completions.create(
        model=MODEL,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Excerpts:\n\n{build_context(hits)}\n\nQuestion: {question}",
            },
        ],
    )
    return parse_json(response.choices[0].message.content)
