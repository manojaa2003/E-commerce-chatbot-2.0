from fastapi import FastAPI

from .database import engine
from . import models

from .routes import users,chat,auth

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import Settings

models.Base.metadata.create_all(bind=engine)

fast_app = FastAPI()

fast_app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Vite dev server
        "http://localhost:3000",   # CRA dev server, if you use it instead
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

fast_app.include_router(users.router)
fast_app.include_router(chat.router)
fast_app.include_router(auth.router)

@fast_app.get("/")
async def root():
    return {
        "message": "E-Commerce Chatbot API"
    }