from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter(prefix="/samples", tags=["samples"])

# Locate data folder relative to backend root
DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent / "data"

SAMPLE_DOCS = [
    {
        "id": "pmay",
        "title": "PMAY Housing Scheme FAQ",
        "category": "Housing & Urban",
        "filename": "RevisedFAQ_PMAY.pdf",
        "rel_path": "pmay/RevisedFAQ_PMAY.pdf",
        "description": "Pradhan Mantri Awas Yojana guidelines, eligibility income caps, and required documentation.",
    },
    {
        "id": "nsp",
        "title": "National Scholarship Portal FAQ",
        "category": "Education & Student Aid",
        "filename": "NSPInstituteFAQV1.7.pdf",
        "rel_path": "NSP/NSPInstituteFAQV1.7.pdf",
        "description": "Eligibility criteria, institute verification steps, and required student documentation.",
    },
    {
        "id": "pmkisan",
        "title": "PM-KISAN Guidelines",
        "category": "Agriculture & Farmers",
        "filename": "RevisedPM-KISANOperationalGuidelines(English).pdf",
        "rel_path": "pmkisan/RevisedPM-KISANOperationalGuidelines(English).pdf",
        "description": "Direct income support for small and marginal landholding farmer families.",
    },
    {
        "id": "pmjay",
        "title": "Ayushman Bharat (PM-JAY)",
        "category": "Healthcare",
        "filename": "public_authorities_ddc2bbda34.pdf",
        "rel_path": "pmjay/public_authorities_ddc2bbda34.pdf",
        "description": "Health coverage eligibility, empanelled hospitals, and claims procedure.",
    },
]


@router.get("")
async def list_sample_documents():
    """List bundled sample government documents available for immediate demo."""
    results = []
    for doc in SAMPLE_DOCS:
        file_path = DATA_DIR / doc["rel_path"]
        available = file_path.exists()
        size_bytes = file_path.stat().st_size if available else 0
        results.append({
            "id": doc["id"],
            "title": doc["title"],
            "category": doc["category"],
            "filename": doc["filename"],
            "description": doc["description"],
            "available": available,
            "size_bytes": size_bytes,
        })
    return results


@router.get("/{sample_id}/download")
async def download_sample_document(sample_id: str):
    """Download the raw sample PDF for analysis or local preview."""
    doc = next((d for d in SAMPLE_DOCS if d["id"] == sample_id), None)
    if not doc:
        raise HTTPException(status_code=404, detail="Sample document not found.")

    file_path = DATA_DIR / doc["rel_path"]
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Sample file {doc['filename']} not found on disk.")

    return FileResponse(
        path=str(file_path),
        filename=doc["filename"],
        media_type="application/pdf",
    )
