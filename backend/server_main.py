from fastapi import FastAPI
from backend.fir_api import router as fir_router
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
# Add backend routes
app.include_router(fir_router, prefix="/api")


@app.get("/")
def root():
    return {"message": "Backend running!"}
