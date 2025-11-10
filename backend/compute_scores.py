#!/usr/bin/env python3
# backend/compute_scores.py
"""
Compute sustainability scores for all companies.

Scoring Logic:
1. For each metric, normalize company value against sector distribution using z-scores
2. invert_score=FALSE means HIGHER is BETTER (renewable %, waste recycled %)
   invert_score=TRUE means LOWER is BETTER (not used in our data, but supported)
3. Compute weighted average of metric scores per sector
4. Calculate global percentile ranking
"""

import math
import statistics
from datetime import datetime
from sqlalchemy import and_
from models import db, Sector, Metric, SectorMetric, Company, CompanyMetric, Score
from app import create_app

def normal_cdf(z):
    """Standard normal cumulative distribution function"""
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))

def compute_metric_score(company_value, sector_values, invert_score=False):
    """
    Compute 0-100 score for a metric value relative to sector.
    
    Args:
        company_value: The company's value for this metric
        sector_values: List of all values for this metric in the sector
        invert_score: If FALSE, higher is better. If TRUE, lower is better.
    
    Returns:
        Score from 0-100, where 50 is average
    """
    # Handle empty sector data
    if not sector_values or all(v is None for v in sector_values):
        return 50.0  # Neutral if no comparison data
    
    # Convert to float and filter None
    vals = [float(v) for v in sector_values if v is not None]
    
    if len(vals) == 0:
        return 50.0
    
    mean = statistics.mean(vals)
    
    # Use sample standard deviation (more appropriate for smaller samples)
    if len(vals) > 1:
        std = statistics.stdev(vals)
    else:
        std = 0.0
    
    # If all values are identical, return 50 (average)
    if std == 0.0:
        return 50.0
    
    # Calculate z-score
    z = (company_value - mean) / std
    
    # Apply inversion logic
    # invert_score=FALSE: higher is better (renewable %, recycling %)
    # invert_score=TRUE: lower is better (emissions, waste)
    if invert_score:
        z = -z  # Flip so lower values get higher scores
    
    # Convert z-score to 0-100 scale using normal CDF
    score = normal_cdf(z) * 100.0
    
    # Clamp to 0-100 range
    return max(0.0, min(100.0, score))

