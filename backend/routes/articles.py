from flask import Blueprint, jsonify, request

from api.dependencies import with_services, get_article_service

articles_bp = Blueprint('articles', __name__)


@articles_bp.route('/articles', methods=['GET'])
@with_services
def get_articles():
    """Get all articles with author and regions"""
    try:
        search_term = request.args.get('search', '').strip()
        author_id = request.args.get('author_id', type=int)
        region_id = request.args.get('region_id', type=int)
        
        article_service = get_article_service()
        
        if author_id:
            articles = article_service.get_articles_by_author(author_id)
        elif region_id:
            articles = article_service.get_articles_by_region(region_id)
        elif search_term:
            articles = article_service.search_articles(search_term)
        else:
            articles = article_service.get_all_articles()
        
        return jsonify(articles)
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@articles_bp.route('/articles', methods=['POST'])
@with_services
def create_article():
    """Create new article with author and regions"""
    try:
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400
        
        article_data = request.get_json()
        article_service = get_article_service()
        
        article = article_service.create_article(article_data)
        return jsonify(article), 201
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@articles_bp.route('/articles/<int:article_id>', methods=['GET'])
@with_services
def get_article(article_id):
    """Get article by ID with author and regions"""
    try:
        article_service = get_article_service()
        article = article_service.get_article_by_id(article_id)
        
        if not article:
            return jsonify({'error': 'Article not found'}), 404
        
        return jsonify(article)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@articles_bp.route('/articles/<int:article_id>', methods=['PUT'])
@with_services
def update_article(article_id):
    """Update article with author and regions"""
    try:
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400
        
        article_data = request.get_json()
        article_service = get_article_service()
        
        article = article_service.update_article(article_id, article_data)
        
        if not article:
            return jsonify({'error': 'Article not found'}), 404
        
        return jsonify(article)
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@articles_bp.route('/articles/<int:article_id>', methods=['DELETE'])
@with_services
def delete_article(article_id):
    """Delete article"""
    try:
        article_service = get_article_service()
        
        if article_service.delete_article(article_id):
            return jsonify({'message': 'Article deleted successfully'})
        else:
            return jsonify({'error': 'Article not found'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
