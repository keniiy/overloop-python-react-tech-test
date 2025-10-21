import json
from flask import Blueprint, request
from pydantic import ValidationError as PydanticValidationError
from flask_apispec import marshal_with, doc, use_kwargs
from marshmallow import Schema, fields

from api.dependencies import with_services, get_article_service
from schemas.article_schemas import CreateArticleRequest, UpdateArticleRequest
from schemas.pagination_schemas import PaginationMetaSchema, ArticleFilterParamsSchema
from core.exceptions import NotFoundError, ValidationError
from core.pagination import PaginatedResponse

articles_bp = Blueprint('articles', __name__)


# Marshmallow schemas for API documentation
class ArticleSchema(Schema):
    id = fields.Int(required=True, metadata={"description": "Article's unique identifier"})
    title = fields.Str(required=True, metadata={"description": "Article title"})
    content = fields.Str(required=True, metadata={"description": "Article content"})
    author_id = fields.Int(allow_none=True, metadata={"description": "Author's ID"})
    author = fields.Dict(allow_none=True, metadata={"description": "Author information"})
    regions = fields.List(fields.Dict(), metadata={"description": "Article regions"})


class CreateArticleSchema(Schema):
    title = fields.Str(required=True, metadata={"description": "Article title"})
    content = fields.Str(required=True, metadata={"description": "Article content"})
    author_id = fields.Int(allow_none=True, metadata={"description": "Author's ID"})
    region_ids = fields.List(fields.Int(), metadata={"description": "List of region IDs"})


class UpdateArticleSchema(Schema):
    title = fields.Str(required=False, metadata={"description": "Article title"})
    content = fields.Str(required=False, metadata={"description": "Article content"})
    author_id = fields.Int(allow_none=True, metadata={"description": "Author's ID"})
    region_ids = fields.List(fields.Int(), metadata={"description": "List of region IDs"})


class PaginatedArticleListSchema(Schema):
    data = fields.List(fields.Nested(ArticleSchema), required=True)
    pagination = fields.Nested(PaginationMetaSchema, required=True)


class ArticleErrorSchema(Schema):
    error = fields.Str(required=True, metadata={"description": "Error message"})


class ArticleSuccessMessageSchema(Schema):
    message = fields.Str(required=True, metadata={"description": "Success message"})


@articles_bp.route('/articles', methods=['GET'])
@doc(
    description='Get all articles with pagination and optional filtering',
    tags=['Articles'],
    responses={
        200: {
            'description': 'Paginated list of articles',
            'schema': PaginatedArticleListSchema
        },
        400: {
            'description': 'Bad request - invalid parameters',
            'schema': ArticleErrorSchema
        },
        500: {
            'description': 'Internal server error',
            'schema': ArticleErrorSchema
        }
    }
)
@use_kwargs(ArticleFilterParamsSchema, location="query")
@marshal_with(PaginatedArticleListSchema)
@with_services
def get_articles(**kwargs):
    """Get all articles with pagination and filtering"""
    # Extract parameters from kwargs (comes from @use_kwargs)
    page = kwargs.get('page', 1)
    limit = kwargs.get('limit', 20)
    search = kwargs.get('search')
    author_id = kwargs.get('author_id')
    region_id = kwargs.get('region_id')

    # Calculate offset
    offset = (page - 1) * limit

    article_service = get_article_service()

    # Get paginated results based on filters
    try:
        if author_id:
            articles, total = article_service.get_articles_by_author_paginated(
                author_id, offset, limit
            )
        elif region_id:
            articles, total = article_service.get_articles_by_region_paginated(
                region_id, offset, limit
            )
        elif search:
            articles, total = article_service.search_articles_paginated(
                search, offset, limit
            )
        else:
            articles, total = article_service.get_all_articles_paginated(
                offset, limit
            )
    except ValueError as e:
        raise ValidationError(str(e))

    # Create paginated response
    return PaginatedResponse.create(
        data=articles,
        total=total,
        page=page,
        limit=limit,
        search=search
    )


