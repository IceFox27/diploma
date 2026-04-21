from flask import Flask

from .extensions import db, migrate, login_manager
from .config import Config

from .routes.main import main 
from .routes.employee import employee 
from .routes.project import project_bp
from .routes.work import work_bp  # ← ДОБАВЛЕН ИМПОРТ

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    app.register_blueprint(main)
    app.register_blueprint(employee) 
    app.register_blueprint(project_bp)
    app.register_blueprint(work_bp)  # ← ДОБАВЛЕНА РЕГИСТРАЦИЯ

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Указывает, куда перенаправлять неавторизованного пользователя.
    login_manager.login_view = 'employee.login'
    login_manager.login_message = 'Вы не можете получить доступ к данной странице. Вам необходимо войти.'
    login_manager.login_message_category = 'info'

    with app.app_context():
        db.create_all() 

    return app