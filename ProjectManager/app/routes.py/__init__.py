from .project_routes import project_bp
from .task_routes import task_bp

def register_routes(app):
    app.register_blueprint(project_bp)
    app.register_blueprint(task_bp)
