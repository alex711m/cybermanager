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
    data = request.get_json()
    new_name = data.get('name')
    
    if not new_name:
        return jsonify({'error': 'Name is required'}), 400
        
    # Vérifier si le nom existe déjà
    if Machine.query.filter_by(name=new_name).first():
        return jsonify({'error': 'Machine already exists'}), 400

    new_machine = Machine(name=new_name, status='available')
    db.session.add(new_machine)
    db.session.commit()
    
    return jsonify({'message': 'Machine created', 'id': new_machine.id}), 201

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
