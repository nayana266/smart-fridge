from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.utils.s3 import generate_presigned_url
import uuid
from datetime import datetime

router = APIRouter()

class PresignRequest(BaseModel):
    fileName: str
    fileType: str

class PresignResponse(BaseModel):
    uploadUrl: str
    key: str
    expiresIn: int

@router.post("/presign", response_model=PresignResponse)
async def get_presigned_upload_url(request: PresignRequest):
    """Generate presigned URL for S3 upload"""
    try:
        # Generate unique key for the file
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        key = f"uploads/{timestamp}_{unique_id}_{request.fileName}"
        
        # Generate presigned URL
        upload_url = generate_presigned_url(key, request.fileType)
        
        return PresignResponse(
            uploadUrl=upload_url,
            key=key,
            expiresIn=3600  # 1 hour
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate presigned URL: {str(e)}")
