from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.security.api_key import APIKey
from permutate.api import auth
from permutate import GenerateTestCase

router = APIRouter(
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.post("/generate-test-cases")
def generate_test_cases(
        test_cases: GenerateTestCase,
        api_key: APIKey = Depends(auth.get_api_key)
):
    try:
        return test_cases.generate_test_cases()
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500,
                            content={"message": "Failed to generate test cases"})
