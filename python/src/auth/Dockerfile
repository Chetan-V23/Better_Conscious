FROM python:3.12.12-slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential && pip install --no-cache-dir --upgrade pip

WORKDIR /app
COPY requirements.txt /app
RUN pip install psycopg2-binary
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app

EXPOSE 8000
CMD ["python3", "server.py"]
