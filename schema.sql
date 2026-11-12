-- =========================================================================
-- AMK TECHNOLOGIES - AI-FIRST COLLEGE TRANSFORMATION PLATFORM
-- Unified Multi-Tenant Database Schema with pgvector
-- Database: PostgreSQL 16
-- =========================================================================

-- 1. Enable Vector Extension for RAG
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- 2. Core Tenant & College Management
CREATE TABLE IF NOT EXISTS tenants (
    tenant_id VARCHAR(50) PRIMARY KEY,            -- Custom College ID: e.g. "SRIT-ATP", "JNTUA-CEA"
    name VARCHAR(255) NOT NULL,
    university_affiliation VARCHAR(100) DEFAULT 'JNTUA',
    tier VARCHAR(50) NOT NULL DEFAULT 'STARTER',  -- STARTER, PROFESSIONAL, ENTERPRISE
    max_students INT NOT NULL DEFAULT 60,
    max_faculty INT NOT NULL DEFAULT 5,
    current_students INT NOT NULL DEFAULT 0,
    current_faculty INT NOT NULL DEFAULT 0,
    monthly_ai_token_quota BIGINT NOT NULL DEFAULT 5000000,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tenant_modules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(50) NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    module_key VARCHAR(50) NOT NULL,
    is_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE(tenant_id, module_key)
);

-- 3. Dynamic Roles & Identity
CREATE TABLE IF NOT EXISTS roles (
    role_id VARCHAR(50) PRIMARY KEY,              -- e.g. "ROLE_STUDENT", "ROLE_FACULTY", "ROLE_ADMIN"
    name VARCHAR(100) NOT NULL,                   -- e.g. "Enrolled Student", "College Faculty"
    description TEXT,
    hierarchy_level INT NOT NULL DEFAULT 10,      -- Higher number = higher authority
    is_self_registerable BOOLEAN NOT NULL DEFAULT FALSE, -- Only TRUE for ROLE_STUDENT
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    permissions JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS users (
    user_id VARCHAR(100) PRIMARY KEY,             -- Custom User ID: Student Roll Number or Staff ID
    tenant_id VARCHAR(50) NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(150) NOT NULL,
    department VARCHAR(50) NOT NULL DEFAULT 'GENERAL', -- CSE, ECE, EEE, AIDS
    batch_year VARCHAR(20),                       -- 2022-2026
    role_id VARCHAR(50) NOT NULL REFERENCES roles(role_id) ON UPDATE CASCADE, -- e.g. "ROLE_STUDENT"
    created_by_user_id VARCHAR(100) REFERENCES users(user_id), -- Admin's user_id
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_tenant_email UNIQUE (tenant_id, email)
);

-- 4. AI Gateway Quotas & Metering
CREATE TABLE IF NOT EXISTS user_ai_quotas (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    daily_query_limit INT NOT NULL DEFAULT 25,
    queries_used_today INT NOT NULL DEFAULT 0,
    last_reset_date DATE NOT NULL DEFAULT CURRENT_DATE
);

CREATE TABLE IF NOT EXISTS ai_usage_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    feature_module VARCHAR(50) NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    prompt_tokens INT NOT NULL DEFAULT 0,
    completion_tokens INT NOT NULL DEFAULT 0,
    total_tokens INT NOT NULL DEFAULT 0,
    estimated_cost_inr NUMERIC(8, 4) NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. Syllabus & Academic Regulations Knowledge Base (RAG)
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    document_type VARCHAR(50) NOT NULL, -- "SYLLABUS", "REGULATION", "LAB_MANUAL"
    file_path VARCHAR(500) NOT NULL,
    total_pages INT NOT NULL DEFAULT 0,
    is_processed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    chunk_index INT NOT NULL,
    page_number INT NOT NULL,
    chunk_content TEXT NOT NULL,
    embedding vector(1536) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS document_chunks_embedding_idx ON document_chunks 
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- 6. Faculty AI Content & Bloom's Taxonomy
DO $$ BEGIN
    CREATE TYPE content_status AS ENUM ('DRAFT', 'APPROVED', 'REJECTED');
    CREATE TYPE content_type AS ENUM ('QUESTION_BANK', 'LESSON_PLAN', 'ASSIGNMENT');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

CREATE TABLE IF NOT EXISTS faculty_generated_content (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    faculty_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subject_name VARCHAR(150) NOT NULL,
    subject_code VARCHAR(50),
    unit_number VARCHAR(50) NOT NULL,
    content_type content_type NOT NULL,
    status content_status NOT NULL DEFAULT 'DRAFT',
    title VARCHAR(255) NOT NULL,
    generated_payload JSONB NOT NULL,
    faculty_feedback TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    approved_at TIMESTAMP WITH TIME ZONE
);

-- 7. AI Learning Hub & Courses
CREATE TABLE IF NOT EXISTS courses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    thumbnail_url VARCHAR(500),
    level VARCHAR(50) DEFAULT 'BEGINNER',
    is_published BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS lessons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    content_markdown TEXT NOT NULL,
    video_url VARCHAR(500),
    lesson_order INT NOT NULL
);

CREATE TABLE IF NOT EXISTS student_enrollments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    progress_percentage NUMERIC(5, 2) DEFAULT 0.00,
    is_completed BOOLEAN DEFAULT FALSE,
    enrolled_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(user_id, course_id)
);

-- 8. Project Studio & Milestone Logs
DO $$ BEGIN
    CREATE TYPE project_status AS ENUM ('PROPOSED', 'IN_PROGRESS', 'UNDER_REVIEW', 'COMPLETED');
    CREATE TYPE milestone_status AS ENUM ('PENDING', 'SUBMITTED', 'VERIFIED_BY_FACULTY', 'REJECTED');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    domain VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    tech_stack TEXT[] NOT NULL,
    leader_student_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    guide_faculty_id UUID REFERENCES users(id) ON DELETE SET NULL,
    github_repo_url VARCHAR(500),
    live_demo_url VARCHAR(500),
    status project_status NOT NULL DEFAULT 'IN_PROGRESS',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS project_milestones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    milestone_number INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    expected_deliverable TEXT NOT NULL,
    proof_url VARCHAR(500),
    status milestone_status NOT NULL DEFAULT 'PENDING',
    faculty_feedback TEXT,
    submitted_at TIMESTAMP WITH TIME ZONE,
    verified_at TIMESTAMP WITH TIME ZONE
);

-- 9. Audit Logs & NAAC Compliance Tracking
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    actor_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    actor_role VARCHAR(50) NOT NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id UUID,
    details JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_audit_tenant_action ON audit_logs(tenant_id, action, created_at);

