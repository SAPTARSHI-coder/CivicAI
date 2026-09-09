import json
from pathlib import Path

# -------- CHANGE THIS EACH TIME--------
JSON_PATH = Path("data/pmkisan/data/pmkisan/Operational Guidelines of Financing Facility under Agriculture Infrastructure Fund.pdf")
# -----------------------------

CHUNK_SIZE = 500
OVERLAP = 75

with open(JSON_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

chunks = []

chunk_id = 1

for page in data["pages"]:

    words = page["text"].split()

    start = 0

    while start < len(words):

        end = start + CHUNK_SIZE

        chunk_text = " ".join(words[start:end])

        chunks.append({
            "chunk_id": chunk_id,
            "page": page["page"],
            "text": chunk_text
        })

        chunk_id += 1

        start += CHUNK_SIZE - OVERLAP

output = {
    "document": data["document"],
    "total_chunks": len(chunks),
    "chunks": chunks
}

output_path = JSON_PATH.parent / "chunks.json"

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=4, ensure_ascii=False)

print(f"Chunks created: {len(chunks)}")
print(f"Saved: {output_path}")