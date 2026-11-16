-- =========================================================================
-- MAK AI PLATFORM - IDENTITY SERVICE DATABASE SETUP FOR SUPABASE
-- Schema: identity_service
-- Bulletproof format for Supabase SQL Editor
-- =========================================================================

-- STEP 1: Schema creation
CREATE SCHEMA IF NOT EXISTS identity_service;

-- STEP 2: Create Tenants Table
CREATE TABLE IF NOT EXISTS identity_service.tenants (
    tenant_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    university_affiliation VARCHAR(100) DEFAULT 'JNTUA',
    tier VARCHAR(50) NOT NULL DEFAULT 'STARTER',
    max_students INT NOT NULL DEFAULT 60,
    max_faculty INT NOT NULL DEFAULT 5,
    current_students INT NOT NULL DEFAULT 0,
    current_faculty INT NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- STEP 3: Create Dynamic Roles Table
CREATE TABLE IF NOT EXISTS identity_service.roles (
    role_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    hierarchy_level INT NOT NULL DEFAULT 10,
    is_self_registerable BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    permissions JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- STEP 4: Create Users Table (tenant_id is NULLABLE for independent students)
CREATE TABLE IF NOT EXISTS identity_service.users (
    user_id VARCHAR(100) PRIMARY KEY,
    tenant_id VARCHAR(50) REFERENCES identity_service.tenants(tenant_id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(150) NOT NULL,
    department VARCHAR(50) NOT NULL DEFAULT 'GENERAL',
    batch_year VARCHAR(20),
    role_id VARCHAR(50) NOT NULL REFERENCES identity_service.roles(role_id) ON UPDATE CASCADE,
    created_by_user_id VARCHAR(100) REFERENCES identity_service.users(user_id),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Ensure tenant_id allows NULL
ALTER TABLE identity_service.users ALTER COLUMN tenant_id DROP NOT NULL;

-- STEP 5: Row Level Security (RLS) Configuration
-- Supabase requires policies if RLS is enabled; these ensure the service role can read/write
ALTER TABLE identity_service.tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE identity_service.roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE identity_service.users ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Service role access tenants" ON identity_service.tenants;
CREATE POLICY "Service role access tenants" ON identity_service.tenants FOR ALL USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "Service role access roles" ON identity_service.roles;
CREATE POLICY "Service role access roles" ON identity_service.roles FOR ALL USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "Service role access users" ON identity_service.users;
CREATE POLICY "Service role access users" ON identity_service.users FOR ALL USING (true) WITH CHECK (true);

-- STEP 6: Indexes & Unique Constraints
CREATE INDEX IF NOT EXISTS idx_users_tenant_role ON identity_service.users(tenant_id, role_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON identity_service.users(email);
CREATE INDEX IF NOT EXISTS idx_users_created_by ON identity_service.users(created_by_user_id);

CREATE UNIQUE INDEX IF NOT EXISTS uq_users_independent_email ON identity_service.users(email) WHERE tenant_id IS NULL;
CREATE UNIQUE INDEX IF NOT EXISTS uq_users_tenant_email ON identity_service.users(tenant_id, email) WHERE tenant_id IS NOT NULL;

-- STEP 7: Seed Core System Roles (Clean, Single-line inserts)
INSERT INTO identity_service.roles (role_id, name, description, hierarchy_level, is_self_registerable)
VALUES
('ROLE_SUPER_ADMIN', 'Super Administrator', 'Platform Super Admin', 100, false),
('ROLE_ADMIN', 'College Administrator', 'College Principal or Management', 90, false),
('ROLE_TECHNICAL_MANAGER', 'Technical Manager', 'Technical Project Manager', 80, false),
('ROLE_MANAGER', 'Innovation Manager', 'Academic and Project Manager', 75, false),
('ROLE_HOD', 'Head of Department', 'Department Head', 70, false),
('ROLE_SR_LEAD', 'Senior Technical Lead', 'Technical Lead and Reviewer', 65, false),
('ROLE_TRAINER', 'Technical Trainer', 'Lab Trainer and Instructor', 60, false),
('ROLE_FACULTY', 'College Faculty', 'Teaching Faculty and Evaluators', 50, false),
('ROLE_TPO', 'Training & Placement Officer', 'Placement Cell Head', 50, false),
('ROLE_STUDENT', 'Enrolled Student', 'Independent or College Student', 10, true)
ON CONFLICT (role_id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    hierarchy_level = EXCLUDED.hierarchy_level,
    is_self_registerable = EXCLUDED.is_self_registerable,
    updated_at = NOW();

-- STEP 8: Seed Pilot Demo College Tenant
INSERT INTO identity_service.tenants (tenant_id, name, university_affiliation, tier, max_students, max_faculty, current_students, current_faculty)
VALUES ('SRIT-ATP', 'Srinivasa Ramanujan Institute of Technology', 'JNTUA', 'PROFESSIONAL', 250, 20, 0, 1)
ON CONFLICT (tenant_id) DO UPDATE SET
    name = EXCLUDED.name,
    updated_at = NOW();
