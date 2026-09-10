from fastapi import APIRouter, HTTPException
from app.models import CompareRequest, CompareResponse
from app import rag

router = APIRouter(prefix="/api/compare", tags=["compare"])


@router.post("", response_model=CompareResponse)
def compare(req: CompareRequest):
    if len(req.policy_ids) < 2:
        raise HTTPException(status_code=400, detail="Select at least 2 policies to compare.")
    result = rag.compare_policies(req.question, req.policy_ids)
    return CompareResponse(**result)
