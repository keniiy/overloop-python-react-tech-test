from flask import Flask, jsonify
import os
from dotenv import load_dotenv
from flask_apispec import FlaskApiSpec, marshal_with, doc
from marshmallow import Schema, fields
from flask_cors import CORS

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config.update({
    'SECRET_KEY': 'dev-secret-key',
    'DATABASE_URL': os.environ.get('DATABASE_URL', 'sqlite:///database.db'),
    'TESTING': False,
    'DEBUG': os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
})

# Enable CORS
CORS(app)

# Initialize API documentation
docs = FlaskApiSpec(document_options=False)
docs.init_app(app)

# Import and register existing blueprints
from routes.authors import authors_bp
from routes.articles import articles_bp
from routes.regions import regions_bp

app.register_blueprint(authors_bp)
app.register_blueprint(articles_bp)
app.register_blueprint(regions_bp)


# Schema definitions
class HealthResponseSchema(Schema):
    class Meta:
        strict = True

    status = fields.Str(
        required=True,
        metadata={"description": "API health status", "example": "healthy"}
    )
    message = fields.Str(
        required=True,
        metadata={"description": "Health check message", "example": "API is running"}
    )
    version = fields.Str(
        required=True,
        metadata={"description": "API version", "example": "v1"}
    )


@app.route('/health')
@doc(
    description='Health check endpoint to verify API is running',
    tags=['System'],
    responses={
        200: {
            'description': 'API is healthy',
            'schema': HealthResponseSchema,
            'examples': {
                'application/json': {
                    'status': 'healthy',
                    'message': 'API is running',
                    'version': 'v1'
                }
            }
        }
    }
)
@marshal_with(HealthResponseSchema)
def health():
    """Get API health status

    Returns the current health status of the API including:
    - Service status
    - Confirmation message
    - API version
    """
    return {
        'status': 'healthy',
        'message': 'API is running',
        'version': 'v1'
    }


docs.register(health)

# Register all blueprint endpoints with documentation
from routes.authors import get_authors, create_author, get_author, update_author, delete_author
docs.register(get_authors, blueprint='authors')
docs.register(create_author, blueprint='authors')
docs.register(get_author, blueprint='authors')
docs.register(update_author, blueprint='authors')
docs.register(delete_author, blueprint='authors')


@app.route('/swagger/')
def swagger_spec():
    """Return swagger spec"""
    from flask import current_app
    return jsonify(current_app.extensions['flask-apispec'].spec.to_dict())


@app.route('/docs/')
def swagger_ui():
    """Swagger UI documentation"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>API Documentation</title>
        <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@3.25.0/swagger-ui.css" />
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="https://unpkg.com/swagger-ui-dist@3.25.0/swagger-ui-bundle.js"></script>
        <script>
            SwaggerUIBundle({
                url: '/swagger/',
                dom_id: '#swagger-ui',
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIBundle.presets.standalone
                ]
            });
        </script>
    </body>
    </html>
    '''


def _get_port():
    # allow common env vars to override the default Flask port
    # prefer API_PORT (project .env), then PORT, then FLASK_RUN_PORT
    port = os.environ.get('API_PORT') or os.environ.get('PORT') or os.environ.get('FLASK_RUN_PORT')
    try:
        return int(port) if port else 5000
    except ValueError:
        return 5000


if __name__ == '__main__':
    debug = os.environ.get('FLASK_DEBUG', '0') not in ('0', 'false', 'False')
    app.run(host='0.0.0.0', port=_get_port(), debug=debug)
