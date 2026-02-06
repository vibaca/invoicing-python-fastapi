FROM python:3.11-bullseye
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
	build-essential \
	gcc \
	python3-dev \
	libssl-dev \
	libffi-dev \
	default-libmysqlclient-dev \
	cargo \
	rustc \
	&& rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt requirements.txt
RUN pip install --upgrade pip setuptools wheel && pip install --no-cache-dir -r requirements.txt

COPY ./src src
COPY ./alembic.ini alembic.ini
COPY ./migrations migrations

CMD ["uvicorn", "src.Main:app", "--host", "0.0.0.0", "--port", "8000"]
