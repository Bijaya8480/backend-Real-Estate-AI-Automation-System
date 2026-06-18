FROM python:3.11-slim

WORKDIR /app

# Install build toolchain so dependencies with native extensions can build.
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc g++ build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Basic health endpoint uses the FastAPI root GET / which returns JSON.
HEALTHCHECK CMD python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8000/').status)" || exit 1

ENTRYPOINT ["uvicorn", "main:app", "--host=0.0.0.0", "--port=8000"]

