from flask import Flask
from .models import db, User # On importe User pour le loader
from flask_login import LoginManager 

def create_app():
    app = Flask(__name__)

    # --- CONFIGURATION ---
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cybermanager.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'dev-cle-secrete'

    # Initialisation BDD
    db.init_app(app)

    # --- CONFIGURATION LOGIN (Le Vigile) ---
    login_manager = LoginManager()
    login_manager.login_view = 'main.login' # Si pas connecté, on renvoie ici
    login_manager.init_app(app)

    # Cette fonction aide Flask à retrouver l'utilisateur via son ID
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # --- ROUTES ---
    from .routes import main_bp
    app.register_blueprint(main_bp)

    # Création des tables
    with app.app_context():
        db.create_all()

    return app