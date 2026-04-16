from flask import Flask

from .extensions import db, migrate
from .config import Config
from .routes.main import main 
from .routes.employee import employee  

from .models.salary import Salary
from .models.role import Role  
from .models.employee import Employee

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    
    app.register_blueprint(main)
    app.register_blueprint(employee)    

    with app.app_context():
        db.create_all() 

    return app