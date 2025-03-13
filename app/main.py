from fastapi import FastAPI
from app.routers import users
from app.models.database import Base, engine

app = FastAPI(title="FastAPI CRUD Example")

# Crear las tablas en la base de datos si no existen
Base.metadata.create_all(bind=engine)

app.include_router(users.router)

@app.get("/")
def home():
    return {"message": "Welcome to FastAPI CRUD with SQLite"}

