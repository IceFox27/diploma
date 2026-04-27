from flask import Flask

from .extensions import db, migrate, login_manager
from .config import Config

from .routes.main import main 
from .routes.employee import employee 
from .routes.project import project_bp
from .routes.work import work_bp  

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    app.register_blueprint(main)
    app.register_blueprint(employee) 
    app.register_blueprint(project_bp)
    app.register_blueprint(work_bp)  

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    login_manager.login_view = 'employee.login'
    login_manager.login_message = 'Вы не можете получить доступ к данной странице. Вам необходимо войти.'
    login_manager.login_message_category = 'info'

    return app