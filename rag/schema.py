from typing import List, TypedDict, Literal
from pydantic import BaseModel, Field


class docEval(BaseModel):
    reason: str
    score: float
    
class KeepOrDrop(BaseModel):
    keep: bool
    
class WebQuery(BaseModel):
    query: str
    
class IsSUPDecision(BaseModel):
    issup: Literal["fully_supported", "partially_supported", "no_support"]
    evidence: List[str] = Field(default_factory=list)
    
class IsUSEDecision(BaseModel):
    isuse: Literal["useful", "not_useful"]
    reason: str = Field(..., description="Short reason in 1 line.")
    
class RewriteDecision(BaseModel):
    retrieval_query: str = Field(
        ...,
        description="Rewritten query optimized for vector retrieval against internal company PDFs."
    )