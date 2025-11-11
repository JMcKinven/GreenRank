# backend/app.py
"""
Flask REST API for GreenRank sustainability scoring system.
Provides endpoints for companies, sectors, metrics, and scores.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS
from models import db, Sector, Metric, SectorMetric, Company, CompanyMetric, Score
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = SQLALCHEMY_TRACK_MODIFICATIONS
    
    # Enable CORS for frontend
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Initialize database
    db.init_app(app)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Resource not found"}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal error: {error}")
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500
    
    # ===== SECTORS ENDPOINTS =====
    
    @app.route("/api/sectors", methods=["GET"])
    def get_sectors():
        """Get all sectors"""
        try:
            sectors = Sector.query.all()
            return jsonify([s.to_dict() for s in sectors])
        except Exception as e:
            logger.error(f"Error fetching sectors: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route("/api/sectors/<int:sector_id>", methods=["GET"])
    def get_sector(sector_id):
        """Get single sector with its metrics"""
        try:
            sector = Sector.query.get_or_404(sector_id)
            result = sector.to_dict()
            
            # Add metrics for this sector
            sector_metrics = SectorMetric.query.filter_by(sector_id=sector_id).all()
            result['metrics'] = [sm.to_dict() for sm in sector_metrics]
            
            return jsonify(result)
        except Exception as e:
            logger.error(f"Error fetching sector {sector_id}: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route("/api/sectors/<int:sector_id>/leaderboard", methods=["GET"])
    def get_sector_leaderboard(sector_id):
        """Get ranked companies within a sector"""
        try:
            # Verify sector exists
            sector = Sector.query.get_or_404(sector_id)
            
            # Get all companies in sector with scores
            companies = Company.query.filter_by(sector_id=sector_id).all()
            
            results = []
            for comp in companies:
                data = comp.to_dict(include_score=True)
                results.append(data)
            
            # Sort by sector_score descending
            results.sort(key=lambda x: x.get('sector_score') or 0, reverse=True)
            
            # Add rank
            for i, company in enumerate(results, 1):
                company['rank'] = i
            
            return jsonify({
                'sector_id': sector_id,
                'sector_name': sector.sector_name,
                'companies': results
            })
        except Exception as e:
            logger.error(f"Error fetching leaderboard for sector {sector_id}: {e}")
            return jsonify({"error": str(e)}), 500
    
    # ===== METRICS ENDPOINTS =====
    
    @app.route("/api/metrics", methods=["GET"])
    def get_metrics():
        """Get all metrics"""
        try:
            metrics = Metric.query.all()
            return jsonify([m.to_dict() for m in metrics])
        except Exception as e:
            logger.error(f"Error fetching metrics: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route("/api/metrics/<int:metric_id>", methods=["GET"])
    def get_metric(metric_id):
        """Get single metric"""
        try:
            metric = Metric.query.get_or_404(metric_id)
            return jsonify(metric.to_dict())
        except Exception as e:
            logger.error(f"Error fetching metric {metric_id}: {e}")
            return jsonify({"error": str(e)}), 500
    
    # ===== COMPANIES ENDPOINTS =====
    
    @app.route("/api/companies", methods=["GET"])
    def get_companies():
        """
        Get all companies with optional filters.
        Query params:
        - sector_id: Filter by sector
        - limit: Limit results
        - offset: Pagination offset
        """
        try:
            # Build query
            query = Company.query
            
            # Apply sector filter
            sector_id = request.args.get("sector_id", type=int)
            if sector_id:
                query = query.filter_by(sector_id=sector_id)
            
            # Apply pagination
            limit = request.args.get("limit", type=int, default=100)
            offset = request.args.get("offset", type=int, default=0)
            
            # Get total count
            total = query.count()
            
            # Get paginated results
            companies = query.limit(limit).offset(offset).all()
            
            results = [c.to_dict(include_score=True) for c in companies]
            
            return jsonify({
                'total': total,
                'limit': limit,
                'offset': offset,
                'companies': results
            })
        except Exception as e:
            logger.error(f"Error fetching companies: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route("/api/companies/<int:company_id>", methods=["GET"])
    def get_company(company_id):
        """Get detailed company information with all metrics"""
        try:
            company = Company.query.get_or_404(company_id)
            return jsonify(company.to_dict_detailed())
        except Exception as e:
            logger.error(f"Error fetching company {company_id}: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route("/api/companies/search", methods=["GET"])
    def search_companies():
        """
        Search companies by name.
        Query params:
        - q: Search query (searches in company name)
        """
        try:
            query_str = request.args.get("q", "").strip()
            
            if not query_str:
                return jsonify({"error": "Search query 'q' is required"}), 400
            
            # Case-insensitive search
            companies = Company.query.filter(
                Company.name.ilike(f"%{query_str}%")
            ).limit(20).all()
            
            results = [c.to_dict(include_score=True) for c in companies]
            
            return jsonify({
                'query': query_str,
                'count': len(results),
                'companies': results
            })
        except Exception as e:
            logger.error(f"Error searching companies: {e}")
            return jsonify({"error": str(e)}), 500
    
    # ===== SCORES ENDPOINTS =====
    
    @app.route("/api/scores", methods=["GET"])
    def get_scores():
        """Get all scores with optional ranking"""
        try:
            # Optional: filter by top N
            limit = request.args.get("limit", type=int)
            
            query = Score.query.order_by(Score.sector_score.desc())
            
            if limit:
                query = query.limit(limit)
            
            scores = query.all()
            results = [s.to_dict() for s in scores]
            
            # Add rank
            for i, score in enumerate(results, 1):
                score['rank'] = i
            
            return jsonify(results)
        except Exception as e:
            logger.error(f"Error fetching scores: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route("/api/leaderboard", methods=["GET"])
    def get_global_leaderboard():
        """Get global leaderboard across all sectors"""
        try:
            limit = request.args.get("limit", type=int, default=290)
            
            # Get top scores with company info
            scores = Score.query.order_by(Score.sector_score.desc()).limit(limit).all()
            
            results = []
            for i, score in enumerate(scores, 1):
                company = Company.query.get(score.company_id)
                result = {
                    'rank': i,
                    'company_id': company.company_id,
                    'name': company.name,
                    'sector_id': company.sector_id,
                    'sector_name': company.sector.sector_name if company.sector else None,
                    'sector_score': float(score.sector_score) if score.sector_score else None,
                    'global_score': float(score.global_score) if score.global_score else None,
                    'turnover': float(company.turnover) if company.turnover else None
                }
                results.append(result)
            
            return jsonify(results)
        except Exception as e:
            logger.error(f"Error fetching leaderboard: {e}")
            return jsonify({"error": str(e)}), 500
    
    # ===== STATS ENDPOINTS =====
    
    @app.route("/api/stats", methods=["GET"])
    def get_stats():
        """Get overall statistics"""
        try:
            stats = {
                'total_companies': Company.query.count(),
                'total_sectors': Sector.query.count(),
                'total_metrics': Metric.query.count(),
                'companies_scored': Score.query.count(),
                'last_updated': db.session.query(Score.last_calculated).order_by(
                    Score.last_calculated.desc()
                ).first()
            }
            
            # Convert datetime to string
            if stats['last_updated']:
                stats['last_updated'] = stats['last_updated'][0].isoformat()
            
            return jsonify(stats)
        except Exception as e:
            logger.error(f"Error fetching stats: {e}")
            return jsonify({"error": str(e)}), 500
    
    # ===== HEALTH CHECK =====
    
    @app.route("/api/health", methods=["GET"])
    def health_check():
        """Health check endpoint"""
        try:
            # Test database connection
            db.session.execute('SELECT 1')
            return jsonify({
                'status': 'healthy',
                'database': 'connected'
            })
        except Exception as e:
            return jsonify({
                'status': 'unhealthy',
                'database': 'disconnected',
                'error': str(e)
            }), 500
    
    @app.route("/", methods=["GET"])
    def index():
        """API root"""
        return jsonify({
            'message': 'GreenRank API',
            'version': '1.0',
            'endpoints': {
                'sectors': '/api/sectors',
                'metrics': '/api/metrics',
                'companies': '/api/companies',
                'leaderboard': '/api/leaderboard',
                'stats': '/api/stats',
                'health': '/api/health'
            }
        })
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
