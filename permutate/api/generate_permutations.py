from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.security.api_key import APIKey

from permutate.api import auth
from permutate.generate_permutations import (
    GeneratePermutations,
    GeneratePermutationsRequest,
)

# Create a FastAPI router
router = APIRouter(
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.post("/generate-permutations")
def generate_permutations(
    request: GeneratePermutationsRequest, api_key: APIKey = Depends(auth.get_api_key)
) -> Any:
    try:
        if request.save_to_s3:
            obj = GeneratePermutations(request=request)
            return obj.gen_s3()
        else:
            obj = GeneratePermutations(request=request)
            return obj.gen()
    except Exception as e:
        print(e)
        return JSONResponse(
            status_code=500, content={"message": "Failed to generate permutations"}
        )
