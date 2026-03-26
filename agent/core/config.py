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
    def access_token_expire_minutes(self) -> int:
        return int(self._get_env_var("ACCESS_TOKEN_EXPIRE_MINUTES"))

    @property
    def jwt_secret_key(self) -> str:
        return self._get_env_var("JWT_SECRET_KEY")

    @property
    def jwt_algorithm(self) -> str:
        return self._get_env_var("JWT_ALGORITHM")

    @property
    def db_name(self) -> str:
        return self._get_env_var("DB_NAME")

    @property
    def db_user(self) -> str:
        return self._get_env_var("DB_USER")

    @property
    def db_password(self) -> str:
        return self._get_env_var("DB_PASSWORD")

    @property
    def gemini_api_key(self) -> str:
        return self._get_env_var("GEMINI_API_KEY")

    @property
    def model_name(self) -> str:
        return self._get_env_var("MODEL_NAME")

    @property
    def model_temperature(self) -> float:
        return float(self._get_env_var("MODEL_TEMPERATURE"))

    @property
    def db_host(self) -> str:
        return self._get_env_var("DB_HOST", "localhost")

    @property
    def db_port(self) -> int:
        return int(self._get_env_var("DB_PORT", "5432"))

    @property
    def redis_host(self) -> str:
        return self._get_env_var("REDIS_HOST", "localhost")

    @property
    def redis_port(self) -> int:
        return int(self._get_env_var("REDIS_PORT", "6379"))

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def checkpoint_url(self) -> str:
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"


settings = ConfigAdapter()
