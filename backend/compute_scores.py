import math
import statistics
from datetime import datetime
from sqlalchemy import and_
from models import db, Sector, Metric, SectorMetric, Company, CompanyMetric, Score
from app import create_app


def normal_cdf(z):
    """Standard normal cumulative distribution function"""
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


# Define which metrics should be normalized by turnover (absolute values)
# Percentages and ratios should NOT be normalized
ABSOLUTE_METRICS = {
    1,  # Operational_energy (MWh/Year)
    3,  # C02_emissions_yearly (tCO2e)
    6,  # Shipping_emmisions (tCO2e/km) - already normalized, keep as is
    9,  # food_waste (Tonne/year)
    10,  # Water_use (cubic m/year)
    13,  # shipping_distance (km)
    14,  # Energy_intensity (MWh/tonne) - already intensity, keep as is
    15,  # waste_landfill (tonne.year)
    17,  # Air_pollutant_emmisions (kg/year)
    18,  # Embedded_carbon_per_project (tCO2e/proj) - already normalized
}


def normalize_value(metric_id, value, company_turnover):
    """
    Normalize metric value by log(turnover) for absolute metrics.
    """
    if metric_id in ABSOLUTE_METRICS and company_turnover and company_turnover > 0:
        # Convert billions to millions for more reasonable log values
        turnover_millions = company_turnover * 1000
        # Use log base 10 + 1 to avoid log(0)
        log_scale = math.log10(turnover_millions + 1)
        # Return value normalized by log of turnover
        return value / log_scale
    else:
        # Return raw value for percentages
        return value


