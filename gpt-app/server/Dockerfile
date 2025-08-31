FROM python:3.12.11-slim


WORKDIR /code


# Install only necessary system dependencies for your Python packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libgl1 \
        && rm -rf /var/lib/apt/lists/*


COPY ./requirements.txt /code/requirements.txt
COPY ./app/.env.prod /code/.env


RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /code/requirements.txt


COPY ./app /code/app
COPY ./app/.env.prod /code/.env
COPY ./app/.env.prod /code/app/.env


CMD ["python", "app/main.py"]