FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# On copie le code ET les dossiers templates/static
COPY . .

EXPOSE 5000

CMD ["python", "app.py"]