import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# --- CONFIGURATION ---
# Par défaut : SQLite local pour le dev, mais prêt pour MySQL (K8s)
db_url = os.environ.get('DATABASE_URL', 'sqlite:///inventory.db')
app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("mysql://", "mysql+pymysql://")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- MODÈLE (BDD) ---
class Machine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    status = db.Column(db.String(20), default='available') # available / occupied

# --- INITIALISATION ---
with app.app_context():
    db.create_all()
    # On crée 5 PC par défaut si la base est vide
    if not Machine.query.first():
        for i in range(1, 6):
            db.session.add(Machine(name=f"PC-{i:02d}"))
        db.session.commit()

# --- ROUTES API (JSON) ---

@app.route('/machines', methods=['GET'])
def get_machines():
    """Renvoie la liste de tous les PC en JSON"""
    machines = Machine.query.all()
    # On transforme l'objet Python en Dictionnaire pour le JSON
    return jsonify([{
        'id': m.id, 
        'name': m.name, 
        'status': m.status
    } for m in machines])

@app.route('/machines/<int:id>', methods=['GET'])
def get_machine(id):
    """Renvoie les infos d'un seul PC"""
    machine = Machine.query.get_or_404(id)
    return jsonify({'id': machine.id, 'name': machine.name, 'status': machine.status})

@app.route('/machines/<int:id>/occupy', methods=['POST'])
def occupy_machine(id):
    """API pour marquer un PC comme occupé (appelée par le Service Billing)"""
    machine = Machine.query.get_or_404(id)
    if machine.status == 'occupied':
        return jsonify({'error': 'Machine already occupied'}), 400
    
    machine.status = 'occupied'
    db.session.commit()
    return jsonify({'message': f'{machine.name} is now occupied', 'status': 'occupied'})

@app.route('/machines/<int:id>/release', methods=['POST'])
def release_machine(id):
    """API pour libérer un PC (appelée par le Service Billing)"""
    machine = Machine.query.get_or_404(id)
    machine.status = 'available'
    db.session.commit()
    return jsonify({'message': f'{machine.name} is now available', 'status': 'available'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)