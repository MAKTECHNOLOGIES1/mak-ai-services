-- =========================================================================
-- AMK TECHNOLOGIES - SEED DATA FOR LOCAL DEVELOPMENT & PILOT TESTING
-- Target Schema: identity_service
-- =========================================================================

-- 1. Insert Sample College (tenant_id is customized: "SRIT-ATP")
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
) ON CONFLICT (tenant_id) DO NOTHING;

-- 2. Seed Default Roles (Dynamic Role System with meaningful role_id)
INSERT INTO identity_service.roles (role_id, name, description, hierarchy_level, is_self_registerable) VALUES
('ROLE_SUPER_ADMIN', 'Super Administrator', 'AMK Platform Administrator', 100, false),
('ROLE_ADMIN', 'College Administrator', 'College Principal / Management', 90, false),
('ROLE_TECHNICAL_MANAGER', 'Technical Manager', 'Technical project manager', 80, false),
('ROLE_MANAGER', 'Innovation Manager', 'Manager coordinating academic tracks', 75, false),
('ROLE_HOD', 'Head of Department', 'Department Head (CSE, ECE, etc.)', 70, false),
('ROLE_SR_LEAD', 'Senior Technical Lead', 'Technical Lead & Architect', 65, false),
('ROLE_TRAINER', 'Technical Trainer', 'Instructor delivering workshops', 60, false),
('ROLE_FACULTY', 'College Faculty', 'Teaching faculty', 50, false),
('ROLE_TPO', 'Training & Placement Officer', 'Placement & Career Head', 50, false),
('ROLE_STUDENT', 'Enrolled Student', 'College student (Roll Number is user_id)', 10, true)
ON CONFLICT (role_id) DO NOTHING;

-- 3. Insert Users (Password is: "Password123!" hashed with BCrypt)
-- Hash: $2a$10$7EqJtq98hPqEX7fNZaFWoO.S4a9sD2Bph9pU5vHqH0f5VzPzYp6vS
INSERT INTO identity_service.users (user_id, tenant_id, email, password_hash, full_name, department, batch_year, role_id, created_by_user_id) VALUES
-- Admin (Principal)
(
    'ADM-SRIT-001',
    'SRIT-ATP',
    'admin@srit.ac.in',
    '$2a$10$7EqJtq98hPqEX7fNZaFWoO.S4a9sD2Bph9pU5vHqH0f5VzPzYp6vS',
    'Dr. M. S Kumar (Principal)',
    'ADMINISTRATION',
    NULL,
    'ROLE_ADMIN',
    NULL
),
-- Faculty (Provisioned by Admin ADM-SRIT-001)
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
-- Student (Roll Number = User ID: "22731A0501", Self-Registered)
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
) ON CONFLICT (user_id) DO NOTHING;
