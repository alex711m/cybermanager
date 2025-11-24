# 1. On part d'une image Python légère officielle
FROM python:3.9-slim

# 2. On définit le dossier de travail dans le conteneur
WORKDIR /app

# 3. On copie les dépendances et on installe
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. On installe Gunicorn (serveur de production) explicitement
RUN pip install gunicorn

# 5. On copie tout le dossier 'app' local vers le dossier '/app/app' du conteneur
COPY app/ ./app/

# 6. On expose le port 5000 (Standard Flask)
EXPOSE 5000

# 7. La commande de démarrage
# Explication : on lance gunicorn, on écoute partout (0.0.0.0) sur le port 5000
# "app:create_app()" dit à gunicorn : "Va dans le dossier app, et lance la fonction create_app()"
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:create_app()"]