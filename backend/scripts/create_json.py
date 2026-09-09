import json
from pathlib import Path

# -------- CHANGE THIS FOR EACH FILE --------
MD_PATH = Path("data/pmkisan/data/pmkisan/Operational Guidelines of Financing Facility under Agriculture Infrastructure Fund.pdf")
# --------------------------------------------

print(f"Reading: {MD_PATH.name}")

with open(MD_PATH, "r", encoding="utf-8") as f:
    lines = f.readlines()

pages = []
current_page = None
content = []

for line in lines:
    line = line.rstrip()

    # Detect page markers
    if line.startswith("# Page"):
        if current_page is not None:
            pages.append({
                "page": current_page,
                "text": "\n".join(content).strip()
            })

        current_page = int(line.replace("# Page", "").strip())
        content = []

    else:
        content.append(line)

# Save last page
if current_page is not None:
    pages.append({
        "page": current_page,
        "text": "\n".join(content).strip()
    })

json_data = {
    "document": MD_PATH.stem,
    "total_pages": len(pages),
    "pages": pages
}

output_file = MD_PATH.with_suffix(".json")

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(json_data, f, indent=4, ensure_ascii=False)

print(f"\nSaved: {output_file}")
print(f"Pages: {len(pages)}")