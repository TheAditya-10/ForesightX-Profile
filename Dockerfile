FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY ForesightX-Profile/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.12-slim AS runner

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app/ForesightX-Profile

COPY --from=builder /install /usr/local
COPY ForesightX-Profile /app/ForesightX-Profile 

RUN useradd --create-home --shell /usr/sbin/nologin appuser && \
    chown -R appuser:appuser /app/ForesightX-Profile
USER appuser

EXPOSE 8002

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8002/health', timeout=3).read()"

CMD ["sh", "-lc", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8002"]
