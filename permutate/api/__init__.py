import os

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException

from permutate.api import (
    cases,
    echo,
    generate_permutations,
    job,
    permutations,
    plugin_operation_params,
    ws_job,
)

from .http_error import http_error_handler

# Define an API prefix for routes
API_PREFIX = "/api"
ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")


# Function to create the FastAPI application instance
def create_app() -> FastAPI:
    # Create a FastAPI instance with title and documentation settings
    app = FastAPI(
        title="Permutate",
        openapi_url=f"{API_PREFIX}/openapi.json",
        docs_url=f"{API_PREFIX}/docs",
    )
    # Set the root path for the application in production environment
    # if ENVIRONMENT == "production":
    #    app.root_path = "/permutate/"

    # Create an APIRouter instance to organize routes
    router = APIRouter()
    # Include various routers from 'permutate' into the main router
    router.include_router(job.router)
    router.include_router(permutations.router)
    router.include_router(cases.router)
    router.include_router(ws_job.router)
    router.include_router(generate_permutations.router)
    router.include_router(echo.router)
    router.include_router(plugin_operation_params.router)

    # Include the main router into the FastAPI app with the specified prefix
    app.include_router(router, prefix=API_PREFIX)

    # Add an exception handler for HTTPException using the custom error handler
    app.add_exception_handler(HTTPException, http_error_handler)

    # Allow Cross-Origin Resource Sharing (CORS)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app


# Create the FastAPI application instance
app = create_app()
