-- 001_init.sql
-- Initial schema for the AI Rolodex Agent.
-- Run against a PostgreSQL 15+ database with the pgvector extension available
-- (Supabase Postgres ships with pgvector pre-installed; for self-hosted
-- Postgres use the `pgvector/pgvector` Docker image or `CREATE EXTENSION`
-- after installing the extension package).

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pgcrypto; -- for gen_random_uuid()

CREATE TABLE IF NOT EXISTS contacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    full_name           VARCHAR(255) NOT NULL,
    headline            VARCHAR(500),
    linkedin_url        VARCHAR(500),
    photo_url           VARCHAR(1000),
    current_company     VARCHAR(255),
    current_title       VARCHAR(255),
    location            VARCHAR(255),
    industry            VARCHAR(255),
    summary             TEXT,

    experience          JSONB DEFAULT '[]'::jsonb,
    education           JSONB DEFAULT '[]'::jsonb,

    skills              JSONB DEFAULT '[]'::jsonb,
    technologies        JSONB DEFAULT '[]'::jsonb,
    domains             JSONB DEFAULT '[]'::jsonb,
    capabilities        JSONB DEFAULT '[]'::jsonb,
    interests           JSONB DEFAULT '[]'::jsonb,

    relevance_summary   TEXT,
    relevance_tags      JSONB DEFAULT '[]'::jsonb,

    connection_notes    JSONB DEFAULT '[]'::jsonb,

    raw_source_text     TEXT,
    source_type         VARCHAR(50),

    -- text-embedding-3-small has 1536 dimensions; keep in sync with
    -- OPENAI_EMBEDDING_DIMENSIONS in app/core/config.py.
    embedding           vector(1536),

    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_contacts_full_name ON contacts (full_name);
CREATE INDEX IF NOT EXISTS idx_contacts_current_company ON contacts (current_company);
CREATE INDEX IF NOT EXISTS idx_contacts_current_title ON contacts (current_title);
CREATE INDEX IF NOT EXISTS idx_contacts_industry ON contacts (industry);
CREATE INDEX IF NOT EXISTS idx_contacts_linkedin_url ON contacts (linkedin_url);

-- GIN indexes for JSONB containment queries (skills @> '["Kubernetes"]', etc).
CREATE INDEX IF NOT EXISTS idx_contacts_skills_gin ON contacts USING GIN (skills);
CREATE INDEX IF NOT EXISTS idx_contacts_technologies_gin ON contacts USING GIN (technologies);
CREATE INDEX IF NOT EXISTS idx_contacts_domains_gin ON contacts USING GIN (domains);
CREATE INDEX IF NOT EXISTS idx_contacts_tags_gin ON contacts USING GIN (relevance_tags);

-- Approximate nearest-neighbour index for semantic search.
-- IVFFlat requires an ANALYZE after data is loaded, and `lists` should be
-- tuned to roughly sqrt(row_count) for larger datasets; 100 is a sane
-- default for a rolodex of up to a few thousand contacts.
CREATE INDEX IF NOT EXISTS idx_contacts_embedding_ivfflat
    ON contacts USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

CREATE TABLE IF NOT EXISTS search_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query VARCHAR(500) NOT NULL,
    result_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_search_logs_created_at ON search_logs (created_at DESC);

-- Keep updated_at current on every row update.
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_contacts_updated_at ON contacts;
CREATE TRIGGER trg_contacts_updated_at
    BEFORE UPDATE ON contacts
    FOR EACH ROW
    EXECUTE FUNCTION set_updated_at();
