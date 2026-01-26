import os
import asyncio
from dotenv import load_dotenv
from pinecone import Pinecone
from embeddings.ollama_local import OllamaLocalEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from pathlib import Path

# Load .env from root directory (consistency with vectorstore.py)
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path, override=True) # Force override


GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
print(f"DEBUG: GOOGLE_API_KEY loaded from {env_path}, prefix: {GOOGLE_API_KEY[:5] if GOOGLE_API_KEY else 'None'}")

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY") # Fixed Typo
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")




# Validating and Loading HF Token
HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")
if not HUGGINGFACEHUB_API_TOKEN:
    print("WARNING: HUGGINGFACEHUB_API_TOKEN not found in .env. Embeddings will fail.")
else:
    print(f"DEBUG: HUGGINGFACEHUB_API_TOKEN found: {HUGGINGFACEHUB_API_TOKEN[:5]}...")


os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY


# Debug prints to verify keys are loaded
print(f"DEBUG: PINECONE_API_KEY loaded: {bool(PINECONE_API_KEY)}")
print(f"DEBUG: GROQ_API_KEY loaded: {bool(GROQ_API_KEY)}")
print(f"DEBUG: PINECONE_INDEX_NAME: {PINECONE_INDEX_NAME}")

pc=Pinecone(api_key=PINECONE_API_KEY)
index=pc.Index(PINECONE_INDEX_NAME)

print("Loading Ollama Embeddings (nomic-embed-text)...")
embed_model = OllamaLocalEmbeddings(model="nomic-embed-text")

llm=ChatGroq(temperature=0.3,model_name="llama-3.3-70b-versatile",groq_api_key=GROQ_API_KEY)


prompt=PromptTemplate.from_template("""
You are a helpful healthcare assistant.Answer the following quetion
 based only on the provided context.
                                    
    Question:{question}
                                    
    Context:{context}
                                    
 Include the document source if relevant in yout answer.

""")

rag_chain=prompt | llm






async def answer_query(query:str,user_role:str):
    
    print(f"DEBUG: Querying for role: {user_role}")
    try:
        embedding=await asyncio.to_thread(embed_model.embed_query,query)
        print(f"DEBUG: Embedding generated. Length: {len(embedding)}")
        if not embedding or all(x == 0 for x in embedding):
            print("ERROR: Embedding is empty or all zeros!")
    except Exception as e:
        print(f"ERROR: Embedding generation failed: {e}")
        return {"answer": f"Error generating embedding: {str(e)}", "sources": []}

    try:
        results=await asyncio.to_thread(index.query, vector=embedding,top_k=3,include_metadata=True)
        print(f"DEBUG: Pinecone returned {len(results['matches'])} matches.")
        for m in results['matches']:
            print(f" - Match score: {m['score']}, Role: {m['metadata'].get('role')}")
    except Exception as e:
        print(f"ERROR: Pinecone query failed: {e}")
        return {"answer": f"Error querying database: {str(e)}", "sources": []}

    filtered_contexts=[]
    sources=set()

    for match in results["matches"]:
        metadata=match["metadata"]
        # Debug the filtering logic
        match_role = metadata.get("role")
        if match_role == user_role:
            filtered_contexts.append(metadata.get("text","")+"\\n")
            sources.add(metadata.get("source"))
        else:
            print(f"DEBUG: Skipped doc due to role mismatch. Doc role: {match_role}, User role: {user_role}")

    if not filtered_contexts:
        print("DEBUG: No contexts remained after filtering.")
        return {"answer":"No relevant info found"}
    
    docs_text="\\n".join(filtered_contexts)
    
    try:
        final_answer=await asyncio.to_thread(rag_chain.invoke,{"question":query,"context":docs_text})
    except Exception as e:
         print(f"ERROR: LLM invocation failed: {e}")
         return {"answer": f"Error calling LLM: {str(e)}", "sources": []}


    return {
        "answer":final_answer.content,
        "sources":list(sources)
    }



