import asyncio
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pinecone import Pinecone, ServerlessSpec
from tqdm.auto import tqdm

from embeddings.ollama_local import OllamaLocalEmbeddings


env_path = Path(__file__).resolve().parent.parent.parent / ".env"
print(f"DEBUG: Loading .env from: {env_path}")
load_dotenv(dotenv_path=env_path, override=True)

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

UPLOAD_DIR = Path("./uploaded_docs")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

if not PINECONE_API_KEY or not PINECONE_INDEX_NAME:
    raise RuntimeError("PINECONE_API_KEY and PINECONE_INDEX_NAME must be set")

pc = Pinecone(api_key=PINECONE_API_KEY)
spec = ServerlessSpec(cloud="aws", region=PINECONE_ENV or "us-east-1")
EMBED_DIMENSION = 768

existing_indexes = list(pc.list_indexes().names())

if PINECONE_INDEX_NAME in existing_indexes:
    index_info = pc.describe_index(PINECONE_INDEX_NAME)
    if getattr(index_info, "dimension", EMBED_DIMENSION) != EMBED_DIMENSION:
        raise RuntimeError(
            f"Pinecone index '{PINECONE_INDEX_NAME}' has dimension {index_info.dimension}, "
            f"but nomic-embed-text requires {EMBED_DIMENSION}. Create a matching index instead of overwriting."
        )

if PINECONE_INDEX_NAME not in existing_indexes:
    print(
        f"Creating new index '{PINECONE_INDEX_NAME}'... This can take up to 3 minutes, please wait...",
        flush=True,
    )
    pc.create_index(
        name=PINECONE_INDEX_NAME,
        dimension=EMBED_DIMENSION,
        metric="cosine",
        spec=spec,
    )
    while not pc.describe_index(PINECONE_INDEX_NAME).status["ready"]:
        time.sleep(1)
    print("Index is ready!", flush=True)

index = pc.Index(PINECONE_INDEX_NAME)


async def load_vectorstore(filename: str, file_bytes: bytes, role: str, doc_id: str):
    safe_name = Path(filename or "document.pdf").name
    if not safe_name.lower().endswith(".pdf"):
        raise ValueError("Only PDF files are supported")
    if not file_bytes:
        raise ValueError("Uploaded file is empty")

    print("Loading Ollama Embeddings (nomic-embed-text)...")
    embed_model = OllamaLocalEmbeddings(model="nomic-embed-text")

    save_path = UPLOAD_DIR / safe_name
    save_path.write_bytes(file_bytes)

    loader = PyPDFLoader(str(save_path))
    documents = loader.load()
    print(f"DEBUG: Loaded {len(documents)} pages from PDF.")

    if not documents:
        raise ValueError("PDF appears empty or unreadable.")

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(documents)
    print(f"DEBUG: Split into {len(chunks)} chunks.")

    if not chunks:
        raise ValueError("No text chunks created. Is this a scanned PDF?")

    texts = [chunk.page_content for chunk in chunks]
    ids = [f"{doc_id}-{i}" for i in range(len(chunks))]
    metadatas = [
        {
            "source": safe_name,
            "doc_id": doc_id,
            "role": role,
            "page": str(chunk.metadata.get("page", 0)),
            "text": chunk.page_content,
        }
        for chunk in chunks
    ]

    print(f"Embedding {len(texts)} chunks...")
    embeddings = await asyncio.to_thread(embed_model.embed_documents, texts)

    vectors = []
    for vid, embedding, metadata in zip(ids, embeddings, metadatas):
        if not embedding:
            print(f"WARNING: Skipping chunk {vid} because embedding was empty")
            continue
        vectors.append({"id": vid, "values": embedding, "metadata": metadata})

    if not vectors:
        raise ValueError("Failed to generate embeddings. Is Ollama running?")

    print("Uploading to Pinecone...")
    batch_size = 100
    with tqdm(total=len(vectors), desc="Upserting to Pinecone") as progress:
        for start in range(0, len(vectors), batch_size):
            batch = vectors[start : start + batch_size]
            index.upsert(vectors=batch)
            progress.update(len(batch))

    print(f"Upload complete for {safe_name}")
    return {"chunks": len(vectors), "source": safe_name}
