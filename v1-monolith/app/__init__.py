from flask import Flask
from .models import db, User
from flask_login import LoginManager
import os # <--- NOUVEL IMPORT IMPORTANT

def create_app():
    app = Flask(__name__)

    # --- CONFIGURATION INTELLIGENTE ---
    # On cherche une variable d'environnement 'DATABASE_URL' (qui sera fournie par K8s)
    # Si elle n'existe pas, on utilise SQLite par défaut (pour ton dev local)
    db_url = os.environ.get('DATABASE_URL', 'sqlite:///cybermanager.db')
    
    # Petit correctif pour SQLAlchemy si l'URL commence par "mysql://" (il préfère "mysql+pymysql://")
    if db_url.startswith("mysql://"):
        db_url = db_url.replace("mysql://", "mysql+pymysql://")

    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'dev-cle-secrete'

    # ... Le reste du fichier ne change pas ...
    db.init_app(app)
    
    login_manager = LoginManager()
    login_manager.login_view = 'main.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .routes import main_bp
    app.register_blueprint(main_bp)

    with app.app_context():
        db.create_all()

    return app