def compute_all_scores():
    """
    Compute scores for all companies and save to database.
    """
    print("=" * 80)
    print("COMPUTING SUSTAINABILITY SCORES")
    print("=" * 80)
    
    all_company_sector_scores = {}  # company_id -> sector_score
    companies_processed = set()
    
    # Process each sector
    sectors = Sector.query.all()
    
    for sector in sectors:
        print(f"\n📊 Processing Sector {sector.id}: {sector.sector_name}")
        print("-" * 80)
        
        # Get metrics for this sector with their weights
        sec_metrics = SectorMetric.query.filter_by(sector_id=sector.id).all()
        
        if not sec_metrics:
            print(f"   ⚠️  No metrics defined for this sector")
            continue
        
        metric_ids = [sm.metric_id for sm in sec_metrics]
        weights_map = {sm.metric_id: float(sm.weight) for sm in sec_metrics}
        
        # Verify weights sum to ~1.0
        total_weight = sum(weights_map.values())
        print(f"   Total weight: {total_weight:.4f} (should be ~1.0)")
        
        # Gather sector-wide values for each metric
        sector_values = {}  # metric_id -> [values]
        
        for m_id in metric_ids:
            # Get all company metric values for this metric within the sector
            rows = db.session.query(CompanyMetric).join(Company).filter(
                and_(
                    Company.sector_id == sector.id,
                    CompanyMetric.metric_id == m_id,
                    CompanyMetric.value.isnot(None)
                )
            ).all()
            
            vals = [float(r.value) for r in rows]
            sector_values[m_id] = vals
            
            metric = Metric.query.get(m_id)
            print(f"   Metric {m_id:2d} ({metric.metric_name:30s}): {len(vals):3d} values")
        
        # Score each company in the sector
        companies_in_sector = Company.query.filter_by(sector_id=sector.id).all()
        print(f"\n   Scoring {len(companies_in_sector)} companies...")
        
        for comp in companies_in_sector:
            weighted_sum = 0.0
            weight_sum_present = 0.0
            metric_scores_debug = []
            
            for m_id in metric_ids:
                # Get company's value for this metric
                cm = CompanyMetric.query.filter_by(
                    company_id=comp.company_id,
                    metric_id=m_id
                ).first()
                
                if cm and cm.value is not None:
                    metric = Metric.query.get(m_id)
                    val = float(cm.value)
                    
                    # Compute score for this metric
                    m_score = compute_metric_score(
                        val,
                        sector_values[m_id],
                        invert_score=bool(metric.invert_score)
                    )
                    
                    # Apply weight
                    w = weights_map.get(m_id, 0.0)
                    weighted_sum += m_score * w
                    weight_sum_present += w
                    
                    metric_scores_debug.append(f"{metric.metric_name[:20]:20s} = {m_score:5.1f}")
            
            # Calculate final sector score
            if weight_sum_present > 0:
                sector_score = weighted_sum / weight_sum_present
            else:
                sector_score = None
            
            all_company_sector_scores[comp.company_id] = sector_score
            companies_processed.add(comp.company_id)
            
            # Debug output for first few companies
            if len(companies_processed) <= 3:
                print(f"\n   {comp.name[:40]:40s} Score: {sector_score:.2f if sector_score else 'N/A'}")
                for debug_line in metric_scores_debug[:3]:
                    print(f"      {debug_line}")
    
    print("\n" + "=" * 80)
    print("COMPUTING GLOBAL PERCENTILE RANKINGS")
    print("=" * 80)
    
    # Compute global percentiles
    scored_items = [(cid, sc) for cid, sc in all_company_sector_scores.items() if sc is not None]
    
    if not scored_items:
        print("❌ No scores computed. Check that company_metrics data exists.")
        return
    
    scores_list = [sc for cid, sc in scored_items]
    sorted_scores = sorted(scores_list)
    
    def percentile(score):
        """Calculate what percentile this score is (0-100)"""
        count_less_or_equal = sum(1 for s in sorted_scores if s <= score)
        return (count_less_or_equal / len(sorted_scores)) * 100.0
    
    print(f"\nScore distribution:")
    print(f"   Min:    {min(scores_list):.2f}")
    print(f"   25th:   {sorted_scores[len(scores_list)//4]:.2f}")
    print(f"   Median: {sorted_scores[len(scores_list)//2]:.2f}")
    print(f"   75th:   {sorted_scores[3*len(scores_list)//4]:.2f}")
    print(f"   Max:    {max(scores_list):.2f}")
    
    # Delete old scores and insert new ones
    print("\n" + "=" * 80)
    print("SAVING SCORES TO DATABASE")
    print("=" * 80)
    
    Score.query.delete()  # Clear old scores
    
    scores_saved = 0
    for cid, sec_score in all_company_sector_scores.items():
        if sec_score is not None:
            global_pct = percentile(sec_score)
        else:
            global_pct = None
        
        new_score = Score(
            company_id=cid,
            sector_score=sec_score,
            global_score=global_pct,
            last_calculated=datetime.utcnow()
        )
        db.session.add(new_score)
        scores_saved += 1
    
    db.session.commit()
    
    print(f"\n✅ Computed and saved scores for {scores_saved} companies")
    print("=" * 80)
    
    # Show top 10
    print("\n🏆 TOP 10 COMPANIES (by sector score):")
    print("-" * 80)
    
    top_scores = Score.query.order_by(Score.sector_score.desc()).limit(10).all()
    for i, score in enumerate(top_scores, 1):
        comp = Company.query.get(score.company_id)
        print(f"{i:2d}. {comp.name[:40]:40s} Score: {float(score.sector_score):6.2f} (Percentile: {float(score.global_score):5.1f})")
    
    print("=" * 80)

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        compute_all_scores()
