
from app.services.ollama_service import (
    check_ollama_connection,
    generate_response,
)


def test_ollama_connection():
    result = check_ollama_connection()

    assert result["connected"] is True
    assert result["model_available"] is True


def test_ollama_generation():
    prompt = (
        "Explain what an AI lead management system does "
        "in two short sentences but the explanation should be in a humorous tone."
    )

    response = generate_response(prompt)

    assert isinstance(response, str)
    assert len(response.strip()) > 0

    print("\nOllama response:", response)
