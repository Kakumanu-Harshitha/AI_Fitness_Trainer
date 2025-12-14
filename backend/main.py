from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .auth import router as auth_router
from .workout import router as workout_router
from .profile import router as profile_router

app = FastAPI(title="AI Fitness Tracker API")

Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(workout_router)
app.include_router(profile_router)

@app.get("/")
def root():
    return {"status": "Backend running"}
