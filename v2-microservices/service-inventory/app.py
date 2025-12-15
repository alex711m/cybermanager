import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import uuid

app = Flask(__name__)

# --- CONFIGURATION ---
db_url = os.environ.get('DATABASE_URL', 'sqlite:///inventory.db')
app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("mysql://", "mysql+pymysql://")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- MODÈLE (BDD) ---
class Machine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    status = db.Column(db.String(20), default='available')

# --- INITIALISATION ---
with app.app_context():
    db.create_all()
    # On crée 5 PC par défaut UNIQUEMENT si la base est vide
    if not Machine.query.first():
        for i in range(1, 6):
            db.session.add(Machine(name=f"PC-{i:02d}"))
        db.session.commit()

# --- ROUTES API (JSON) ---

@app.route('/machines', methods=['GET'])
def get_machines():
    """Renvoie la liste de tous les PC"""
    machines = Machine.query.all()
    return jsonify([{'id': m.id, 'name': m.name, 'status': m.status} for m in machines])

@app.route('/machines/<int:id>', methods=['GET'])
def get_machine(id):
    machine = Machine.query.get_or_404(id)
    return jsonify({'id': machine.id, 'name': machine.name, 'status': machine.status})

# --- NOUVEAU : Route pour AJOUTER un PC ---
@app.route('/machines', methods=['POST'])
def create_machine():
    """Crée un PC avec la logique : Nom = 'PC-' + (Nombre total + 1)"""
    
    # 1. On compte combien de machines existent DANS LA BDD
    count = Machine.query.count()
    
    # 2. On génère le nom
    # Note : Si tu as supprimé des PC, il peut y avoir des conflits (ex: PC-3 existe déjà)
    # On fait une petite boucle de sécurité pour trouver le prochain numéro libre
    next_id = count + 1
    new_name = f"PC-{next_id}"
    
    while Machine.query.filter_by(name=new_name).first():
        next_id += 1
        new_name = f"PC-{next_id}"

    # 3. On enregistre
    new_machine = Machine(name=new_name, status='available')
    
    try:
        db.session.add(new_machine)
        db.session.commit()
        
        # 4. IMPORTANT : On renvoie le nom généré au Gateway
        return jsonify({
            'message': 'Machine created', 
            'id': new_machine.id, 
            'name': new_machine.name
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- NOUVEAU : Route pour SUPPRIMER un PC ---
@app.route('/machines/<int:id>', methods=['DELETE'])
def delete_machine(id):
    machine = Machine.query.get_or_404(id)
    db.session.delete(machine)
    db.session.commit()
    return jsonify({'message': 'Machine deleted'}), 200

@app.route('/machines/<int:id>/occupy', methods=['POST'])
def occupy_machine(id):
    machine = Machine.query.get_or_404(id)
    if machine.status == 'occupied':
        return jsonify({'error': 'Machine already occupied'}), 400
    
    machine.status = 'occupied'
    db.session.commit()
    return jsonify({'message': f'{machine.name} is now occupied', 'status': 'occupied'})

@app.route('/machines/<int:id>/release', methods=['POST'])
def release_machine(id):
    machine = Machine.query.get_or_404(id)
    machine.status = 'available'
    db.session.commit()
    return jsonify({'message': f'{machine.name} is now available', 'status': 'available'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
