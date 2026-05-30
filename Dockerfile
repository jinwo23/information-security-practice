# Dockerfile — Security Hardened
# Антон: multi-stage build — зменшує розмір образу та поверхню атаки

FROM python:3.12-slim AS builder

WORKDIR /app
COPY requirements.txt .

# Встановлюємо залежності в окрему папку /install
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


FROM python:3.12-slim

# Богдан: non-root користувач — контейнер працює не від root
RUN groupadd -r appuser && \
    useradd -r -g appuser -d /app -s /sbin/nologin appuser

WORKDIR /app

# Артем: копіюємо встановлені залежності з builder
COPY --from=builder /install /usr/local

# Копіюємо код додатку
COPY ./app ./app
COPY ./alembic ./alembic
COPY alembic.ini .

# Влад: data директорія з правами appuser
RUN mkdir -p /app/data && chown -R appuser:appuser /app

# Перемикаємось на non-root
USER appuser

# Антон: health check — контейнер перевіряє працездатність API
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
