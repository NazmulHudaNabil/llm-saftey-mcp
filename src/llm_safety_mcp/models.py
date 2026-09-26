from pydantic import BaseModel
from typing import List, Optional

class Finding(BaseModel):
    category: str
    severity: str
    message: str

class SafetyResult(BaseModel):
    safe: bool
    risk: str
    findings: List[Finding]

class PiiEntity(BaseModel):
    type: str
    value: str

class PiiResult(BaseModel):
    contains_pii: bool
    entities: List[PiiEntity]
