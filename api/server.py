from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from api.routes import user_router, pipeline_router, project_router , commit_router , general_router , value_router , project_router_v2



app = FastAPI()

app.include_router(user_router, tags=["users"])
app.include_router(pipeline_router, tags=["pipelines"])
app.include_router(project_router, tags=["projects"])
app.include_router(commit_router, tags=["commits"])
app.include_router(general_router,  tags=["general"])
app.include_router(value_router, tags=["value"])
app.include_router(project_router_v2, tags=["projects_v2"])



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
