import os
import requests
from datetime import datetime
import pytz
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# --- CONFIGURATION ---
# Base de données dédiée aux FACTURES (pas aux machines)
db_url = os.environ.get('DATABASE_URL', 'sqlite:///billing.db')
app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("mysql://", "mysql+pymysql://")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# URL du Service Inventory (pour lui donner des ordres)
INVENTORY_API_URL = os.environ.get('INVENTORY_API_URL', 'http://host.docker.internal:5002')

# Configuration Métier
PRIX_PAR_HEURE = 5.0
TZ_QUEBEC = pytz.timezone('America/Montreal')

db = SQLAlchemy(app)

# --- MODÈLE (BDD) ---
class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    machine_id = db.Column(db.Integer, nullable=False) # On stocke juste l'ID, pas l'objet Machine complet
    start_time = db.Column(db.DateTime, default=datetime.now)
    end_time = db.Column(db.DateTime, nullable=True)
    total_price = db.Column(db.Float, default=0.0)

# --- INITIALISATION ---
with app.app_context():
    db.create_all()

# --- LOGIQUE MÉTIER ---

@app.route('/sessions/start', methods=['POST'])
def start_session():
    data = request.json
    machine_id = data.get('machine_id')
    
    # 1. COMMUNICATION INTER-SERVICE : On dit à l'Inventory "Occupe ce PC !"
    # Si l'Inventory dit non (400), on arrête tout.
    try:
        response = requests.post(f"{INVENTORY_API_URL}/machines/{machine_id}/occupy")
        if response.status_code != 200:
            return jsonify({'error': 'Impossible de réserver la machine (déjà prise ?)'}), 400
    except Exception as e:
        return jsonify({'error': f'Erreur de connexion avec Inventory: {str(e)}'}), 500

    # 2. Si l'Inventory est OK, on crée la session chez nous
    now_quebec = datetime.now(TZ_QUEBEC).replace(tzinfo=None) # On simplifie pour SQLite
    new_session = Session(machine_id=machine_id, start_time=now_quebec)
    
    db.session.add(new_session)
    db.session.commit()
    
    return jsonify({'message': 'Session démarrée', 'session_id': new_session.id})

@app.route('/sessions/stop/<int:machine_id>', methods=['POST'])
def stop_session(machine_id):
    # 1. On cherche la session active pour ce PC
    active_session = Session.query.filter_by(machine_id=machine_id, end_time=None).first()
    
    if not active_session:
        return jsonify({'error': 'Aucune session active trouvée'}), 404
        
    # 2. Calcul du prix
    now_quebec = datetime.now(TZ_QUEBEC).replace(tzinfo=None)
    active_session.end_time = now_quebec
    
    duration = active_session.end_time - active_session.start_time
    hours = duration.total_seconds() / 3600
    price = round(hours * PRIX_PAR_HEURE, 2)
    active_session.total_price = price

    # 3. COMMUNICATION INTER-SERVICE : On dit à l'Inventory "Libère ce PC !"
    try:
        requests.post(f"{INVENTORY_API_URL}/machines/{machine_id}/release")
    except Exception as e:
        # On loggue l'erreur mais on ne plante pas la facturation (l'argent d'abord !)
        print(f"Attention: Impossible de libérer la machine dans l'inventaire: {e}")

    db.session.commit()
    
    return jsonify({
        'message': 'Session terminée', 
        'price': price, 
        'duration_hours': round(hours, 2)
    })

if __name__ == '__main__':
    # On lance sur le port 5000 interne
    app.run(host='0.0.0.0', port=5000, debug=True)
