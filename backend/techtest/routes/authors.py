from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from techtest.api.dependencies import with_services, get_author_service
from techtest.schemas.author_schemas import CreateAuthorRequest, UpdateAuthorRequest

authors_bp = Blueprint('authors', __name__)


@authors_bp.route('/authors', methods=['GET'])
@with_services
def get_authors():
    """Get all authors"""
    try:
        search_term = request.args.get('search', '').strip()
        author_service = get_author_service()
        
        if search_term:
            authors = author_service.search_authors(search_term)
        else:
            authors = author_service.get_all_authors()
        
        # Convert Pydantic models to dict for JSON response
        return jsonify([author.model_dump() for author in authors])
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@authors_bp.route('/authors', methods=['POST'])
@with_services
def create_author():
    """Create new author with Pydantic validation"""
    try:
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400
        
        # Validate request data with Pydantic
        try:
            author_request = CreateAuthorRequest.model_validate(request.get_json())
        except ValidationError as e:
            return jsonify({'error': 'Validation failed', 'details': e.errors()}), 400
        
        author_service = get_author_service()
        author = author_service.create_author(author_request)
        
        return jsonify(author.model_dump()), 201
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@authors_bp.route('/authors/<int:author_id>', methods=['GET'])
@with_services
def get_author(author_id):
    """Get author by ID"""
    try:
        author_service = get_author_service()
        author = author_service.get_author_by_id(author_id)
        
        if not author:
            return jsonify({'error': 'Author not found'}), 404
        
        return jsonify(author.model_dump())
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@authors_bp.route('/authors/<int:author_id>', methods=['PUT'])
@with_services
def update_author(author_id):
    """Update author"""
    try:
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400
        
        author_data = request.get_json()
        author_service = get_author_service()
        
        author = author_service.update_author(author_id, author_data)
        
        if not author:
            return jsonify({'error': 'Author not found'}), 404
        
        return jsonify(author)
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@authors_bp.route('/authors/<int:author_id>', methods=['DELETE'])
@with_services
def delete_author(author_id):
    """Delete author"""
    try:
        author_service = get_author_service()
        
        if author_service.delete_author(author_id):
            return jsonify({'message': 'Author deleted successfully'})
        else:
            return jsonify({'error': 'Author not found'}), 404
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@authors_bp.route('/authors/with-stats', methods=['GET'])
@with_services
def get_authors_with_stats():
    """Get all authors with article count"""
    try:
        author_service = get_author_service()
        authors = author_service.get_authors_with_article_count()
        return jsonify(authors)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500