from pathlib import Path


class PromptAdapter:
    """
    Adaptador para leer prompts desde archivos Markdown.
    Centraliza la gestión de los prompts utilizados por el modelo.
    """

    def __init__(self):
        self.prompts_dir = Path(__file__).parent / "prompts"

    def _read_prompt(self, filename: str) -> str:
        file_path = self.prompts_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"El archivo de prompt no existe: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            return f.read().strip()

    @property
    def lara_system_prompt(self) -> str:
        return self._read_prompt("lara.md")


# Instancia única para ser utilizada en toda la aplicación
prompts = PromptAdapter()
