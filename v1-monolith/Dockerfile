# Étape 1 : Utiliser une image Python officielle comme base
FROM python:3.9-slim

# Étape 2 : Définir le répertoire de travail
WORKDIR /app

# Étape 3 : Copier le fichier des dépendances et les installer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Étape 4 : Copier le code de l'application
# La ligne suivante copie le contenu du dossier local "app" directement dans "/app"
COPY ./app/ .

# Étape 5 : Exposer le port
EXPOSE 5001

# Étape 6 : Commande de lancement corrigée
# On dit à Gunicorn de chercher l'objet "app" dans le fichier "__init__.py"
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "__init__:app"]