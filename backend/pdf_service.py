"""PDF extraction and optional private S3 persistence for uploaded CV files."""
from __future__ import annotations
import base64
import os
import re
import time
import boto3
import fitz

# CV_BUCKET is injected by AWS SAM. Without it, local parsing stays fully local.
_BUCKET = os.getenv("CV_BUCKET")
_s3 = boto3.client("s3") if _BUCKET else None

def extract_pdf_text(filename: str, content_base64: str) -> tuple[str, str | None]:
    # Decode and validate the upload before opening it with PyMuPDF.
    raw = base64.b64decode(content_base64, validate=True)
    if len(raw) > 5 * 1024 * 1024:
        raise ValueError("PDF is larger than the 5 MB demo limit")
    doc = fitz.open(stream=raw, filetype="pdf")
    text = "\n".join(page.get_text("text") for page in doc)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    if not text:
        raise ValueError("No selectable text found in the PDF")

    s3_key = None
    # Cloud deployments keep the original PDF private in S3; local mode skips storage.
    if _s3 is not None and _BUCKET:
        safe = re.sub(r"[^A-Za-z0-9._-]", "_", filename)[:100] or "cv.pdf"
        s3_key = f"uploads/{int(time.time())}-{safe}"
        _s3.put_object(Bucket=_BUCKET, Key=s3_key, Body=raw, ContentType="application/pdf")
    return text, s3_key
