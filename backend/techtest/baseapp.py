from flask import Flask
from flask_cors import CORS


def create_app(config=None):
    """Application factory pattern for creating Flask app instances"""
    app = Flask('techtest')
    CORS(app)
    
    # Default configuration
    app.config.update({
        'DATABASE_URL': 'sqlite:///database.db',
        'TESTING': False,
        'DEBUG': False
    })
    
    # Override with provided config
    if config:
        app.config.update(config)
    
    # Register routes
    from techtest.routes.authors import authors_bp
    from techtest.routes.articles import articles_bp
    from techtest.routes.regions import regions_bp
    
    app.register_blueprint(authors_bp)
    app.register_blueprint(articles_bp)
    app.register_blueprint(regions_bp)
    
    return app


# Default app instance for backward compatibility
app = create_app()
