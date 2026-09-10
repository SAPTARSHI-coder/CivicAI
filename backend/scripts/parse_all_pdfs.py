import fitz
import json
from pathlib import Path
from PIL import Image
import pytesseract

# =====================================================
# Configuration
# =====================================================

DATA_FOLDER = Path("data")

CHUNK_SIZE = 500
OVERLAP = 75

# Set your Tesseract path (Windows)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# =====================================================
# Helper Function
# =====================================================

def extract_text(page):
    """
    Try extracting text using PyMuPDF.
    If very little text is found, fall back to OCR.
    """

    text = page.get_text("text")

    # If enough text exists, use it
    if len(text.strip()) > 30:
        return text

    print("   OCR fallback used...")

    # Convert page to image
    pix = page.get_pixmap(dpi=300)

    img = Image.frombytes(
        "RGB",
        [pix.width, pix.height],
        pix.samples
    )

    # OCR
    text = pytesseract.image_to_string(img)

    return text


# =====================================================
# Process PDFs
# =====================================================

for tender_folder in sorted(DATA_FOLDER.iterdir()):

    if not tender_folder.is_dir():
        continue

    pdf_files = list(tender_folder.glob("*.pdf"))

    if len(pdf_files) == 0:
        print(f"No PDF found in {tender_folder.name}")
        continue

    pdf_path = pdf_files[0]

    print("=" * 60)
    print(f"Processing {pdf_path.name}")
    print("=" * 60)

    # ---------------------------------------------------
    # STEP 1 : PDF -> Markdown
    # ---------------------------------------------------

    doc = fitz.open(pdf_path)

    markdown = ""

    for page_no, page in enumerate(doc, start=1):

        text = extract_text(page)

        markdown += f"\n\n# Page {page_no}\n\n"
        markdown += text

    md_path = pdf_path.with_suffix(".md")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(markdown)

    doc.close()

    print("Markdown created")

    # ---------------------------------------------------
    # STEP 2 : Markdown -> JSON
    # ---------------------------------------------------

    pages = []

    current_page = None
    content = []

    for line in markdown.splitlines():

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

    if current_page is not None:

        pages.append({
            "page": current_page,
            "text": "\n".join(content).strip()
        })

    json_data = {
        "document": pdf_path.stem,
        "total_pages": len(pages),
        "pages": pages
    }

    json_path = pdf_path.with_suffix(".json")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=4, ensure_ascii=False)

    print("JSON created")

    # ---------------------------------------------------
    # STEP 3 : Chunking
    # ---------------------------------------------------

    chunks = []

    chunk_id = 1

    for page in pages:

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

    chunk_data = {
        "document": pdf_path.stem,
        "total_chunks": len(chunks),
        "chunks": chunks
    }

    chunk_path = tender_folder / "chunks.json"

    with open(chunk_path, "w", encoding="utf-8") as f:
        json.dump(chunk_data, f, indent=4, ensure_ascii=False)

    print(f"Chunks created: {len(chunks)}")

print("\n🎉 All PDFs processed successfully!")