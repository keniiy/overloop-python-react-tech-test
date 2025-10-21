from flask import Blueprint, jsonify, request

from techtest.api.dependencies import with_services, get_region_service

regions_bp = Blueprint('regions', __name__)


@regions_bp.route('/regions', methods=['GET'])
@with_services
def get_regions():
    """Get all regions"""
    try:
        search_term = request.args.get('search', '').strip()
        region_service = get_region_service()
        
        if search_term:
            regions = region_service.search_regions(search_term)
        else:
            regions = region_service.get_all_regions()
        
        return jsonify(regions)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@regions_bp.route('/regions', methods=['POST'])
@with_services
def create_region():
    """Create new region"""
    try:
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400
        
        region_data = request.get_json()
        region_service = get_region_service()
        
        region = region_service.create_region(region_data)
        return jsonify(region), 201
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@regions_bp.route('/regions/<int:region_id>', methods=['GET'])
@with_services
def get_region(region_id):
    """Get region by ID"""
    try:
        region_service = get_region_service()
        region = region_service.get_region_by_id(region_id)
        
        if not region:
            return jsonify({'error': 'Region not found'}), 404
        
        return jsonify(region)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@regions_bp.route('/regions/<int:region_id>', methods=['PUT'])
@with_services
def update_region(region_id):
    """Update region"""
    try:
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400
        
        region_data = request.get_json()
        region_service = get_region_service()
        
        region = region_service.update_region(region_id, region_data)
        
        if not region:
            return jsonify({'error': 'Region not found'}), 404
        
        return jsonify(region)
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@regions_bp.route('/regions/<int:region_id>', methods=['DELETE'])
@with_services
def delete_region(region_id):
    """Delete region"""
    try:
        region_service = get_region_service()
        
        if region_service.delete_region(region_id):
            return jsonify({'message': 'Region deleted successfully'})
        else:
            return jsonify({'error': 'Region not found'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
