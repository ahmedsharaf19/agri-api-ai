from fastapi import APIRouter, UploadFile, File, Request
from fastapi.responses import JSONResponse
from app.services.detection_service import process_image
import uuid

router = APIRouter()

@router.post("/predict")
async def predict_api(request: Request, file: UploadFile = File(...)):
    try:
        session_id = request.headers.get("X-Session-ID", str(uuid.uuid4()))

        result = await process_image(file)

        return JSONResponse(content={
            "session_id": session_id,
            "image_url": result.get("image_url"),
            "diseases": result.get("diseases"),
            "treatment": result.get("treatment"),
        })

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
