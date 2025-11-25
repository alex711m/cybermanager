import os
import requests
from flask import Flask, render_template, redirect, url_for, request, flash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-key-gateway'

# --- CONFIGURATION RÉSEAU ---
# On définit les adresses des deux autres services
INVENTORY_API_URL = os.environ.get('INVENTORY_API_URL', 'http://host.docker.internal:5002')
BILLING_API_URL = os.environ.get('BILLING_API_URL', 'http://host.docker.internal:5004')

# --- CLASSE DUMMY (Utilisateur fictif pour l'affichage) ---
class MockUser:
    username = "Admin (Microservices)"
    is_authenticated = True

@app.route('/')
def index():
    # 1. On récupère l'état des machines depuis l'Inventory
    try:
        response = requests.get(f"{INVENTORY_API_URL}/machines")
        if response.status_code == 200:
            machines = response.json()
        else:
            machines = []
    except Exception as e:
        print(f"Erreur Inventory: {e}")
        machines = []

    return render_template('index.html', machines=machines, user=MockUser())

# --- NOUVELLES ROUTES (Actions) ---

@app.route('/session/start/<int:machine_id>', methods=['POST'])
def start_session_route(machine_id):
    """Quand on clique sur Démarrer"""
    try:
        # Le Gateway délègue le travail au Service Billing
        response = requests.post(f"{BILLING_API_URL}/sessions/start", json={'machine_id': machine_id})
        
        if response.status_code == 200:
            flash(f"Session démarrée sur le PC {machine_id}", "success")
        else:
            flash("Erreur : Impossible de démarrer (Machine occupée ?)", "error")
            
    except Exception as e:
        flash(f"Erreur de connexion au Service Billing: {str(e)}", "error")

    return redirect(url_for('index'))

@app.route('/session/stop/<int:machine_id>', methods=['POST'])
def stop_session_route(machine_id):
    """Quand on clique sur Arrêter"""
    try:
        # Le Gateway demande au Billing d'arrêter la session
        response = requests.post(f"{BILLING_API_URL}/sessions/stop/{machine_id}")
        
        if response.status_code == 200:
            data = response.json()
            prix = data.get('price')
            flash(f"Session terminée ! Prix à payer : {prix} $", "success")
        else:
            flash("Erreur lors de l'arrêt de la session", "error")
            
    except Exception as e:
        flash(f"Erreur de connexion au Service Billing: {str(e)}", "error")

    return redirect(url_for('index'))

# --- Route de réinitialisation (Optionnel, appelle Inventory) ---
@app.route('/reset')
def reset():
    # Pour l'instant on redirige juste, à implémenter si besoin
    return redirect(url_for('index'))

@app.route('/machines/add', methods=['POST'])
def add_machine():
    # Dans une vraie v2, il faudrait appeler l'API Inventory : requests.post(...)
    flash("Fonctionnalité 'Ajout de PC' désactivée pour la démo Microservices.", "warning")
    return redirect(url_for('index'))

@app.route('/history')
def history():
    # Dans une vraie v2, il faudrait appeler l'API Billing pour avoir la liste des transactions
    flash("L'historique est stocké dans le service Billing mais l'interface n'est pas encore reliée.", "info")
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    # Comme on utilise un MockUser, la déconnexion est simulée
    flash("Déconnexion impossible : Vous êtes sur un compte de démonstration.", "info")
    return redirect(url_for('index'))

@app.route('/reset')
def reset_db():
    flash("La réinitialisation du parc est désactivée pour la sécurité de la démo.", "warning")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)