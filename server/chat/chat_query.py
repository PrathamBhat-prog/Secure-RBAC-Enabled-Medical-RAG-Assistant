import os
import asyncio
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from pinecone import Pinecone

from embeddings.ollama_local import OllamaLocalEmbeddings


env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

if GOOGLE_API_KEY:
    os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

print(f"DEBUG: PINECONE_API_KEY loaded: {bool(PINECONE_API_KEY)}")
print(f"DEBUG: GROQ_API_KEY loaded: {bool(GROQ_API_KEY)}")
print(f"DEBUG: PINECONE_INDEX_NAME: {PINECONE_INDEX_NAME}")

if not PINECONE_API_KEY or not PINECONE_INDEX_NAME:
    raise RuntimeError("PINECONE_API_KEY and PINECONE_INDEX_NAME must be set")

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)

print("Loading Ollama Embeddings (nomic-embed-text)...")
embed_model = OllamaLocalEmbeddings(model="nomic-embed-text")

llm = ChatGroq(
    temperature=0.3,
    model_name=GROQ_MODEL,
    groq_api_key=GROQ_API_KEY,
)

prompt = PromptTemplate.from_template(
    """
You are a helpful healthcare assistant. Answer the following question
based only on the provided context. If the context is insufficient, say you do not know.

Question: {question}

Context: {context}

Include the document source if relevant in your answer.
"""
)

rag_chain = prompt | llm

ROLE_ACCESS = {
    "admin": None,
    "doctor": ["doctor", "nurse", "patient", "other"],
    "nurse": ["nurse", "patient", "other"],
    "patient": ["patient", "other"],
    "other": ["other"],
}


def pinecone_filter_for_role(user_role: str):
    allowed = ROLE_ACCESS.get((user_role or "").lower(), ["other"])
    if allowed is None:
        return None
    return {"role": {"$in": allowed}}


async def answer_query(query: str, user_role: str):
    query = (query or "").strip()
    if not query:
        return {"answer": "Please enter a question.", "sources": []}

    print(f"DEBUG: Querying for role: {user_role}")
    try:
        embedding = await asyncio.to_thread(embed_model.embed_query, query)
        print(f"DEBUG: Embedding generated. Length: {len(embedding) if embedding else 0}")
        if not embedding or all(x == 0 for x in embedding):
            return {
                "answer": "Embedding service returned an empty vector. Is Ollama running with nomic-embed-text?",
                "sources": [],
            }
    except Exception as e:
        print(f"ERROR: Embedding generation failed: {e}")
        return {"answer": f"Error generating embedding: {str(e)}", "sources": []}

    metadata_filter = pinecone_filter_for_role(user_role)
    try:
        query_kwargs = {
            "vector": embedding,
            "top_k": 5,
            "include_metadata": True,
        }
        if metadata_filter:
            query_kwargs["filter"] = metadata_filter
        results = await asyncio.to_thread(index.query, **query_kwargs)
        matches = results.get("matches") or []
        print(f"DEBUG: Pinecone returned {len(matches)} matches.")
    except Exception as e:
        print(f"ERROR: Pinecone query failed: {e}")
        return {"answer": f"Error querying database: {str(e)}", "sources": []}

    filtered_contexts = []
    sources = set()

    for match in matches:
        metadata = match.get("metadata") or {}
        text = metadata.get("text", "")
        source = metadata.get("source")
        if text:
            filtered_contexts.append(text)
        if source:
            sources.add(source)

    if not filtered_contexts:
        print("DEBUG: No contexts remained after filtering.")
        return {
            "answer": "No relevant information was found for your role.",
            "sources": [],
        }

    docs_text = "\n\n".join(filtered_contexts)

    try:
        final_answer = await asyncio.to_thread(
            rag_chain.invoke, {"question": query, "context": docs_text}
        )
    except Exception as e:
        print(f"ERROR: LLM invocation failed: {e}")
        return {"answer": f"Error calling LLM: {str(e)}", "sources": []}

    return {
        "answer": final_answer.content,
        "sources": list(sources),
    }
