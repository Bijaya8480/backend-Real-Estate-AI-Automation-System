"""FastAPI entrypoint for Real Estate AI Automation System."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional

# Support both package and non-package execution.
# Prefer relative imports when `backend` is a package.
try:
    from .email_classifier import classify_email
    from .document_processor import extract_info_from_text
    from .lead_qualifier import qualify_lead
except ImportError:  # pragma: no cover
    from email_classifier import classify_email
    from document_processor import extract_info_from_text
    from lead_qualifier import qualify_lead


app = FastAPI(
    title="Real Estate AI Automation API",
    description="AI workflows for Real Estate SMEs: Email Classification, Document Processing, Lead Qualification",
    version="1.0.0",
)


class EmailRequest(BaseModel):
    email_text: str


class EmailResponse(BaseModel):
    category: str
    confidence: str
    scores: Dict[str, int]


class DocumentRequest(BaseModel):
    text: str


class DocumentResponse(BaseModel):
    tenant: Optional[str]
    landlord: Optional[str]
    rent_amount: Optional[str]
    start_date: Optional[str]
    end_date: Optional[str]
    property_address: Optional[str]
    total_amount: Optional[str]
    full_text: str


class LeadRequest(BaseModel):
    lead_text: str


class LeadResponse(BaseModel):
    qualification: str
    score: float
    reasoning: str


@app.get("/")
def root() -> Dict[str, str]:
    return {"message": "Real Estate AI Automation API is running"}


@app.post("/classify_email", response_model=EmailResponse)
def classify_email_endpoint(request: EmailRequest) -> Dict[str, Any]:
    if not request.email_text.strip():
        raise HTTPException(status_code=400, detail="email_text is required")
    return classify_email(request.email_text)


@app.post("/extract_document", response_model=DocumentResponse)
def extract_document_endpoint(request: DocumentRequest) -> Dict[str, Any]:
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="text is required")
    return extract_info_from_text(request.text)


@app.post("/qualify_lead", response_model=LeadResponse)
def qualify_lead_endpoint(request: LeadRequest) -> Dict[str, Any]:
    if not request.lead_text.strip():
        raise HTTPException(status_code=400, detail="lead_text is required")
    return qualify_lead(request.lead_text)


def start():
    """Callable entrypoint for deployment platforms."""
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

