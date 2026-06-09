from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.fir_api import router as fir_router
from backend.auth_api import router as auth_router
from backend.stats_api import router as stats_router
from backend.chat_api import router as chat_router
from backend.report_api import router as report_router

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(fir_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(stats_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(report_router, prefix="/api")


@app.get("/")
def root():
    return {"message": "Backend running!"}
