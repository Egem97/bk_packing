CREATE SCHEMA IF NOT EXISTS pipeline;

CREATE TABLE IF NOT EXISTS pipeline.pipeline_data (
  id VARCHAR(255) PRIMARY KEY,
  source_file VARCHAR(500),
  data_type VARCHAR(100),
  raw_data JSONB,
  processed_data JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Optional helper tables referenced by API demo endpoints
CREATE TABLE IF NOT EXISTS pipeline.employee_data (
  id VARCHAR(255) PRIMARY KEY,
  source_file VARCHAR(255),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  raw_data JSONB,
  processed_data JSONB
);

CREATE TABLE IF NOT EXISTS pipeline.sales_data (
  id VARCHAR(255) PRIMARY KEY,
  source_file VARCHAR(255),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  raw_data JSONB,
  processed_data JSONB
);

CREATE TABLE IF NOT EXISTS pipeline.production_data (
  id VARCHAR(255) PRIMARY KEY,
  source_file VARCHAR(255),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  raw_data JSONB,
  processed_data JSONB
);

CREATE TABLE IF NOT EXISTS pipeline.data_statistics (
  id VARCHAR(255) PRIMARY KEY,
  data_type VARCHAR(100),
  record_count INT,
  file_count INT,
  earliest_record TIMESTAMPTZ,
  latest_record TIMESTAMPTZ,
  calculated_at TIMESTAMPTZ DEFAULT NOW()
);


