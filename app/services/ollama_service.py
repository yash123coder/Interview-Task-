
import httpx
import os

OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://localhost:11434"
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "llama3.2:3b"
)


class OllamaServiceError(Exception):
    """Raised when Ollama cannot process a request."""


def check_ollama_connection():
    """Check whether Ollama is running and the model is available."""

    try:
        response = httpx.get(
            f"{OLLAMA_BASE_URL}/api/tags",
            timeout=10.0
        )
        response.raise_for_status()

        models = response.json().get("models", [])

        available_models = [
            model.get("name") for model in models
        ]

        return {
            "connected": True,
            "model": OLLAMA_MODEL,
            "model_available": OLLAMA_MODEL in available_models,
            "available_models": available_models
        }

    except httpx.HTTPError as exc:
        raise OllamaServiceError(
            f"Unable to connect to Ollama: {exc}"
        ) from exc


# def generate_response(prompt: str) -> str:
#     """Generate a response using the configured local model."""

#     try:
#         response = httpx.post(
#             f"{OLLAMA_BASE_URL}/api/generate",
#             json={
#                 "model": OLLAMA_MODEL,
#                 "prompt": prompt,
#                 "stream": False,
#                 "options": {
#                     "temperature": 0.2
#                 }
#             },
#             timeout=120.0
#         )

#         response.raise_for_status()

#         result = response.json()

#         generated_text = result.get("response")

#         if not generated_text:
#             raise OllamaServiceError(
#                 "Ollama returned an empty response."
#             )

#         return generated_text

#     except httpx.TimeoutException as exc:
#         raise OllamaServiceError(
#             "Ollama request timed out."
#         ) from exc

#     except httpx.HTTPError as exc:
#         raise OllamaServiceError(
#             f"Ollama API request failed: {exc}"
#         ) from exc


def generate_response(prompt: str, response_format=None) -> str:
    """Generate a response using the configured local model."""

    try:
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1
            }
        }

        if response_format:
            payload["format"] = response_format

        response = httpx.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=120.0
        )

        response.raise_for_status()

        result = response.json()
        generated_text = result.get("response")

        if not generated_text:
            raise OllamaServiceError(
                "Ollama returned an empty response."
            )

        return generated_text

    except httpx.TimeoutException as exc:
        raise OllamaServiceError(
            "Ollama request timed out."
        ) from exc

    except httpx.HTTPError as exc:
        raise OllamaServiceError(
            f"Ollama API request failed: {exc}"
        ) from exc