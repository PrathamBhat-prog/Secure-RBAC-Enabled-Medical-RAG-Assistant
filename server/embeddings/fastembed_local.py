from typing import List
from fastembed import TextEmbedding

class LocalFastEmbeddings:
    """
    A unified wrapper for FastEmbed (ONNX) to replace LangChain/Google embeddings.
    Runs locally, no API key, no heavy Torch dependency.
    """
    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        # "BAAI/bge-small-en-v1.5" is a very popular, small, high-quality model (384 dim)
        # It is supported natively by fastembed and is better than all-MiniLM-L6-v2
        print(f"Loading Local ONNX Model: {model_name} ...")
        self.model = TextEmbedding(model_name=model_name)
        print("Model loaded successfully.")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        # fastembed returns a generator, convert to list
        return list(self.model.embed(texts))

    def embed_query(self, text: str) -> List[float]:
        # embed returns list of generators, we need the first vector
        result = list(self.model.embed([text]))
        if result:
            return list(result[0])
        return []
