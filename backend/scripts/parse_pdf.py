import fitz  # PyMuPDF
from pathlib import Path

# ------------ CHANGE THIS FOR EACH TENDER ------------
PDF_PATH = Path("data/tender1/RFP.pdf")
# -----------------------------------------------------

print(f"Parsing: {PDF_PATH.name}")

doc = fitz.open(PDF_PATH)

markdown = ""

for page_no, page in enumerate(doc, start=1):
    text = page.get_text("text")

    markdown += f"\n\n# Page {page_no}\n\n"
    markdown += text

output_file = PDF_PATH.with_suffix(".md")

with open(output_file, "w", encoding="utf-8") as f:
    f.write(markdown)

doc.close()

print(f"\nSaved to {output_file}")
print(f"Total Pages: {len(fitz.open(PDF_PATH))}")