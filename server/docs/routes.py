import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from auth.models import ALLOWED_ROLES
from auth.routes import authenticate
from docs.vectorstore import load_vectorstore


router = APIRouter()


@router.post("/upload_docs")
async def upload_docs(
    user=Depends(authenticate),
    file: UploadFile = File(...),
    role: str = Form(...),
):
    if user["role"] not in ["admin", "doctor"]:
        raise HTTPException(status_code=403, detail="Only admin and doctor can upload files")

    target_role = (role or "").strip().lower()
    if target_role not in ALLOWED_ROLES:
        raise HTTPException(
            status_code=400,
            detail=f"accessible role must be one of: {', '.join(ALLOWED_ROLES)}",
        )

    filename = file.filename or ""
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    doc_id = str(uuid.uuid4())
    try:
        await load_vectorstore(filename, file_bytes, target_role, doc_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail="Failed to index document")

    return {
        "message": f"{filename} uploaded successfully",
        "doc_id": doc_id,
        "accessible_to": target_role,
    }
