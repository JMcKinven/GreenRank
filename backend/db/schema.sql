-- backend/db/schema.sql
-- Schema matching the actual CSV structure (CSVs are source of truth)

-- Drop tables in correct order (respecting foreign keys)
DROP TABLE IF EXISTS scores CASCADE;
DROP TABLE IF EXISTS company_metrics CASCADE;
DROP TABLE IF EXISTS sector_metrics CASCADE;
DROP TABLE IF EXISTS companies CASCADE;
DROP TABLE IF EXISTS metrics CASCADE;
DROP TABLE IF EXISTS sectors CASCADE;

-- SECTORS table (CSV: id,sector_name,description)
CREATE TABLE sectors (
  id SERIAL PRIMARY KEY,
  sector_name TEXT NOT NULL UNIQUE,
  description TEXT
);

-- METRICS table (CSV: metric_id,metric_name,unit,invert_score,description,source)
-- Note: 'invert_score' FALSE means higher is better (renewable %), TRUE means lower is better (emissions)
CREATE TABLE metrics (
  metric_id SERIAL PRIMARY KEY,
  metric_name TEXT NOT NULL UNIQUE,
  unit TEXT,
  invert_score BOOLEAN DEFAULT FALSE,
  description TEXT,
  source TEXT
);

-- SECTOR_METRICS table (CSV: sector_metric_id,sector_id,metric_id,weight)
CREATE TABLE sector_metrics (
  sector_metric_id SERIAL PRIMARY KEY,
  sector_id INT NOT NULL REFERENCES sectors(id) ON DELETE CASCADE,
  metric_id INT NOT NULL REFERENCES metrics(metric_id) ON DELETE CASCADE,
  weight NUMERIC DEFAULT 0.0,
  UNIQUE (sector_id, metric_id)
);

-- COMPANIES table (CSV: company_id,name,sector_id,turnover,country,description,website)
CREATE TABLE companies (
  company_id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  sector_id INT REFERENCES sectors(id),
  turnover NUMERIC,
  country TEXT,
  description TEXT,
  website TEXT
);

-- COMPANY_METRICS table (CSV from populated: id,company_id,metric_id,value,year)
CREATE TABLE company_metrics (
  id SERIAL PRIMARY KEY,
  company_id INT NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE,
  metric_id INT NOT NULL REFERENCES metrics(metric_id) ON DELETE CASCADE,
  value NUMERIC,
  year INT,
  UNIQUE (company_id, metric_id, year)
);

-- SCORES table (computed, not from CSV)
CREATE TABLE scores (
  score_id SERIAL PRIMARY KEY,
  company_id INT NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE,
  sector_score NUMERIC,
  global_score NUMERIC,
  last_calculated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (company_id)  -- One current score per company
);

-- Create indexes for performance
CREATE INDEX idx_company_metrics_company ON company_metrics(company_id);
CREATE INDEX idx_company_metrics_metric ON company_metrics(metric_id);
CREATE INDEX idx_companies_sector ON companies(sector_id);
CREATE INDEX idx_sector_metrics_sector ON sector_metrics(sector_id);
CREATE INDEX idx_scores_company ON scores(company_id);

-- Grant permissions to greenrank_user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO greenrank_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO greenrank_user;
