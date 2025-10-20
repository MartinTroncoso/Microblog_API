FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Comando por defecto (se pasa a "$@" en el entrypoint)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]