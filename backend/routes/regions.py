import json
from flask import Blueprint, request
from pydantic import ValidationError as PydanticValidationError
from flask_apispec import marshal_with, doc, use_kwargs
from marshmallow import Schema, fields

from api.dependencies import with_services, get_region_service
from schemas.region_schemas import CreateRegionRequest, UpdateRegionRequest
from schemas.pagination_schemas import PaginationMetaSchema, RegionFilterParamsSchema
from core.exceptions import NotFoundError, ValidationError
from core.pagination import PaginatedResponse

regions_bp = Blueprint('regions', __name__)


# Marshmallow schemas for API documentation
class RegionSchema(Schema):
    id = fields.Int(required=True, metadata={"description": "Region's unique identifier"})
    code = fields.Str(required=True, metadata={"description": "Two-letter region code"})
    name = fields.Str(required=True, metadata={"description": "Region name"})


class CreateRegionSchema(Schema):
    code = fields.Str(required=True, metadata={"description": "Two-letter region code"})
    name = fields.Str(required=True, metadata={"description": "Region name"})


class UpdateRegionSchema(Schema):
    code = fields.Str(required=False, metadata={"description": "Two-letter region code"})
    name = fields.Str(required=False, metadata={"description": "Region name"})


class PaginatedRegionListSchema(Schema):
    data = fields.List(fields.Nested(RegionSchema), required=True)
    pagination = fields.Nested(PaginationMetaSchema, required=True)


class RegionErrorSchema(Schema):
    error = fields.Str(required=True, metadata={"description": "Error message"})


class RegionSuccessMessageSchema(Schema):
    message = fields.Str(required=True, metadata={"description": "Success message"})


@regions_bp.route('/regions', methods=['GET'])
@doc(
    description='Get all regions with pagination and optional search',
    tags=['Regions'],
    responses={
        200: {
            'description': 'Paginated list of regions',
            'schema': PaginatedRegionListSchema
        },
        400: {
            'description': 'Bad request - invalid parameters',
            'schema': RegionErrorSchema
        },
        500: {
            'description': 'Internal server error',
            'schema': RegionErrorSchema
        }
    }
)
@use_kwargs(RegionFilterParamsSchema, location="query")
@marshal_with(PaginatedRegionListSchema)
@with_services
def get_regions(**kwargs):
    """Get all regions with pagination"""
    # Extract parameters from kwargs (comes from @use_kwargs)
    page = kwargs.get('page', 1)
    limit = kwargs.get('limit', 20)
    search = kwargs.get('search')

    # Calculate offset
    offset = (page - 1) * limit

    region_service = get_region_service()

    # Get paginated results
    if search:
        regions, total = region_service.search_regions_paginated(
            search, offset, limit
        )
    else:
        regions, total = region_service.get_all_regions_paginated(
            offset, limit
        )

    # Create paginated response
    return PaginatedResponse.create(
        data=regions,
        total=total,
        page=page,
        limit=limit,
        search=search
    )


@regions_bp.route('/regions', methods=['POST'])
@doc(
    description='Create a new region',
    tags=['Regions'],
    responses={
        201: {
            'description': 'Region created successfully',
            'schema': RegionSchema
        },
        400: {
            'description': 'Bad request - validation failed',
            'schema': RegionErrorSchema
        },
        500: {
            'description': 'Internal server error',
            'schema': RegionErrorSchema
        }
    }
)
@marshal_with(RegionSchema, code=201)
@with_services
def create_region():
    """Create new region with Pydantic validation"""
    try:
        if not request.is_json:
            raise ValidationError('Request must be JSON')

        payload = request.get_json(silent=True)
        if payload is None:
            raise ValidationError('Request must be JSON')

        # Validate request data with Pydantic
        try:
            region_request = CreateRegionRequest.model_validate(payload)
        except PydanticValidationError as e:
            raise ValidationError('Validation failed', {'details': json.loads(e.json())})

        region_service = get_region_service()
        region = region_service.create_region(region_request)

        return region, 201

    except ValueError as e:
        raise ValidationError(str(e))


@regions_bp.route('/regions/<int:region_id>', methods=['GET'])
@doc(
    description='Get a single region by ID',
    tags=['Regions'],
    params={
        'region_id': {
            'description': 'Region ID',
            'type': 'integer',
            'required': True
        }
    },
    responses={
        200: {
            'description': 'Region details',
            'schema': RegionSchema
        },
        404: {
            'description': 'Region not found',
            'schema': RegionErrorSchema
        },
        500: {
            'description': 'Internal server error',
            'schema': RegionErrorSchema
        }
    }
)
@marshal_with(RegionSchema)
@with_services
def get_region(region_id):
    """Get region by ID"""
    region_service = get_region_service()
    region = region_service.get_region_by_id(region_id)

    if not region:
        raise NotFoundError('Region not found')

    return region


@regions_bp.route('/regions/<int:region_id>', methods=['PUT'])
@doc(
    description='Update a single region',
    tags=['Regions'],
    params={
        'region_id': {
            'description': 'Region ID',
            'type': 'integer',
            'required': True
        }
    },
    responses={
        200: {
            'description': 'Region updated successfully',
            'schema': RegionSchema
        },
        400: {
            'description': 'Bad request - validation failed',
            'schema': RegionErrorSchema
        },
        404: {
            'description': 'Region not found',
            'schema': RegionErrorSchema
        },
        500: {
            'description': 'Internal server error',
            'schema': RegionErrorSchema
        }
    }
)
@marshal_with(RegionSchema)
@with_services
def update_region(region_id):
    """Update region"""
    if not request.is_json:
        raise ValidationError('Request must be JSON')

    # Create Pydantic model from kwargs
    try:
        payload = request.get_json(silent=True)
        if payload is None:
            raise ValidationError('Request must be JSON')
        region_request = UpdateRegionRequest.model_validate(payload)
    except PydanticValidationError as e:
        raise ValidationError('Validation failed', {'details': e.errors()})

    region_service = get_region_service()

    try:
        region = region_service.update_region(region_id, region_request)
    except ValueError as e:
        raise ValidationError(str(e))

    if not region:
        raise NotFoundError('Region not found')

    return region


@regions_bp.route('/regions/<int:region_id>', methods=['DELETE'])
@doc(
    description='Delete a single region',
    tags=['Regions'],
    params={
        'region_id': {
            'description': 'Region ID',
            'type': 'integer',
            'required': True
        }
    },
    responses={
        200: {
            'description': 'Region deleted successfully',
            'schema': RegionSuccessMessageSchema
        },
        404: {
            'description': 'Region not found',
            'schema': RegionErrorSchema
        },
        400: {
            'description': 'Bad request',
            'schema': RegionErrorSchema
        },
        500: {
            'description': 'Internal server error',
            'schema': RegionErrorSchema
        }
    }
)
@marshal_with(RegionSuccessMessageSchema)
@with_services
def delete_region(region_id):
    """Delete region"""
    try:
        region_service = get_region_service()

        if region_service.delete_region(region_id):
            return {'message': 'Region deleted successfully'}
        else:
            raise NotFoundError('Region not found')

    except ValueError as e:
        raise ValidationError(str(e))
