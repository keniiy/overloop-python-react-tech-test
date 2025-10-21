import json
from flask import Blueprint, jsonify, request
from pydantic import ValidationError as PydanticValidationError
from flask_apispec import marshal_with, doc
from marshmallow import Schema, fields

from api.dependencies import with_services, get_author_service
from schemas.author_schemas import CreateAuthorRequest, UpdateAuthorRequest
from schemas.pagination_schemas import PaginationMetaSchema, AuthorFilterParamsSchema
from core.exceptions import NotFoundError, ValidationError
from core.pagination import get_pagination_params, get_search_params, PaginatedResponse

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

class PaginatedAuthorListSchema(Schema):
    data = fields.List(fields.Nested(AuthorSchema), required=True)
    pagination = fields.Nested(PaginationMetaSchema, required=True)


class ErrorSchema(Schema):
    error = fields.Str(required=True, metadata={"description": "Error message"})


class AuthorSuccessMessageSchema(Schema):
    message = fields.Str(required=True, metadata={"description": "Success message"})


@authors_bp.route('/authors', methods=['GET'])
@doc(
    description='Get all authors with pagination and optional search',
    tags=['Authors'],
    params={
        'page': {
            'description': 'Page number (1-based)',
            'type': 'integer',
            'required': False,
            'default': 1
        },
        'limit': {
            'description': 'Items per page (1-100)',
            'type': 'integer', 
            'required': False,
            'default': 20
        },
        'search': {
            'description': 'Search term to filter authors by name',
            'type': 'string',
            'required': False
        }
    },
    responses={
        200: {
            'description': 'Paginated list of authors',
            'schema': PaginatedAuthorListSchema
        },
        400: {
            'description': 'Bad request - invalid parameters',
            'schema': ErrorSchema
        },
        500: {
            'description': 'Internal server error',
            'schema': ErrorSchema
        }
    }
)
@marshal_with(PaginatedAuthorListSchema)
@with_services
def get_authors():
    """Get all authors with pagination"""
    # Get and validate pagination parameters
    pagination = get_pagination_params()
    search = get_search_params()
    
    author_service = get_author_service()
    
    # Get paginated results
    if search.search:
        authors, total = author_service.search_authors_paginated(
            search.search, pagination.offset, pagination.limit
        )
    else:
        authors, total = author_service.get_all_authors_paginated(
            pagination.offset, pagination.limit
        )
    
    # Convert to dict and create paginated response
    author_data = [author.model_dump() for author in authors]
    return PaginatedResponse.create(
        data=author_data,
        total=total,
        page=pagination.page,
        limit=pagination.limit,
        search=search.search
    )


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
@marshal_with(AuthorSchema, code=201)
@with_services
def create_author():
    """Create new author with Pydantic validation"""
    try:
        if not request.is_json:
            raise ValidationError('Request must be JSON')

        payload = request.get_json(silent=True)
        if payload is None:
            raise ValidationError('Request must be JSON')

        # Validate request data with Pydantic
        try:
            author_request = CreateAuthorRequest.model_validate(payload)
        except PydanticValidationError as e:
            raise ValidationError('Validation failed', {'details': json.loads(e.json())})
        
        author_service = get_author_service()
        author = author_service.create_author(author_request)
        
        return author.model_dump(), 201
    
    except ValueError as e:
        raise ValidationError(str(e))


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
    author_service = get_author_service()
    author = author_service.get_author_by_id(author_id)
    
    if not author:
        raise NotFoundError('Author not found')
    
    return author.model_dump()


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
@marshal_with(AuthorSchema)
@with_services
def update_author(author_id):
    """Update author"""
    if not request.is_json:
        raise ValidationError('Request must be JSON')

    payload = request.get_json(silent=True)
    if payload is None:
        raise ValidationError('Request must be JSON')

    # Create Pydantic model from kwargs
    try:
        author_request = UpdateAuthorRequest.model_validate(payload)
    except PydanticValidationError as e:
        raise ValidationError('Validation failed', {'details': json.loads(e.json())})
        
    author_service = get_author_service()
    
    try:
        author = author_service.update_author(author_id, author_request)
    except ValueError as e:
        raise ValidationError(str(e))
    
    if not author:
        raise NotFoundError('Author not found')

    return author.model_dump()


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
            'schema': AuthorSuccessMessageSchema
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
@marshal_with(AuthorSuccessMessageSchema)
@with_services
def delete_author(author_id):
    """Delete author"""
    try:
        author_service = get_author_service()
        
        if author_service.delete_author(author_id):
            return {'message': 'Author deleted successfully'}
        else:
            raise NotFoundError('Author not found')
    
    except ValueError as e:
        raise ValidationError(str(e))


@authors_bp.route('/authors/with-stats', methods=['GET'])
@with_services
def get_authors_with_stats():
    """Get all authors with article count"""
    author_service = get_author_service()
    authors = author_service.get_authors_with_article_count()
    return authors
