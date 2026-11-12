-- =========================================================================
-- AMK TECHNOLOGIES - AI-FIRST COLLEGE TRANSFORMATION PLATFORM
-- IDENTITY SERVICE SCHEMA FOR SUPABASE POSTGRESQL
-- Target Schema: identity_service
-- Database: postgres (db.enkssiilvwiemxvsqaoy.supabase.co)
-- =========================================================================

-- 1. Create Schema
CREATE SCHEMA IF NOT EXISTS identity_service;

-- Set search path to identity_service schema
SET search_path TO identity_service, public;

-- 2. Create Tenants Table (Zero random UUIDs: custom college code e.g. 'SRIT-ATP')
CREATE TABLE IF NOT EXISTS identity_service.tenants (
    tenant_id VARCHAR(50) PRIMARY KEY,                    -- Custom ID: e.g. 'SRIT-ATP', 'JNTUA-CEA'
    name VARCHAR(255) NOT NULL,                           -- Full college name
    university_affiliation VARCHAR(100) DEFAULT 'JNTUA',
    tier VARCHAR(50) NOT NULL DEFAULT 'STARTER',          -- 'STARTER', 'PROFESSIONAL', 'ENTERPRISE'
    max_students INT NOT NULL DEFAULT 60,
    max_faculty INT NOT NULL DEFAULT 5,
    current_students INT NOT NULL DEFAULT 0,
    current_faculty INT NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Create Dynamic Roles Table (Zero random UUIDs: meaningful string IDs)
CREATE TABLE IF NOT EXISTS identity_service.roles (
    role_id VARCHAR(50) PRIMARY KEY,                      -- e.g. 'ROLE_STUDENT', 'ROLE_FACULTY', 'ROLE_HOD'
    name VARCHAR(100) NOT NULL,                           -- Human readable role name
    description TEXT,
    hierarchy_level INT NOT NULL DEFAULT 10,              -- Higher number = higher authority (10 to 100)
    is_self_registerable BOOLEAN NOT NULL DEFAULT FALSE, -- Only TRUE for ROLE_STUDENT
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    permissions JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Create Users Table (Zero random UUIDs: Student Roll No or Staff ID)
CREATE TABLE IF NOT EXISTS identity_service.users (
    user_id VARCHAR(100) PRIMARY KEY,                     -- Student Roll No ('22731A0501') or Staff ID ('FAC-SRIT-001')
    tenant_id VARCHAR(50) NOT NULL REFERENCES identity_service.tenants(tenant_id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(150) NOT NULL,
    department VARCHAR(50) NOT NULL DEFAULT 'GENERAL',     -- 'CSE', 'ECE', 'EEE', 'AIDS', etc.
    batch_year VARCHAR(20),                               -- e.g. '2022-2026'
    role_id VARCHAR(50) NOT NULL REFERENCES identity_service.roles(role_id) ON UPDATE CASCADE,
    created_by_user_id VARCHAR(100) REFERENCES identity_service.users(user_id), -- Admin's user_id who provisioned
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_identity_tenant_email UNIQUE (tenant_id, email)
);

-- Indexes for lightning fast lookups
CREATE INDEX IF NOT EXISTS idx_users_tenant_role ON identity_service.users(tenant_id, role_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON identity_service.users(email);
CREATE INDEX IF NOT EXISTS idx_users_created_by ON identity_service.users(created_by_user_id);

-- 5. Seed Core System Roles
INSERT INTO identity_service.roles (role_id, name, description, hierarchy_level, is_self_registerable) VALUES
('ROLE_SUPER_ADMIN', 'Super Administrator', 'AMK Platform Administrator with global access', 100, false),
('ROLE_ADMIN', 'College Administrator', 'College Principal / Management Authority', 90, false),
('ROLE_TECHNICAL_MANAGER', 'Technical Manager', 'Technical project and operations manager', 80, false),
('ROLE_MANAGER', 'Innovation Manager', 'Manager coordinating academic and project tracks', 75, false),
('ROLE_HOD', 'Head of Department', 'Department Head (CSE, ECE, EEE, MECH, etc.)', 70, false),
('ROLE_SR_LEAD', 'Senior Technical Lead', 'Technical Lead, Architect and Project Reviewer', 65, false),
('ROLE_TRAINER', 'Technical Trainer', 'Hands-on Technical Trainer & Lab Instructor', 60, false),
('ROLE_FACULTY', 'College Faculty', 'Teaching faculty, guides, and evaluators', 50, false),
('ROLE_TPO', 'Training & Placement Officer', 'Placement & Career Development Cell Head', 50, false),
('ROLE_STUDENT', 'Enrolled Student', 'College student (Roll Number is User ID)', 10, true)
ON CONFLICT (role_id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    hierarchy_level = EXCLUDED.hierarchy_level,
    is_self_registerable = EXCLUDED.is_self_registerable,
    updated_at = CURRENT_TIMESTAMP;

-- 6. Seed Pilot Demo College (SRIT - Anantapur)
INSERT INTO identity_service.tenants (tenant_id, name, university_affiliation, tier, max_students, max_faculty, current_students, current_faculty)
VALUES (
    'SRIT-ATP',
    'Srinivasa Ramanujan Institute of Technology',
    'JNTUA',
    'PROFESSIONAL',
    250,
    20,
    1,
    2
) ON CONFLICT (tenant_id) DO UPDATE SET
    name = EXCLUDED.name,
    university_affiliation = EXCLUDED.university_affiliation,
    updated_at = CURRENT_TIMESTAMP;

-- 7. Seed Initial Test Accounts (Default Password for test users: "Password123!")
-- BCrypt Hash: $2a$10$7EqJtq98hPqEX7fNZaFWoO.S4a9sD2Bph9pU5vHqH0f5VzPzYp6vS
INSERT INTO identity_service.users (user_id, tenant_id, email, password_hash, full_name, department, batch_year, role_id, created_by_user_id) VALUES
-- 1. College Administrator (Principal)
(
    'ADM-SRIT-001',
    'SRIT-ATP',
    'admin@srit.ac.in',
    '$2a$10$7EqJtq98hPqEX7fNZaFWoO.S4a9sD2Bph9pU5vHqH0f5VzPzYp6vS',
    'Dr. M. S. Kumar (Principal)',
    'ADMINISTRATION',
    NULL,
    'ROLE_ADMIN',
    NULL
),
-- 2. College Faculty (Provisioned by Admin)
(
    'FAC-SRIT-001',
    'SRIT-ATP',
    'faculty@srit.ac.in',
    '$2a$10$7EqJtq98hPqEX7fNZaFWoO.S4a9sD2Bph9pU5vHqH0f5VzPzYp6vS',
    'Dr. K. Sreenivasulu',
    'CSE',
    NULL,
    'ROLE_FACULTY',
    'ADM-SRIT-001'
),
-- 3. Student (Roll Number = User ID: "22731A0501", Self-Registered)
(
    '22731A0501',
    'SRIT-ATP',
    'student@srit.ac.in',
    '$2a$10$7EqJtq98hPqEX7fNZaFWoO.S4a9sD2Bph9pU5vHqH0f5VzPzYp6vS',
    'Rahul Sharma',
    'CSE',
    '2022-2026',
    'ROLE_STUDENT',
    NULL
)
ON CONFLICT (user_id) DO UPDATE SET
    email = EXCLUDED.email,
    full_name = EXCLUDED.full_name,
    department = EXCLUDED.department,
    updated_at = CURRENT_TIMESTAMP;

