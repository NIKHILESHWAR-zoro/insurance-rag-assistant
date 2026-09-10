from pydantic import BaseModel
from typing import Optional


class PolicyInfo(BaseModel):
    policy_id: str
    filename: str
    num_chunks: int


class UploadResponse(BaseModel):
    policy: PolicyInfo
    message: str


class QueryRequest(BaseModel):
    question: str
    policy_ids: Optional[list[str]] = None  # if None, search across all uploaded policies


class SourceCitation(BaseModel):
    policy_id: str
    filename: str
    chunk_text: str
    page: Optional[int] = None
    score: Optional[float] = None


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceCitation]


class CompareRequest(BaseModel):
    question: str
    policy_ids: list[str]


class CompareRow(BaseModel):
    policy_id: str
    filename: str
    finding: str
    sources: list[SourceCitation]


class CompareResponse(BaseModel):
    summary: str
    rows: list[CompareRow]


class PolicyListResponse(BaseModel):
    policies: list[PolicyInfo]
