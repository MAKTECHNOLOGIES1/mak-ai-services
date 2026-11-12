-- =========================================================================
-- AMK TECHNOLOGIES - SEED DATA FOR LOCAL DEVELOPMENT & PILOT TESTING
-- =========================================================================

-- 1. Insert Sample College (Srinivasa Ramanujan Institute of Technology)
INSERT INTO tenants (id, code, name, university_affiliation, tier, max_students, max_faculty, current_students, current_faculty)
VALUES (
    'c1f7a40b-7871-46c6-9964-16ce34927b23',
    'SRIT-ATP',
    'Srinivasa Ramanujan Institute of Technology',
    'JNTUA',
    'PROFESSIONAL',
    250,
    20,
    2,
    1
) ON CONFLICT (code) DO NOTHING;

-- 2. Enable Modules for the College
INSERT INTO tenant_modules (tenant_id, module_key, is_enabled) VALUES
('c1f7a40b-7871-46c6-9964-16ce34927b23', 'COLLEGE_AI', true),
('c1f7a40b-7871-46c6-9964-16ce34927b23', 'FACULTY_AI', true),
('c1f7a40b-7871-46c6-9964-16ce34927b23', 'PROJECT_STUDIO', true),
('c1f7a40b-7871-46c6-9964-16ce34927b23', 'LEARNING_HUB', true)
ON CONFLICT DO NOTHING;

-- 3. Insert Users (Password is: "Password123!" hashed with BCrypt)
-- Hash: $2a$10$7EqJtq98hPqEX7fNZaFWoO.S4a9sD2Bph9pU5vHqH0f5VzPzYp6vS
INSERT INTO users (id, tenant_id, email, password_hash, full_name, roll_number, department, batch_year, role) VALUES
-- Student 1
(
    'a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d',
    'c1f7a40b-7871-46c6-9964-16ce34927b23',
    'student@srit.ac.in',
    '$2a$10$7EqJtq98hPqEX7fNZaFWoO.S4a9sD2Bph9pU5vHqH0f5VzPzYp6vS',
    'Rahul Sharma',
    '22731A0501',
    'CSE',
    '2022-2026',
    'STUDENT'
),
-- Faculty 1
(
    'b2c3d4e5-f6a7-8b9c-0d1e-2f3a4b5c6d7e',
    'c1f7a40b-7871-46c6-9964-16ce34927b23',
    'faculty@srit.ac.in',
    '$2a$10$7EqJtq98hPqEX7fNZaFWoO.S4a9sD2Bph9pU5vHqH0f5VzPzYp6vS',
    'Dr. K. Sreenivasulu',
    NULL,
    'CSE',
    NULL,
    'FACULTY'
),
-- College Admin / HOD
(
    'c3d4e5f6-a7b8-9c0d-1e2f-3a4b5c6d7e8f',
    'c1f7a40b-7871-46c6-9964-16ce34927b23',
    'hod.cse@srit.ac.in',
    '$2a$10$7EqJtq98hPqEX7fNZaFWoO.S4a9sD2Bph9pU5vHqH0f5VzPzYp6vS',
    'Prof. M. Ramesh Kumar',
    NULL,
    'CSE',
    NULL,
    'HOD'
) ON CONFLICT DO NOTHING;

-- 4. Seed User Quotas
INSERT INTO user_ai_quotas (user_id, tenant_id, daily_query_limit, queries_used_today) VALUES
('a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d', 'c1f7a40b-7871-46c6-9964-16ce34927b23', 25, 3),
('b2c3d4e5-f6a7-8b9c-0d1e-2f3a4b5c6d7e', 'c1f7a40b-7871-46c6-9964-16ce34927b23', 100, 12)
ON CONFLICT DO NOTHING;

-- 5. Seed 1 Sample Course
INSERT INTO courses (id, tenant_id, title, description, level) VALUES (
    'd4e5f6a7-b8c9-0d1e-2f3a-4b5c6d7e8f9a',
    'c1f7a40b-7871-46c6-9964-16ce34927b23',
    'Generative AI & Prompt Engineering for Engineers',
    'Master prompt engineering techniques, code generation, and responsible AI usage for JNTUA students.',
    'BEGINNER'
) ON CONFLICT DO NOTHING;

INSERT INTO lessons (id, course_id, title, content_markdown, lesson_order) VALUES (
    'e5f6a7b8-c9d0-1e2f-3a4b-5c6d7e8f9a0b',
    'd4e5f6a7-b8c9-0d1e-2f3a-4b5c6d7e8f9a',
    'Lesson 1: Introduction to LLMs & Prompt Anatomy',
    '# Introduction to Large Language Models\n\nLLMs predict the next most likely token. A prompt consists of:\n1. Role / Persona\n2. Context / Background\n3. Instruction / Task\n4. Output format constraints',
    1
) ON CONFLICT DO NOTHING;