def compute_metric_score(company_value, comparison_values, invert_score=False):
    """
    Compute 0-100 score for a metric value relative to comparison set.

    Args:
        company_value: The company's (normalized) value for this metric
        comparison_values: List of all (normalized) values to compare against
        invert_score: If FALSE, higher is better. If TRUE, lower is better.

    Returns:
        Score from 0-100, where 50 is average
    """
    # Handle empty comparison data
    if not comparison_values or all(v is None for v in comparison_values):
        return 50.0

    # Convert to float and filter None
    vals = [float(v) for v in comparison_values if v is not None]

    if len(vals) == 0:
        return 50.0

    mean = statistics.mean(vals)

    # Use standard deviation
    if len(vals) > 1:
        std = statistics.stdev(vals)
    else:
        std = 0.0

    # If all values are identical, return 50
    if std == 0.0:
        return 50.0

    # Calculate z-score
    z = (company_value - mean) / std

    # Apply inversion
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
    print("COMPUTING SUSTAINABILITY SCORES (TURNOVER-ADJUSTED)")
    print("=" * 80)

    all_company_sector_scores = {}
    companies_processed = set()

    # Build turnover lookup
    company_turnover = {}
    for comp in Company.query.all():
        company_turnover[comp.company_id] = float(comp.turnover) if comp.turnover else None

    # Process each sector
    sectors = Sector.query.all()

    for sector in sectors:
        print(f"\nProcessing Sector {sector.id}: {sector.sector_name}")
        print("-" * 80)

        sec_metrics = SectorMetric.query.filter_by(sector_id=sector.id).all()

        if not sec_metrics:
            print(f"No metrics defined for this sector")
            continue

        metric_ids = [sm.metric_id for sm in sec_metrics]
        weights_map = {sm.metric_id: float(sm.weight) for sm in sec_metrics}

        total_weight = sum(weights_map.values())
        print(f"   Total weight: {total_weight:.4f}")

        # Gather sector-wide NORMALIZED values for each metric
        sector_values = {}

        for m_id in metric_ids:
            rows = db.session.query(CompanyMetric).join(Company).filter(
                and_(
                    Company.sector_id == sector.id,
                    CompanyMetric.metric_id == m_id,
                    CompanyMetric.value.isnot(None)
                )
            ).all()

            # Normalize values by company turnover
            normalized_vals = []
            for r in rows:
                turnover = company_turnover.get(r.company_id)
                if turnover:
                    normalized_val = normalize_value(m_id, float(r.value), turnover)
                    normalized_vals.append(normalized_val)

            sector_values[m_id] = normalized_vals

            metric = Metric.query.get(m_id)
            normalization = " (intensity)" if m_id in ABSOLUTE_METRICS else " (raw)"
            print(f"   Metric {m_id:2d} ({metric.metric_name:30s}): {len(normalized_vals):3d} values{normalization}")

        # Score each company in the sector
        companies_in_sector = Company.query.filter_by(sector_id=sector.id).all()
        print(f"\n   Scoring {len(companies_in_sector)} companies...")

        for comp in companies_in_sector:
            weighted_sum = 0.0
            weight_sum_present = 0.0

            for m_id in metric_ids:
                cm = CompanyMetric.query.filter_by(
                    company_id=comp.company_id,
                    metric_id=m_id
                ).first()

                if cm and cm.value is not None:
                    turnover = company_turnover.get(comp.company_id)
                    if not turnover:
                        continue

                    metric = Metric.query.get(m_id)
                    normalized_val = normalize_value(m_id, float(cm.value), turnover)

                    # Compute score for this normalized metric
                    m_score = compute_metric_score(
                        normalized_val,
                        sector_values[m_id],
                        invert_score=bool(metric.invert_score)
                    )

                    w = weights_map.get(m_id, 0.0)
                    weighted_sum += m_score * w
                    weight_sum_present += w

            if weight_sum_present > 0:
                sector_score = weighted_sum / weight_sum_present
            else:
                sector_score = None

            all_company_sector_scores[comp.company_id] = sector_score
            companies_processed.add(comp.company_id)

    print("\n" + "=" * 80)
    print("COMPUTING GLOBAL SCORES (TURNOVER-ADJUSTED, CROSS-SECTOR)")
    print("=" * 80)

    # Get all unique metrics
    all_metrics_used = set()
    for sm in SectorMetric.query.all():
        all_metrics_used.add(sm.metric_id)

    print(f"\nComparing companies globally across {len(all_metrics_used)} metrics...")

    # Gather GLOBAL normalized values
    global_metric_values = {}

    for m_id in all_metrics_used:
        rows = db.session.query(CompanyMetric).filter(
            CompanyMetric.metric_id == m_id,
            CompanyMetric.value.isnot(None)
        ).all()

        normalized_vals = []
        for r in rows:
            turnover = company_turnover.get(r.company_id)
            if turnover:
                normalized_val = normalize_value(m_id, float(r.value), turnover)
                normalized_vals.append(normalized_val)

        if normalized_vals:
            global_metric_values[m_id] = normalized_vals
            metric = Metric.query.get(m_id)
            normalization = " (intensity)" if m_id in ABSOLUTE_METRICS else " (raw)"
            print(f"   Metric {m_id:2d} ({metric.metric_name:30s}): {len(normalized_vals):3d} values{normalization}")

    # Compute global scores
    all_company_global_scores = {}

    print(f"\nScoring {len(companies_processed)} companies globally...")

    for comp in Company.query.all():
        company_metrics = CompanyMetric.query.filter_by(company_id=comp.company_id).all()

        if not company_metrics:
            all_company_global_scores[comp.company_id] = None
            continue

        turnover = company_turnover.get(comp.company_id)
        if not turnover:
            all_company_global_scores[comp.company_id] = None
            continue

        metric_scores = []

        for cm in company_metrics:
            if cm.value is None or cm.metric_id not in global_metric_values:
                continue

            metric = Metric.query.get(cm.metric_id)
            normalized_val = normalize_value(cm.metric_id, float(cm.value), turnover)

            # Score this metric GLOBALLY
            m_score = compute_metric_score(
                normalized_val,
                global_metric_values[cm.metric_id],
                invert_score=bool(metric.invert_score)
            )

            metric_scores.append(m_score)

        if metric_scores:
            all_company_global_scores[comp.company_id] = sum(metric_scores) / len(metric_scores)
        else:
            all_company_global_scores[comp.company_id] = None

    # Display score distributions
    print("\n" + "-" * 80)
    print("SCORE DISTRIBUTIONS")
    print("-" * 80)

    sector_scores = [s for s in all_company_sector_scores.values() if s is not None]
    if sector_scores:
        sorted_sector = sorted(sector_scores)
        print(f"\nSector Scores:")
        print(f"   Min:    {min(sector_scores):.2f}")
        print(f"   25th:   {sorted_sector[len(sector_scores) // 4]:.2f}")
        print(f"   Median: {sorted_sector[len(sector_scores) // 2]:.2f}")
        print(f"   75th:   {sorted_sector[3 * len(sector_scores) // 4]:.2f}")
        print(f"   Max:    {max(sector_scores):.2f}")

    global_scores = [s for s in all_company_global_scores.values() if s is not None]
    if global_scores:
        sorted_global = sorted(global_scores)
        print(f"\nGlobal Scores:")
        print(f"   Min:    {min(global_scores):.2f}")
        print(f"   25th:   {sorted_global[len(global_scores) // 4]:.2f}")
        print(f"   Median: {sorted_global[len(global_scores) // 2]:.2f}")
        print(f"   75th:   {sorted_global[3 * len(global_scores) // 4]:.2f}")
        print(f"   Max:    {max(global_scores):.2f}")

    # Save to database
    print("\n" + "=" * 80)
    print("SAVING SCORES TO DATABASE")
    print("=" * 80)

    Score.query.delete()

    scores_saved = 0
    for cid in companies_processed:
        new_score = Score(
            company_id=cid,
            sector_score=all_company_sector_scores.get(cid),
            global_score=all_company_global_scores.get(cid),
            last_calculated=datetime.utcnow()
        )
        db.session.add(new_score)
        scores_saved += 1

    db.session.commit()

    print(f"\nComputed and saved scores for {scores_saved} companies")
    print("=" * 80)

    # Show top 20 by GLOBAL score
    print("\n TOP 20 COMPANIES (by GLOBAL score - turnover-adjusted cross-sector):")
    print("-" * 80)

    top_scores = Score.query.order_by(Score.global_score.desc()).limit(20).all()
    for i, score in enumerate(top_scores, 1):
        comp = Company.query.get(score.company_id)
        sector = Sector.query.get(comp.sector_id)
        global_val = float(score.global_score) if score.global_score else 0
        sector_val = float(score.sector_score) if score.sector_score else 0
        turnover_val = float(comp.turnover) if comp.turnover else 0
        print(
            f"{i:2d}. {comp.name[:30]:30s} | {sector.sector_name:15s} | Turnover: £{turnover_val:6.2f}B | Global: {global_val:5.2f}")

    print("\n TOP 20 COMPANIES (by SECTOR score):")
    print("-" * 80)

    top_sector_scores = Score.query.order_by(Score.sector_score.desc()).limit(20).all()
    for i, score in enumerate(top_sector_scores, 1):
        comp = Company.query.get(score.company_id)
        sector = Sector.query.get(comp.sector_id)
        sector_val = float(score.sector_score) if score.sector_score else 0
        global_val = float(score.global_score) if score.global_score else 0
        turnover_val = float(comp.turnover) if comp.turnover else 0
        print(
            f"{i:2d}. {comp.name[:30]:30s} | {sector.sector_name:15s} | Turnover: £{turnover_val:6.2f}B | Sector: {sector_val:5.2f}")

    print("=" * 80)


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        compute_all_scores()