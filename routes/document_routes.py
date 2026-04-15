from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
import logging
from services.document_extraction_service import DocumentExtractionService

router = APIRouter()
logger = logging.getLogger(__name__)

def get_extraction_service():
    return DocumentExtractionService()

@router.post("/documents/extract")
async def extract_document_data(
    file: UploadFile = File(...),
    extraction_service: DocumentExtractionService = Depends(get_extraction_service)
):
    """
    Accepts an uploaded document (image or PDF), passes it to the AI extraction service,
    and returns parsed structured JSON without saving the file to the database.
    """
    try:
        if not file.content_type.startswith("image/") and file.content_type != "application/pdf":
            raise HTTPException(
                status_code=400, 
                detail="Invalid file type. Please upload an image or PDF."
            )

        file_bytes = await file.read()
        
        parsed_data = await extraction_service.extract_data_from_document(
            file_bytes=file_bytes, 
            mime_type=file.content_type
        )
        
        return parsed_data
        
    except Exception as e:
        logger.error(f"Failed to process document upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/documents/extract/loan")
async def extract_loan_document_data(
    file: UploadFile = File(...),
    extraction_service: DocumentExtractionService = Depends(get_extraction_service)
):
    """
    Accepts an uploaded loan document (image or PDF), passes it to the AI extraction service,
    and returns parsed structured JSON for a loan without saving the file to the database.
    """
    try:
        if not file.content_type.startswith("image/") and file.content_type != "application/pdf":
            raise HTTPException(
                status_code=400, 
                detail="Invalid file type. Please upload an image or PDF."
            )

        file_bytes = await file.read()
        
        parsed_data = await extraction_service.extract_loan_data_from_document(
            file_bytes=file_bytes, 
            mime_type=file.content_type
        )
        
        return parsed_data
        
    except Exception as e:
        logger.error(f"Failed to process loan document upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))
