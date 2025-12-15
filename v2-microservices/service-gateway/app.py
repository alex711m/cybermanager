import os
import requests
import random
from flask import Flask, render_template, redirect, url_for, request, flash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-key-gateway'

INVENTORY_API_URL = os.environ.get('INVENTORY_API_URL', 'http://host.docker.internal:5002')
BILLING_API_URL = os.environ.get('BILLING_API_URL', 'http://host.docker.internal:5004')

class MockUser:
    username = "Admin (Microservices)"
    is_authenticated = True

@app.route('/')
def index():
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

@app.route('/session/start/<int:machine_id>', methods=['POST'])
def start_session_route(machine_id):
    try:
        response = requests.post(f"{BILLING_API_URL}/sessions/start", json={'machine_id': machine_id})
        if response.status_code == 200:
            flash(f"Session démarrée sur le PC {machine_id}", "success")
        else:
            flash("Erreur : Impossible de démarrer (La machine est peut être occupée ?)", "error")
    except Exception as e:
        flash(f"Erreur de connexion Billing: {str(e)}", "error")
    return redirect(url_for('index'))

@app.route('/session/stop/<int:machine_id>', methods=['POST'])
def stop_session_route(machine_id):
    try:
        response = requests.post(f"{BILLING_API_URL}/sessions/stop/{machine_id}")
        if response.status_code == 200:
            data = response.json()
            flash(f"Session terminée ! Prix : {data.get('price')} $", "success")
        else:
            flash("Erreur lors de l'arrêt de la session", "error")
    except Exception as e:
        flash(f"Erreur de connexion Billing: {str(e)}", "error")
    return redirect(url_for('index'))

# --- NOUVEAU : AJOUT DE PC ---
@app.route('/machines/add', methods=['POST'])
def add_machine():
    # Sécurité (simulée avec MockUser comme dans ton code actuel)
    # Dans un vrai cas, on vérifierait current_user.is_admin ici
    
    try:
        # 1. On envoie une requête POST vide (pas de 'json={"name":...}')
        # C'est l'Inventory qui va décider du nom
        response = requests.post(f"{INVENTORY_API_URL}/machines")
        
        if response.status_code == 201:
            data = response.json()
            # 2. On récupère le nom que l'Inventory a choisi
            created_name = data.get('name') 
            flash(f"Nouvelle machine ajoutée : {created_name}", "success")
        else:
            # Gestion d'erreur propre
            error_msg = response.json().get('error', 'Erreur inconnue')
            flash(f"Erreur lors de la création : {error_msg}", "error")
            
    except Exception as e:
        flash(f"Impossible de contacter le service Inventory : {e}", "error")

    return redirect(url_for('index'))

# --- NOUVEAU : SUPPRESSION DE PC ---
@app.route('/machines/delete/<int:machine_id>', methods=['POST'])
def delete_machine(machine_id):
    try:
        # On envoie la demande de suppression à l'Inventory
        response = requests.delete(f"{INVENTORY_API_URL}/machines/{machine_id}")
        
        if response.status_code == 200:
            flash("PC supprimé avec succès.", "warning")
        else:
            flash("Erreur lors de la suppression.", "error")
    except Exception as e:
        flash(f"Impossible de contacter l'Inventory : {e}", "error")

    return redirect(url_for('index'))

@app.route('/history')
def history():
    flash("L'historique est stocké dans le service Billing.", "info")
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    flash("Déconnexion impossible : Compte démo.", "info")
    return redirect(url_for('index'))

@app.route('/reset')
def reset_db():
    flash("Réinitialisation désactivée.", "warning")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
