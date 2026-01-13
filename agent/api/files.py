from fastapi import APIRouter, UploadFile, File, HTTPException
from agent.schemas.chat import Message
from agent.core.agent import agent
import base64
from typing import List

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/analyze-images")
async def analyze_images(files: List[UploadFile] = File(...)):
    if len(files) > 5:
        raise HTTPException(
            status_code=422, detail="You can upload a maximum of 5 files."
        )

    for file in files:
        if not any(
            [
                file.content_type.startswith("image/"),
                file.content_type == "application/pdf",
            ]
        ):
            raise HTTPException(
                status_code=400,
                detail=f"El archivo {file.filename} no es una imagen o PDF.",
            )

    file_content = []

    for file in files:
        try:
            image_bytes = await file.read()
            image_b64 = base64.b64encode(image_bytes).decode("utf-8")

            file_content.append(
                {
                    "type": "image",
                    "base64": image_b64,
                    "mime_type": file.content_type,
                }
            )

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error procesando el archivo {file.filename}: {str(e)}",
            )

    try:
        response = await agent.analyze_images(file_content)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
