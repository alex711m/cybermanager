# Image Python légère
FROM python:3.9-slim

# Dossier de travail
WORKDIR /app

# Installation des dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code
COPY app.py .

# On expose le port standard Flask
EXPOSE 5000

# Lancement direct (pas de Gunicorn pour l'instant pour faciliter le debug)
CMD ["python", "app.py"]