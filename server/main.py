from fastapi import FastAPI
from auth.routes import router as auth_router
from docs.routes import router as docs_router
from chat.routes import  router as chat_router


app=FastAPI()

app.include_router(auth_router)
app.include_router(docs_router)
app.include_router(chat_router)


@app.on_event("startup")
def startup_db_client():
    try:
        from config.db import client
        client.admin.command('ping')
        print("DEBUG: Connected to MongoDB successfully!", flush=True)
    except Exception as e:
        import sys
        print(f"DEBUG: MongoDB connection failed: {e}", file=sys.stderr, flush=True)

@app.get("/health")
def health_check():
    return {"message":"OKkkk"}


# def main():
#     print("Hello from server!")


# if __name__ == "__main__":
#     main()
