import re
from .models import Finding, SafetyResult, PiiEntity, PiiResult

PII_PATTERNS = {
    "EMAIL": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
    "PHONE": r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",
    "IP_ADDRESS": r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b",
    "CREDIT_CARD": r"\b(?:\d[ -]*?){13,16}\b"
}

PROMPT_INJECTION_KEYWORDS = [
    "ignore all previous instructions",
    "ignore previous instructions",
    "system prompt",
    "reveal your instructions",
    "you are now",
    "override",
]

def detect_pii(text: str) -> PiiResult:
    entities = []
    
    for pii_type, pattern in PII_PATTERNS.items():
        matches = re.finditer(pattern, text)
        for match in matches:
            value = match.group(0)
            # basic validation to avoid simple false positives in CCs etc.
            # (In a real system this would be more robust)
            if pii_type == "CREDIT_CARD" and len(re.sub(r"[^\d]", "", value)) not in [13, 14, 15, 16]:
                continue
            
            entities.append(PiiEntity(type=pii_type, value=value))
            
    return PiiResult(contains_pii=bool(entities), entities=entities)

def detect_prompt_injection(text: str) -> SafetyResult:
    findings = []
    text_lower = text.lower()
    
    for keyword in PROMPT_INJECTION_KEYWORDS:
        if keyword in text_lower:
            findings.append(Finding(
                category="prompt_injection",
                severity="high",
                message=f"Instruction override attempt detected: '{keyword}'"
            ))
            
    safe = len(findings) == 0
    risk = "high" if not safe else "low"
    
    return SafetyResult(safe=safe, risk=risk, findings=findings)

def sanitize_text(text: str) -> str:
    sanitized_text = text
    
    # Simple replacement strategy (can overlap, but works for v1)
    # We replace longer matches first to avoid partial overlaps
    entities = detect_pii(text).entities
    entities = sorted(entities, key=lambda e: len(e.value), reverse=True)
    
    for entity in entities:
        sanitized_text = sanitized_text.replace(entity.value, f"[{entity.type}_REDACTED]")
        
    return sanitized_text

def check_text(text: str) -> SafetyResult:
    findings = []
    
    # 1. PII Check
    pii_result = detect_pii(text)
    if pii_result.contains_pii:
        for entity in pii_result.entities:
            findings.append(Finding(
                category="pii",
                severity="medium",
                message=f"{entity.type} detected"
            ))
            
    # 2. Prompt Injection Check
    injection_result = detect_prompt_injection(text)
    findings.extend(injection_result.findings)
    
    safe = len(findings) == 0
    risk = "high" if any(f.severity == "high" for f in findings) else ("medium" if len(findings) > 0 else "low")
    
    return SafetyResult(safe=safe, risk=risk, findings=findings)
