from fastapi import FastAPI
from config.database import startup_db_client, shutdown_db_client
from bookstore.routes import router as book_router
from s100.s102.routes import router as s102_router
from s100.s111.routes import router as s111_router
from s100.s104.routes import router as s104_router
import uvicorn


from dotenv import dotenv_values
from fastapi.middleware.cors import CORSMiddleware

config = dotenv_values(".env")

origins = [
    "http://localhost",
    "http://localhost:3000",
    "https://watermelon-gis-app-42qk-samdyra.vercel.app"
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    startup_db_client(app, config)


@app.on_event("shutdown")
async def shutdown():
    shutdown_db_client(app)

app.include_router(book_router, tags=["books"], prefix="/book")
app.include_router(s102_router, tags=["s102"], prefix="/s102")
app.include_router(s104_router, tags=["s104"], prefix="/s104")
app.include_router(s111_router, tags=["s111"], prefix="/s111")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)