@articles_bp.route('/articles', methods=['POST'])
@doc(
    description='Create a new article',
    tags=['Articles'],
    responses={
        201: {
            'description': 'Article created successfully',
            'schema': ArticleSchema
        },
        400: {
            'description': 'Bad request - validation failed',
            'schema': ArticleErrorSchema
        },
        500: {
            'description': 'Internal server error',
            'schema': ArticleErrorSchema
        }
    }
)
@marshal_with(ArticleSchema, code=201)
@with_services
def create_article():
    """Create new article with Pydantic validation"""
    try:
        if not request.is_json:
            raise ValidationError('Request must be JSON')

        payload = request.get_json(silent=True)
        if payload is None:
            raise ValidationError('Request must be JSON')

        # Validate request data with Pydantic
        try:
            article_request = CreateArticleRequest.model_validate(payload)
        except PydanticValidationError as e:
            raise ValidationError('Validation failed', {'details': json.loads(e.json())})

        article_service = get_article_service()
        article = article_service.create_article(article_request)

        return article, 201

    except ValueError as e:
        raise ValidationError(str(e))


@articles_bp.route('/articles/<int:article_id>', methods=['GET'])
@doc(
    description='Get a single article by ID',
    tags=['Articles'],
    params={
        'article_id': {
            'description': 'Article ID',
            'type': 'integer',
            'required': True
        }
    },
    responses={
        200: {
            'description': 'Article details',
            'schema': ArticleSchema
        },
        404: {
            'description': 'Article not found',
            'schema': ArticleErrorSchema
        },
        500: {
            'description': 'Internal server error',
            'schema': ArticleErrorSchema
        }
    }
)
@marshal_with(ArticleSchema)
@with_services
def get_article(article_id):
    """Get article by ID"""
    article_service = get_article_service()
    article = article_service.get_article_by_id(article_id)

    if not article:
        raise NotFoundError('Article not found')

    return article


@articles_bp.route('/articles/<int:article_id>', methods=['PUT'])
@doc(
    description='Update a single article',
    tags=['Articles'],
    params={
        'article_id': {
            'description': 'Article ID',
            'type': 'integer',
            'required': True
        }
    },
    responses={
        200: {
            'description': 'Article updated successfully',
            'schema': ArticleSchema
        },
        400: {
            'description': 'Bad request - validation failed',
            'schema': ArticleErrorSchema
        },
        404: {
            'description': 'Article not found',
            'schema': ArticleErrorSchema
        },
        500: {
            'description': 'Internal server error',
            'schema': ArticleErrorSchema
        }
    }
)
@marshal_with(ArticleSchema)
@with_services
def update_article(article_id):
    """Update article"""
    if not request.is_json:
        raise ValidationError('Request must be JSON')

    # Create Pydantic model from kwargs
    try:
        payload = request.get_json(silent=True)
        if payload is None:
            raise ValidationError('Request must be JSON')
        article_request = UpdateArticleRequest.model_validate(payload)
    except PydanticValidationError as e:
        raise ValidationError('Validation failed', {'details': e.errors()})

    article_service = get_article_service()

    try:
        article = article_service.update_article(article_id, article_request)
    except ValueError as e:
        raise ValidationError(str(e))

    if not article:
        raise NotFoundError('Article not found')

    return article


@articles_bp.route('/articles/<int:article_id>', methods=['DELETE'])
@doc(
    description='Delete a single article',
    tags=['Articles'],
    params={
        'article_id': {
            'description': 'Article ID',
            'type': 'integer',
            'required': True
        }
    },
    responses={
        200: {
            'description': 'Article deleted successfully',
            'schema': ArticleSuccessMessageSchema
        },
        404: {
            'description': 'Article not found',
            'schema': ArticleErrorSchema
        },
        400: {
            'description': 'Bad request',
            'schema': ArticleErrorSchema
        },
        500: {
            'description': 'Internal server error',
            'schema': ArticleErrorSchema
        }
    }
)
@marshal_with(ArticleSuccessMessageSchema)
@with_services
def delete_article(article_id):
    """Delete article"""
    try:
        article_service = get_article_service()

        if article_service.delete_article(article_id):
            return {'message': 'Article deleted successfully'}
        else:
            raise NotFoundError('Article not found')

    except ValueError as e:
        raise ValidationError(str(e))
