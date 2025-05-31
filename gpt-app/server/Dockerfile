# Stage 1: Build dependencies
FROM python:3.9-slim as builder

WORKDIR /code

# System packages required for building some Python dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libgeos-dev \
    libproj-dev \
    proj-data \
    libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt .

RUN pip install --upgrade pip \
 && pip install --prefix=/install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.9-slim

WORKDIR /code

COPY --from=builder /install /usr/local
COPY ./app /code/app

# Clean environment to reduce size
RUN apt-get purge -y build-essential gcc \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/* /tmp/* /root/.cache

# Run FastAPI via uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
