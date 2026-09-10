import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential
from app.config import settings

genai.configure(api_key=settings.gemini_api_key)

_model = genai.GenerativeModel(settings.gemini_model)


@retry(stop=stop_after_attempt(4), wait=wait_exponential(multiplier=1, min=2, max=20))
def embed_text(text: str, task_type: str = "retrieval_document") -> list[float]:
    result = genai.embed_content(
        model=settings.gemini_embedding_model,
        content=text,
        task_type=task_type,
    )
    return result["embedding"]


@retry(stop=stop_after_attempt(4), wait=wait_exponential(multiplier=1, min=2, max=20))
def embed_batch(texts: list[str], task_type: str = "retrieval_document") -> list[list[float]]:
    # Gemini embed_content supports single content; loop with retry per item.
    return [embed_text(t, task_type=task_type) for t in texts]


@retry(stop=stop_after_attempt(4), wait=wait_exponential(multiplier=1, min=2, max=20))
def generate(prompt: str, system_instruction: str | None = None) -> str:
    model = _model
    if system_instruction:
        model = genai.GenerativeModel(
            settings.gemini_model, system_instruction=system_instruction
        )
    response = model.generate_content(prompt)
    return response.text.strip()
