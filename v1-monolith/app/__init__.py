import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

# Crée l'application Flask
app = Flask(__name__)

# --- Configuration de la Base de Données via Variables d'Environnement ---
# On lit les informations de connexion depuis les variables d'environnement.
# Si une variable n'existe pas, une valeur par défaut est utilisée (pour le développement local).
db_user = os.environ.get('MYSQL_USER', 'root')
db_pass = os.environ.get('MYSQL_PASSWORD', 'votre_mdp_local') # Mettez votre mot de passe local ici
db_host = os.environ.get('MYSQL_HOST', 'localhost')
db_name = os.environ.get('MYSQL_DB_NAME', 'cybermanager_db')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://{db_user}:{db_pass}@{db_host}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Définition des Routes ---
@app.route('/')
def index():
    try:
        # Test simple pour vérifier la connexion à la BDD
        db.session.execute(text('SELECT 1'))
        db_status = "Connecté à la base de données !"
    except Exception as e:
        db_status = f"Erreur de connexion à la BDD : {e}"
        
    return render_template('index.html', db_status=db_status)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)