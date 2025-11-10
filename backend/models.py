# backend/models.py
"""
SQLAlchemy models matching the actual CSV structure.
CSVs are the source of truth.
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Sector(db.Model):
    __tablename__ = "sectors"
    
    id = db.Column(db.Integer, primary_key=True)  # Matches CSV: 'id'
    sector_name = db.Column(db.Text, unique=True, nullable=False)
    description = db.Column(db.Text)
    
    # Relationships
    companies = db.relationship("Company", back_populates="sector", lazy='dynamic')
    sector_metrics = db.relationship("SectorMetric", back_populates="sector", lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'sector_name': self.sector_name,
            'description': self.description
        }

class Metric(db.Model):
    __tablename__ = "metrics"
    
    metric_id = db.Column(db.Integer, primary_key=True)
    metric_name = db.Column(db.Text, unique=True, nullable=False)
    unit = db.Column(db.Text)
    invert_score = db.Column(db.Boolean, default=False)  # FALSE = higher is better
    description = db.Column(db.Text)
    source = db.Column(db.Text)
    
    # Relationships
    sector_metrics = db.relationship("SectorMetric", back_populates="metric", lazy='dynamic')
    company_metrics = db.relationship("CompanyMetric", back_populates="metric", lazy='dynamic')
    
    def to_dict(self):
        return {
            'metric_id': self.metric_id,
            'metric_name': self.metric_name,
            'unit': self.unit,
            'invert_score': self.invert_score,
            'description': self.description,
            'source': self.source
        }

class SectorMetric(db.Model):
    __tablename__ = "sector_metrics"
    
    sector_metric_id = db.Column(db.Integer, primary_key=True)
    sector_id = db.Column(db.Integer, db.ForeignKey("sectors.id"), nullable=False)
    metric_id = db.Column(db.Integer, db.ForeignKey("metrics.metric_id"), nullable=False)
    weight = db.Column(db.Numeric, default=0.0)
    
    # Relationships
    sector = db.relationship("Sector", back_populates="sector_metrics")
    metric = db.relationship("Metric", back_populates="sector_metrics")
    
    def to_dict(self):
        return {
            'sector_metric_id': self.sector_metric_id,
            'sector_id': self.sector_id,
            'metric_id': self.metric_id,
            'weight': float(self.weight) if self.weight else 0.0
        }

class Company(db.Model):
    __tablename__ = "companies"
    
    company_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    sector_id = db.Column(db.Integer, db.ForeignKey("sectors.id"))
    turnover = db.Column(db.Numeric)
    country = db.Column(db.Text)
    description = db.Column(db.Text)
    website = db.Column(db.Text)
    
    # Relationships
    sector = db.relationship("Sector", back_populates="companies")
    metrics = db.relationship("CompanyMetric", back_populates="company", lazy='dynamic')
    score = db.relationship("Score", back_populates="company", uselist=False)  # One score per company
    
    def to_dict(self, include_score=True):
        result = {
            'company_id': self.company_id,
            'name': self.name,
            'sector_id': self.sector_id,
            'sector_name': self.sector.sector_name if self.sector else None,
            'turnover': float(self.turnover) if self.turnover else None,
            'country': self.country,
            'description': self.description,
            'website': self.website
        }
        
        if include_score and self.score:
            result['sector_score'] = float(self.score.sector_score) if self.score.sector_score else None
            result['global_score'] = float(self.score.global_score) if self.score.global_score else None
            result['last_calculated'] = self.score.last_calculated.isoformat() if self.score.last_calculated else None
        
        return result
    
    def to_dict_detailed(self):
        """Detailed view with all metrics"""
        result = self.to_dict(include_score=True)
        
        # Add all metrics
        metrics_list = []
        for cm in self.metrics:
            metrics_list.append({
                'metric_id': cm.metric_id,
                'metric_name': cm.metric.metric_name,
                'value': float(cm.value) if cm.value else None,
                'unit': cm.metric.unit,
                'year': cm.year
            })
        
        result['metrics'] = metrics_list
        return result

class CompanyMetric(db.Model):
    __tablename__ = "company_metrics"
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.company_id"), nullable=False)
    metric_id = db.Column(db.Integer, db.ForeignKey("metrics.metric_id"), nullable=False)
    value = db.Column(db.Numeric)
    year = db.Column(db.Integer)
    
    # Relationships
    company = db.relationship("Company", back_populates="metrics")
    metric = db.relationship("Metric", back_populates="company_metrics")
    
    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'metric_id': self.metric_id,
            'metric_name': self.metric.metric_name if self.metric else None,
            'value': float(self.value) if self.value else None,
            'unit': self.metric.unit if self.metric else None,
            'year': self.year
        }

class Score(db.Model):
    __tablename__ = "scores"
    
    score_id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.company_id"), nullable=False, unique=True)
    sector_score = db.Column(db.Numeric)
    global_score = db.Column(db.Numeric)
    last_calculated = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    company = db.relationship("Company", back_populates="score")
    
    def to_dict(self):
        return {
            'score_id': self.score_id,
            'company_id': self.company_id,
            'company_name': self.company.name if self.company else None,
            'sector_score': float(self.sector_score) if self.sector_score else None,
            'global_score': float(self.global_score) if self.global_score else None,
            'last_calculated': self.last_calculated.isoformat() if self.last_calculated else None
        }
