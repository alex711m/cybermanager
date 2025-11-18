from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
import pytz
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from .models import db, Machine, Session, User
from sqlalchemy import func # Ajoute cet import tout en haut si besoin, ou utilise sum() python

# Création du Blueprint
main_bp = Blueprint('main', __name__)

# Configuration
PRIX_PAR_HEURE = 5.0
TZ_QUEBEC = pytz.timezone('America/Montreal')

# ==========================================
# 1. ROUTES D'AUTHENTIFICATION (Publiques)
# ==========================================

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Si l'utilisateur est déjà connecté, on le renvoie au dashboard
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main.index'))
        else:
            flash('Identifiant ou mot de passe incorrect.', 'error')
            
    return render_template('login.html')

@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('main.login'))

# Route spéciale pour créer le premier admin (A supprimer en prod normalement)
@main_bp.route('/init-admin')
def init_admin():
    existing = User.query.filter_by(username='admin').first()
    if not existing:
        hashed_pw = generate_password_hash('admin123', method='pbkdf2:sha256')
        new_admin = User(username='admin', password=hashed_pw)
        db.session.add(new_admin)
        db.session.commit()
        return "✅ Admin créé ! (Login: admin / Pass: admin123)"
    return "⚠️ L'admin existe déjà."

# ==========================================
# 2. ROUTES MÉTIER (Protégées par Login)
# ==========================================

@main_bp.route('/')
@login_required 
def index():
    machines = Machine.query.all()
    return render_template('index.html', machines=machines, user=current_user)

@main_bp.route('/machines/add', methods=['POST'])
@login_required # Sécurité ajoutée
def add_machine():
    count = Machine.query.count()
    new_machine = Machine(name=f"PC-{count + 1}", status="available")
    
    db.session.add(new_machine)
    db.session.commit()
    flash('Nouvelle machine ajoutée.', 'success')
    return redirect(url_for('main.index'))

@main_bp.route('/reset')
@login_required # Sécurité ajoutée
def reset_db():
    # Attention : On ne supprime pas les Users pour ne pas tuer ton compte admin !
    Machine.query.delete()
    Session.query.delete()
    
    # On recrée 5 PC
    for i in range(1, 6):
        pc = Machine(name=f"PC-{i:02d}")
        db.session.add(pc)
    db.session.commit()
    flash('Base de données machines réinitialisée.', 'warning')
    return redirect(url_for('main.index'))

@main_bp.route('/session/start/<int:machine_id>', methods=['POST'])
@login_required
def start_session(machine_id):
    machine = Machine.query.get_or_404(machine_id)
    
    if machine.status == 'occupied':
        flash('Cette machine est déjà prise !', 'error')
        return redirect(url_for('main.index'))

    machine.status = 'occupied' 
    now_quebec = datetime.now(TZ_QUEBEC)
    start_time_db = now_quebec.replace(tzinfo=None)
    
    new_session = Session(machine_id=machine.id, start_time=start_time_db)
    
    db.session.add(new_session)
    db.session.commit()
    
    return redirect(url_for('main.index'))

@main_bp.route('/session/stop/<int:machine_id>', methods=['POST'])
@login_required # Sécurité ajoutée
def stop_session(machine_id):
    machine = Machine.query.get_or_404(machine_id)
    
    active_session = Session.query.filter_by(machine_id=machine.id, end_time=None).first()
    
    if active_session:
        now_quebec = datetime.now(TZ_QUEBEC)
        active_session.end_time = now_quebec.replace(tzinfo=None)
        
        duration = active_session.end_time - active_session.start_time
        hours = duration.total_seconds() / 3600
        price = round(hours * PRIX_PAR_HEURE, 2)
        
        active_session.total_price = price
        machine.status = 'available'
        db.session.commit()
        
        flash(f"Session terminée ! Prix : {price} €", 'success')
        
    return redirect(url_for('main.index'))

@main_bp.route('/history')
@login_required
def history():
    # Récupérer toutes les sessions terminées (celles qui ont une date de fin)
    # On les trie par date décroissante (du plus récent au plus vieux)
    finished_sessions = Session.query.filter(Session.end_time != None).order_by(Session.start_time.desc()).all()
    
    # Calcul du chiffre d'affaires total
    raw_income = sum(session.total_price for session in finished_sessions)
    total_income = round(raw_income, 2)
    
    return render_template('history.html', sessions=finished_sessions, total_income=total_income)