from flask import Blueprint, jsonify, request
from pydantic import ValidationError
from flask_apispec import marshal_with, doc, use_kwargs
from marshmallow import Schema, fields

from api.dependencies import with_services, get_author_service
from schemas.author_schemas import CreateAuthorRequest, UpdateAuthorRequest

authors_bp = Blueprint('authors', __name__)


# Marshmallow schemas for API documentation
class AuthorSchema(Schema):
    id = fields.Int(required=True, metadata={"description": "Author's unique identifier"})
    first_name = fields.Str(required=True, metadata={"description": "Author's first name"})
    last_name = fields.Str(required=True, metadata={"description": "Author's last name"})
    full_name = fields.Str(required=True, metadata={"description": "Author's full name"})


class CreateAuthorSchema(Schema):
    first_name = fields.Str(required=True, metadata={"description": "Author's first name"})
    last_name = fields.Str(required=True, metadata={"description": "Author's last name"})


class UpdateAuthorSchema(Schema):
    first_name = fields.Str(required=False, metadata={"description": "Author's first name"})
    last_name = fields.Str(required=False, metadata={"description": "Author's last name"})


class AuthorListSchema(Schema):
    authors = fields.List(fields.Nested(AuthorSchema), required=True)


class ErrorSchema(Schema):
    error = fields.Str(required=True, metadata={"description": "Error message"})


class SuccessMessageSchema(Schema):
    message = fields.Str(required=True, metadata={"description": "Success message"})


@authors_bp.route('/authors', methods=['GET'])
@doc(
    description='Get all authors with optional search functionality',
    tags=['Authors'],
    params={
        'search': {
            'description': 'Search term to filter authors by name',
            'type': 'string',
            'required': False
        }
    },
    responses={
        200: {
            'description': 'List of authors',
            'schema': AuthorListSchema
        },
        500: {
            'description': 'Internal server error',
            'schema': ErrorSchema
        }
    }
)
@marshal_with(AuthorListSchema)
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
        return {
            'authors': [author.model_dump() for author in authors]
        }
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@authors_bp.route('/authors', methods=['POST'])
@doc(
    description='Create a new author',
    tags=['Authors'],
    responses={
        201: {
            'description': 'Author created successfully',
            'schema': AuthorSchema
        },
        400: {
            'description': 'Bad request - validation failed',
            'schema': ErrorSchema
        },
        500: {
            'description': 'Internal server error',
            'schema': ErrorSchema
        }
    }
)
@use_kwargs(CreateAuthorSchema, location="json")
@marshal_with(AuthorSchema, code=201)
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
        
        return author.model_dump(), 201
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@authors_bp.route('/authors/<int:author_id>', methods=['GET'])
@doc(
    description='Get a single author by ID',
    tags=['Authors'],
    params={
        'author_id': {
            'description': 'Author ID',
            'type': 'integer',
            'required': True
        }
    },
    responses={
        200: {
            'description': 'Author details',
            'schema': AuthorSchema
        },
        404: {
            'description': 'Author not found',
            'schema': ErrorSchema
        },
        500: {
            'description': 'Internal server error',
            'schema': ErrorSchema
        }
    }
)
@marshal_with(AuthorSchema)
@with_services
def get_author(author_id):
    """Get author by ID"""
    try:
        author_service = get_author_service()
        author = author_service.get_author_by_id(author_id)
        
        if not author:
            return jsonify({'error': 'Author not found'}), 404
        
        return author.model_dump()
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@authors_bp.route('/authors/<int:author_id>', methods=['PUT'])
@doc(
    description='Update a single author',
    tags=['Authors'],
    params={
        'author_id': {
            'description': 'Author ID',
            'type': 'integer',
            'required': True
        }
    },
    responses={
        200: {
            'description': 'Author updated successfully',
            'schema': AuthorSchema
        },
        400: {
            'description': 'Bad request - validation failed',
            'schema': ErrorSchema
        },
        404: {
            'description': 'Author not found',
            'schema': ErrorSchema
        },
        500: {
            'description': 'Internal server error',
            'schema': ErrorSchema
        }
    }
)
@use_kwargs(UpdateAuthorSchema, location="json")
@marshal_with(AuthorSchema)
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
        
        return author
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@authors_bp.route('/authors/<int:author_id>', methods=['DELETE'])
@doc(
    description='Delete a single author',
    tags=['Authors'],
    params={
        'author_id': {
            'description': 'Author ID',
            'type': 'integer',
            'required': True
        }
    },
    responses={
        200: {
            'description': 'Author deleted successfully',
            'schema': SuccessMessageSchema
        },
        404: {
            'description': 'Author not found',
            'schema': ErrorSchema
        },
        400: {
            'description': 'Bad request',
            'schema': ErrorSchema
        },
        500: {
            'description': 'Internal server error',
            'schema': ErrorSchema
        }
    }
)
@marshal_with(SuccessMessageSchema)
@with_services
def delete_author(author_id):
    """Delete author"""
    try:
        author_service = get_author_service()
        
        if author_service.delete_author(author_id):
            return {'message': 'Author deleted successfully'}
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