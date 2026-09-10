from fastapi import APIRouter
from app.models import QueryRequest, QueryResponse
from app import rag

router = APIRouter(prefix="/api/query", tags=["query"])


@router.post("", response_model=QueryResponse)
def ask_question(req: QueryRequest):
    result = rag.answer_question(req.question, req.policy_ids)
    return QueryResponse(**result)
