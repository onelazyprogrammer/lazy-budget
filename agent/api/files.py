from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from agent.schemas.chat import Message
from agent.schemas.auth import User
from agent.core.agent import agent
from agent.utils.auth import get_current_user
import base64
from typing import List

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/analyze-images")
async def analyze_images(files: List[UploadFile] = File(...), current_user: User = Depends(get_current_user)):
    if len(files) > 5:
        raise HTTPException(
            status_code=422, detail="You can upload a maximum of 5 files."
        )

    content_parts = [
        {
            "type": "text",
            "text": "Analiza estas imágenes y extrae la información solicitada.",
        }
    ]

    for file in files:
        if not (
            file.content_type.startswith("image/")
            or file.content_type == "application/pdf"
        ):
            raise HTTPException(
                status_code=400,
                detail=f"El archivo {file.filename} no es una imagen o PDF.",
            )

        try:
            file_bytes = await file.read()
            base64_data = base64.b64encode(file_bytes).decode("utf-8")

            content_parts.append(
                {"type": "image", "base64": base64_data, "mime_type": file.content_type}
            )

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error procesando el archivo {file.filename}: {str(e)}",
            )

    try:
        user_message = Message(role="user", content=content_parts)
        response = await agent.analyze_images([user_message])
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
