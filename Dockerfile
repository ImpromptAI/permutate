FROM python:3.9

# Create app directory
WORKDIR /usr/app

# Install dependencies
COPY pyproject.toml ./
COPY poetry.lock ./
RUN pip install poetry
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes


RUN pip install -r requirements.txt

RUN pip install openplugin==0.0.31
# Bundle app source code
COPY . .

EXPOSE 8989

CMD ["python", "/usr/app/start_api_server.py"]