FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN useradd --create-home app && mkdir -p instance && chown -R app:app instance
USER app
EXPOSE 8000
# One worker + threads keeps the in-memory rate limits accurate. Mount /app/instance as a volume.
CMD ["gunicorn", "wsgi:app", "--workers", "1", "--threads", "8", "--bind", "0.0.0.0:8000", "--access-logfile", "-"]
