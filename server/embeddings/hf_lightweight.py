import requests
from typing import List, Optional

class LightweightHFEmbeddings:
    """
    A lightweight wrapper for HuggingFace Inference API that uses standard 'requests'
    instead of the heavy 'langchain-huggingface' library to avoid DLL/Torch issues on Windows.
    """
    def __init__(self, api_key: str, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.api_url = f"https://router.huggingface.co/models/{model_name}"
        self.headers = {"Authorization": f"Bearer {api_key}"}

    def _call_api(self, inputs: List[str]) -> List[List[float]]:
        # HuggingFace API expects 'inputs' as list of strings
        payload = {
            "inputs": inputs,
            "options": {"wait_for_model": True}
        }
        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error calling HF API: {e}")
            try:
                print(f"Response content: {response.text}")
            except:
                pass
            raise e

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents."""
        return self._call_api(texts)

    def embed_query(self, text: str) -> List[float]:
        """Embed a single query."""
        result = self._call_api([text])
        if isinstance(result, list) and len(result) > 0:
            return result[0]
        return []
