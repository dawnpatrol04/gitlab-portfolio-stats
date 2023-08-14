
from fastapi import FastAPI
from api.routes import router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()


origins = [
    "http://127.0.0.1:5000",
    "http://localhost:5000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)