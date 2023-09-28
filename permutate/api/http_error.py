from fastapi import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse


# Define an asynchronous function to handle HTTP exceptions
async def http_error_handler(_: Request, exc: HTTPException) -> JSONResponse:
    """
    An error handler for FastAPI that converts HTTP exceptions into JSON responses.

    Args:
        _: Request object (not used in this function)
        exc: The HTTPException instance representing the error

    Returns:
        JSONResponse: A JSON response containing the error message and status code.
    """
    # Create a JSONResponse with a list containing the error detail and the HTTP status code
    return JSONResponse({"errors": [exc.detail]}, status_code=exc.status_code)
