import os
import time
from pathlib import Path
from dotenv import load_dotenv
from tqdm.auto import tqdm
from pinecone import Pinecone, ServerlessSpec
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from embeddings.ollama_local import OllamaLocalEmbeddings
import asyncio


from pathlib import Path
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
print(f"DEBUG: Loading .env from: {env_path}")
load_dotenv(dotenv_path=env_path, override=True) # Force override

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") # Not used for embeddings but maybe needed elsewhere?

# Validating and Loading HF Token
HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")
if not HUGGINGFACEHUB_API_TOKEN:
    print("WARNING: HUGGINGFACEHUB_API_TOKEN not found in .env. Embeddings will fail.")
else:
    print(f"DEBUG: HUGGINGFACEHUB_API_TOKEN found: {HUGGINGFACEHUB_API_TOKEN[:5]}...")

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")



UPLOAD_DIR = "./uploaded_docs"
os.makedirs(UPLOAD_DIR, exist_ok=True)


pc = Pinecone(api_key=PINECONE_API_KEY)
spec = ServerlessSpec(cloud='aws', region=PINECONE_ENV or "us-east-1")

EMBED_DIMENSION = 768

existing_index = [i["name"] for i in pc.list_indexes()]

if PINECONE_INDEX_NAME in existing_index:
    try:
        index_info = pc.describe_index(PINECONE_INDEX_NAME)
        if index_info.dimension != EMBED_DIMENSION:
            print(f"WARNING: Index dimension mismatch (Expected {EMBED_DIMENSION}, got {index_info.dimension}). Deleting index...")
            pc.delete_index(PINECONE_INDEX_NAME)
            existing_index.remove(PINECONE_INDEX_NAME)
            time.sleep(10)
    except Exception as e:
        print(f"Error checking index dimension: {e}")

if PINECONE_INDEX_NAME not in existing_index:
    print(f"Creating new index '{PINECONE_INDEX_NAME}' with dimension {EMBED_DIMENSION}...")
    pc.create_index(
        name=PINECONE_INDEX_NAME,
        dimension=EMBED_DIMENSION,
        metric="dotproduct",
        spec=spec
    )
    while not pc.describe_index(PINECONE_INDEX_NAME).status["ready"]:
        time.sleep(1)

index = pc.Index(PINECONE_INDEX_NAME)

async def load_vectorstore(uploaded_files, role: str, doc_id: str):
    print("Loading Ollama Embeddings (nomic-embed-text)...")
    embed_model = OllamaLocalEmbeddings(model="nomic-embed-text")

    for file in uploaded_files:
        save_path = Path(UPLOAD_DIR) / file.filename
        with open(save_path, "wb") as f:
            f.write(file.file.read())

        loader = PyPDFLoader(str(save_path))
        documents = loader.load()
        print(f"DEBUG: Loaded {len(documents)} pages from PDF.")

        if not documents:
            print("ERROR: PDF appears empty or unreadable.")
            return

        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = splitter.split_documents(documents)
        print(f"DEBUG: Split into {len(chunks)} chunks.")

        if not chunks:
            print("ERROR: No text chunks created. Is this a scanned PDF?")
            return

        texts = [chunk.page_content for chunk in chunks]
        ids = [f"{doc_id}-{i}" for i in range(len(chunks))]
        metadatas = [
            {
                "source": file.filename,
                "doc_id": doc_id,
                "role": role,
                "page": chunk.metadata.get("page", 0)
            }
            for i, chunk in enumerate(chunks)
        ]

        print(f"Embedding {len(texts)} chunks...")
        # Run embedding in main thread
        embeddings = await asyncio.to_thread(embed_model.embed_documents,texts)

        print("Uploading to Pinecone...")
        with tqdm(total=len(embeddings), desc="Upserting to Pinecone") as progress:
            index.upsert(vectors=zip(ids, embeddings, metadatas))
            progress.update(len(embeddings))

        print(f"Upload complete for {file.filename}")
