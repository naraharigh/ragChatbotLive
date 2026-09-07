from fastapi import FastAPI

from app.api import admin, auth, query
from fastapi.responses import RedirectResponse

app = FastAPI(title="ADV RAG", version="0.1.0-lesson-9")
@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")
app.include_router(admin.router)
app.include_router(auth.router)
app.include_router(query.router)

