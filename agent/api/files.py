from fastapi import APIRouter, UploadFile, File, HTTPException
from agent.schemas.chat import Message
from agent.core.agent import agent
import base64

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/analyze-image")
async def analyze_image(file: UploadFile = File(...)):

    # Validar extensión
    if not any(
        [file.content_type.startswith("image/"), file.content_type == "application/pdf"]
    ):
        raise HTTPException(
            status_code=400, detail="El archivo enviado no es una imagen."
        )

    try:
        # Leer y codificar imagen
        image_bytes = await file.read()
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")

        # Crear mensaje multimodal usando el esquema de Message/langchain
        # Aquí pasamos el contenido que el nodo _image_analysis_node espera
        multimodal_message = Message(
            role="user",
            content=[
                {
                    "type": "text",
                    "text": "Analiza esta imagen y extrae la información para el budget. Quiero saber quien mando a quien y cuanto dinero.",
                },
                {
                    "type": "image",
                    "base64": image_b64,
                    "mime_type": file.content_type,
                },
            ],
        )

        response = await agent.analyze_image(multimodal_message)

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
