import os
from fastapi import FastAPI
from fastapi import APIRouter
from .http_error import http_error_handler
from starlette.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from permutate.api import job
from permutate.api import permutations
from permutate.api import cases

API_PREFIX = "/api"
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'development')


def create_app() -> FastAPI:
    app = FastAPI(
        title="Permutate",
        openapi_url=f"{API_PREFIX}/openapi.json",
        docs_url=f"{API_PREFIX}/docs"
    )
    if ENVIRONMENT == 'production':
        app.root_path = "/permutate/"

    # add routes
    router = APIRouter()
    router.include_router(job.router)
    router.include_router(permutations.router)
    router.include_router(cases.router)
    app.include_router(router, prefix=API_PREFIX)

    app.add_exception_handler(HTTPException, http_error_handler)
    # Allow CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app


app = create_app()
