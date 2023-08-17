import os
import uvicorn
from dotenv import load_dotenv
from permutate.api import app

load_dotenv()

if __name__ == "__main__":
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 8989))
    uvicorn.run(app, host=host, port=port)
