import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models import UploadResponse, PolicyInfo, PolicyListResponse
from app.pdf_parser import extract_pages, chunk_pages
from app import vectorstore

router = APIRouter(prefix="/api/policies", tags=["policies"])


@router.post("/upload", response_model=UploadResponse)
async def upload_policy(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    pages = extract_pages(file_bytes)
    chunks = chunk_pages(pages)
    if not chunks:
        raise HTTPException(status_code=400, detail="Could not extract readable text from this PDF.")

    policy_id = uuid.uuid4().hex[:12]
    num_added = vectorstore.add_policy_chunks(policy_id, file.filename, chunks)

    return UploadResponse(
        policy=PolicyInfo(policy_id=policy_id, filename=file.filename, num_chunks=num_added),
        message=f"Uploaded and indexed {num_added} chunks from {file.filename}.",
    )


@router.get("", response_model=PolicyListResponse)
def list_policies():
    policies = vectorstore.list_policies()
    return PolicyListResponse(policies=[PolicyInfo(**p) for p in policies])


@router.delete("/{policy_id}")
def delete_policy(policy_id: str):
    vectorstore.delete_policy(policy_id)
    return {"message": f"Deleted policy {policy_id}"}
