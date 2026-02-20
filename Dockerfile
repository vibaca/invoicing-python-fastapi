FROM python:3.11-slim-bullseye
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
	#build-essential \
	gcc \
	#python3-dev \
	#libssl-dev \
	#libffi-dev \
	libpq-dev \
	#cargo \
	#rustc \
	&& rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# dev dependencies
COPY requirements-dev.txt /app/requirements-dev.txt
RUN pip install --no-cache-dir -r requirements-dev.txt

COPY ./src /app/src
COPY ./alembic.ini /app/
COPY ./migrations /app/migrations

# Create non-root user
RUN addgroup --system --gid 1001 app && \
    adduser --system --uid 1001 --gid 1001 app && \
    chown -R app:app /app
USER app

EXPOSE 8000

CMD ["uvicorn", "src.Main:app", "--host", "0.0.0.0", "--port", "8000"]