from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.security.api_key import APIKey

from permutate import GenerateTestCase
from permutate.api import auth

# Create a FastAPI router
router = APIRouter(
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


# Define a route to generate test cases
@router.post("/generate-test-cases")
def generate_test_cases(
    test_cases: GenerateTestCase, api_key: APIKey = Depends(auth.get_api_key)
) -> Any:
    try:
        # Call the 'generate_test_cases' method of the 'GenerateTestCase' object
        return test_cases.generate_test_cases()
    except Exception as e:
        print(e)
        # Return a JSON response with a 500 status code in case of an exception
        return JSONResponse(
            status_code=500, content={"message": "Failed to generate test cases"}
        )
