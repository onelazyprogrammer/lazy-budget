import os
from dotenv import load_dotenv
from typing import Optional


class ConfigAdapter:
    """
    Clase intermedia (Adapter) que abstrae el origen de las variables de entorno.
    Sigue el patrón adaptador para proporcionar una interfaz limpia al resto de la app.
    """

    def __init__(self):
        load_dotenv()

    def _get_env_var(self, key: str, default: Optional[str] = None) -> str:
        value = os.getenv(key, default)
        if value is None:
            raise ValueError(
                f"La variable de entorno '{key}' no está definida y no tiene valor por defecto."
            )
        return value

    @property
    def gemini_api_key(self) -> str:
        return self._get_env_var("GEMINI_API_KEY")

    @property
    def model_name(self) -> str:
        return self._get_env_var("MODEL_NAME")

    @property
    def model_temperature(self) -> float:
        return float(self._get_env_var("MODEL_TEMPERATURE"))


settings = ConfigAdapter()
