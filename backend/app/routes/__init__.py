from .transit import transit_bp
from .business import business_bp
from .zones import zones_bp

def register_blueprints(app):
    """Register all route blueprints"""
    app.register_blueprint(transit_bp, url_prefix="/transit")
    app.register_blueprint(business_bp, url_prefix="/business")
    app.register_blueprint(zones_bp, url_prefix="/zones")
