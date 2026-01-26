import requests
from typing import List

class OllamaLocalEmbeddings:
    """
    A lightweight wrapper for Ollama that uses standard HTTP requests.
    This bypasses ALL Python AI libraries (Torch, Onnx, LangChain) to prevent DLL crashes.
    """
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "nomic-embed-text"):
        self.base_url = base_url
        self.model = model
        print(f"Initialized Ollama Embeddings (Model: {model}) at {base_url}")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        for text in texts:
            embeddings.append(self.embed_query(text))
        return embeddings

    def embed_query(self, text: str) -> List[float]:
        try:
            response = requests.post(
                f"{self.base_url}/api/embeddings",
                json={
                    "model": self.model,
                    "prompt": text
                },
                timeout=30
            )
            if response.status_code == 200:
                return response.json()["embedding"]
            else:
                print(f"ERROR: Ollama returned {response.status_code}: {response.text}")
                return []
        except Exception as e:
            print(f"ERROR: Could not connect to Ollama at {self.base_url}. Is it running? Error: {e}")
            return []
