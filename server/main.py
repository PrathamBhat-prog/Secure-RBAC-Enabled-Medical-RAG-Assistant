from fastapi import FastAPI

from auth.routes import router as auth_router
from chat.routes import router as chat_router
from config.db import init_db, ping_db
from docs.routes import router as docs_router


app = FastAPI(title="RBAC Medical RAG Assistant")

app.include_router(auth_router)
app.include_router(docs_router)
app.include_router(chat_router)


@app.on_event("startup")
def startup_db_client():
    try:
        init_db()
        ping_db()
        print("DEBUG: Connected to Supabase Postgres successfully!", flush=True)
    except Exception as e:
        import sys

        print(f"DEBUG: Postgres connection failed: {e}", file=sys.stderr, flush=True)


@app.get("/health")
def health_check():
    try:
        ping_db()
        db_status = "ok"
    except Exception:
        db_status = "error"
    return {"message": "OK", "database": db_status}
