-- seed.sql
-- Wipes all tables and reinserts clean sample data.

CREATE DATABASE IF NOT EXISTS job_tracker
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;

USE job_tracker;

SET FOREIGN_KEY_CHECKS = 0;

TRUNCATE TABLE application_status;
TRUNCATE TABLE application;
TRUNCATE TABLE job_posting;
TRUNCATE TABLE contact;
TRUNCATE TABLE company;

ALTER TABLE company            AUTO_INCREMENT = 1;
ALTER TABLE contact            AUTO_INCREMENT = 1;
ALTER TABLE job_posting        AUTO_INCREMENT = 1;
ALTER TABLE application        AUTO_INCREMENT = 1;
ALTER TABLE application_status AUTO_INCREMENT = 1;

SET FOREIGN_KEY_CHECKS = 1;

-- ── Companies ─────────────────────────────────────────────────────────
INSERT INTO company (name, website, company_location) VALUES
  ('Acme Corp', 'https://acme.example', 'Austin, TX');
SET @company1_id = LAST_INSERT_ID();

INSERT INTO company (name, website, company_location) VALUES
  ('Beta Systems', 'https://beta.example', 'Remote');
SET @company2_id = LAST_INSERT_ID();

-- ── Contacts ──────────────────────────────────────────────────────────
INSERT INTO contact (company_id, full_name, title, email, phone, linkedin) VALUES
  (@company1_id, 'Jane Doe', 'Hiring Manager', 'jane.doe@acme.example', '555-0101', 'https://linkedin.example/jane-doe');
SET @contact1_id = LAST_INSERT_ID();

INSERT INTO contact (company_id, full_name, title, email, phone, linkedin) VALUES
  (@company2_id, 'John Smith', 'Recruiter', 'john.smith@beta.example', '555-0202', 'https://linkedin.example/john-smith');
SET @contact2_id = LAST_INSERT_ID();

-- ── Job Postings ──────────────────────────────────────────────────────
INSERT INTO job_posting (company_id, job_title, job_location, employment_type, job_url, salary, posted_date) VALUES
  (@company1_id, 'Software Engineer I', 'Austin, TX', 'Full-time', 'https://jobs.acme/example1', 85000, '2026-02-01');
SET @job1_id = LAST_INSERT_ID();

INSERT INTO job_posting (company_id, job_title, job_location, employment_type, job_url, salary, posted_date) VALUES
  (@company2_id, 'Data Engineer', 'Remote', 'Contract', 'https://jobs.beta/example2', NULL, '2026-01-15');
SET @job2_id = LAST_INSERT_ID();

-- ── Applications ──────────────────────────────────────────────────────
INSERT INTO application (job_id, applied_date, source, priority, resume) VALUES
  (@job1_id, '2026-02-10', 'Referral', 1, '/resumes/resume.pdf');
SET @app1_id = LAST_INSERT_ID();

INSERT INTO application (job_id, applied_date, source, priority, resume) VALUES
  (@job2_id, NULL, 'LinkedIn', 3, NULL);
SET @app2_id = LAST_INSERT_ID();

-- ── Application Statuses ──────────────────────────────────────────────
INSERT INTO application_status (application_id, contact_id, status) VALUES
  (@app1_id, @contact1_id, 'APPLIED'),
  (@app1_id, NULL,         'INTERVIEW'),
  (@app1_id, @contact1_id, 'OFFER'),
  (@app2_id, NULL,         'SAVED'),
  (@app2_id, @contact2_id, 'SCREEN');
