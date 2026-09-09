import json
import re
from pathlib import Path

# ==========================
# Configuration
# ==========================

DATA_FOLDER = Path("data")

CHUNK_SIZE = 500        # words
OVERLAP = 75            # words


# ==========================
# Helper Functions
# ==========================

def chunk_text(text, page_start, page_end):
    """
    Split parent text into child chunks.
    """

    words = text.split()

    children = []

    child_id = 1

    start = 0

    while start < len(words):

        end = start + CHUNK_SIZE

        chunk = " ".join(words[start:end])

        children.append({
            "child_id": child_id,
            "chunk_index": child_id,
            "page_start": page_start,
            "page_end": page_end,
            "word_count": len(chunk.split()),
            "text": chunk
        })

        child_id += 1

        start += CHUNK_SIZE - OVERLAP

    return children


# Detect headings like:
# 1 Introduction
# 2 Scope of Work
# 10 Eligibility
TOP_LEVEL = re.compile(r'^\d+\s+.+')

PAGE_MARKER = re.compile(r'^# Page (\d+)')


# ==========================
# Process Every Tender
# ==========================

for tender in sorted(DATA_FOLDER.iterdir()):

    if not tender.is_dir():
        continue

    md_files = list(tender.glob("*.md"))

    if not md_files:
        print(f"No markdown found in {tender.name}")
        continue

    md_path = md_files[0]

    print(f"\nProcessing {md_path.name}")

    with open(md_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    parents = []

    current_title = None
    current_text = []

    parent_id = 1

    current_page = 1
    page_start = 1

    # --------------------------

    for line in lines:

        line = line.rstrip()

        # Page Marker

        page_match = PAGE_MARKER.match(line)

        if page_match:

            current_page = int(page_match.group(1))
            continue

        # Top Level Heading

        if TOP_LEVEL.match(line):

            # Save previous parent

            if current_title is not None:

                parent_text = "\n".join(current_text).strip()

                parents.append({

                    "parent_id": parent_id,

                    "title": current_title,

                    "page_start": page_start,

                    "page_end": current_page,

                    "text": parent_text,

                    "children": chunk_text(
                        parent_text,
                        page_start,
                        current_page
                    )

                })

                parent_id += 1

            # Start new parent

            current_title = line

            current_text = []

            page_start = current_page

        else:

            current_text.append(line)

    # Save Last Parent

    if current_title is not None:

        parent_text = "\n".join(current_text).strip()

        parents.append({

            "parent_id": parent_id,

            "title": current_title,

            "page_start": page_start,

            "page_end": current_page,

            "text": parent_text,

            "children": chunk_text(
                parent_text,
                page_start,
                current_page
            )

        })

    # ==========================
    # Output JSON
    # ==========================

    output = {

        "document": md_path.stem,

        "total_parents": len(parents),

        "parents": parents

    }

    output_file = tender / "parent_child.json"

    with open(output_file, "w", encoding="utf-8") as f:

        json.dump(
            output,
            f,
            indent=4,
            ensure_ascii=False
        )

    print(f"Parents : {len(parents)}")

print("\nAll tenders processed successfully.")