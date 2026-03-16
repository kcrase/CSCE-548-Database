-- schema_with_defaults.sql
-- MySQL 8.0+ recommended

CREATE DATABASE IF NOT EXISTS job_tracker
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;

USE job_tracker;

-- --------------------------------------------------
-- 1) company
-- Columns: company_id, name, website, company_location
-- Only added DEFAULT for company_location (no new columns).
-- --------------------------------------------------
CREATE TABLE IF NOT EXISTS company (
  company_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(150) NOT NULL,
  website VARCHAR(255) DEFAULT NULL,
  company_location VARCHAR(150) DEFAULT 'Remote',
  CONSTRAINT uq_company_name UNIQUE (name)
) ENGINE=InnoDB;

-- Examples: company inserts that rely on defaults
INSERT INTO company (name) VALUES ('Acme Corp');
INSERT INTO company (name, website) VALUES ('Beta LLC', 'https://beta.example');
-- explicit override of default
INSERT INTO company (name, company_location) VALUES ('Onsite Inc', 'On-site HQ');

-- --------------------------------------------------
-- 2) contact
-- Columns: contact_id, company_id, full_name, title, email, phone, linkedin
-- Added DEFAULTs: title -> 'Unknown', email/phone/linkedin -> NULL (explicitly)
-- --------------------------------------------------
CREATE TABLE IF NOT EXISTS contact (
  contact_id INT AUTO_INCREMENT PRIMARY KEY,
  company_id INT NOT NULL,
  full_name VARCHAR(150) NOT NULL,
  title VARCHAR(100) DEFAULT 'Unknown',
  email VARCHAR(255) DEFAULT NULL,
  phone VARCHAR(50) DEFAULT NULL,
  linkedin VARCHAR(255) DEFAULT NULL,
  KEY idx_contact_company_id (company_id),
  CONSTRAINT fk_contact_company FOREIGN KEY (company_id)
    REFERENCES company(company_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Examples: contact inserts
-- minimal: will set title to 'Unknown' and optional fields to NULL
INSERT INTO contact (company_id, full_name) VALUES (1, 'Jane Doe');
-- provide some fields, leave others defaulted
INSERT INTO contact (company_id, full_name, email) VALUES (1, 'John Smith', 'jsmith@example.com');
-- override title explicitly
INSERT INTO contact (company_id, full_name, title, phone) VALUES (2, 'Sara Li', 'Engineer', '555-0101');

-- --------------------------------------------------
-- 3) job_posting
-- Columns: job_id, company_id, job_title, job_location, employment_type, job_url, salary, posted_date
-- Added DEFAULTs: job_location -> 'Remote', employment_type -> 'Full-time', job_url/salary/posted_date -> NULL
-- --------------------------------------------------
CREATE TABLE IF NOT EXISTS job_posting (
  job_id INT AUTO_INCREMENT PRIMARY KEY,
  company_id INT NOT NULL,
  job_title VARCHAR(200) NOT NULL,
  job_location VARCHAR(150) DEFAULT 'Remote',
  employment_type VARCHAR(50) DEFAULT 'Full-time',
  job_url VARCHAR(255) DEFAULT NULL,
  salary DECIMAL(12,2) DEFAULT NULL,
  posted_date DATE DEFAULT NULL,
  KEY idx_job_company_id (company_id),
  CONSTRAINT fk_job_company FOREIGN KEY (company_id)
    REFERENCES company(company_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Examples: job_posting inserts
-- minimal: job_location -> 'Remote', employment_type -> 'Full-time'
INSERT INTO job_posting (company_id, job_title) VALUES (1, 'Software Engineer');
-- provide URL and salary
INSERT INTO job_posting (company_id, job_title, job_url, salary) VALUES (1, 'Data Analyst', 'https://jobs.example/123', 90000.00);
-- override location to onsite
INSERT INTO job_posting (company_id, job_title, job_location, employment_type) VALUES (2, 'QA Tester', 'On-site', 'Contract');

-- --------------------------------------------------
-- 4) application
-- Columns: application_id, job_id, applied_date, source, priority, resume
-- Added DEFAULTs: source -> 'Unknown', priority -> 0, other nullable fields -> NULL
-- --------------------------------------------------
CREATE TABLE IF NOT EXISTS application (
  application_id INT AUTO_INCREMENT PRIMARY KEY,
  job_id INT NOT NULL,
  applied_date DATE DEFAULT NULL,
  source VARCHAR(100) DEFAULT 'Unknown',
  priority INT DEFAULT 0,
  resume VARCHAR(255) DEFAULT NULL,
  KEY idx_app_job_id (job_id),
  CONSTRAINT fk_application_job FOREIGN KEY (job_id)
    REFERENCES job_posting(job_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Examples: application inserts
-- omit source -> becomes 'Unknown', priority -> 0
INSERT INTO application (job_id) VALUES (1);
-- provide source, leave priority default
INSERT INTO application (job_id, source) VALUES (2, 'LinkedIn');
-- explicit applied_date and resume path
INSERT INTO application (job_id, applied_date, resume, priority) VALUES (1, '2025-02-01', '/resumes/alice.pdf', 2);

-- --------------------------------------------------
-- 5) application_status
-- Columns: status_id, application_id, contact_id, status
-- Added DEFAULT: status -> 'SAVED' (string), contact_id -> NULL allowed
-- --------------------------------------------------
CREATE TABLE IF NOT EXISTS application_status (
  status_id INT AUTO_INCREMENT PRIMARY KEY,
  application_id INT NOT NULL,
  contact_id INT DEFAULT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'SAVED',
  KEY idx_status_application_id (application_id),
  KEY idx_status_contact_id (contact_id),
  CONSTRAINT fk_status_application
    FOREIGN KEY (application_id)
    REFERENCES application(application_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT fk_status_contact
    FOREIGN KEY (contact_id)
    REFERENCES contact(contact_id)
    ON DELETE SET NULL
    ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Examples: application_status inserts
-- minimal: contact_id omitted -> NULL, status defaults to 'SAVED'
INSERT INTO application_status (application_id) VALUES (1);
-- provide contact_id and explicit status
INSERT INTO application_status (application_id, contact_id, status) VALUES (2, 1, 'APPLIED');
-- create a screening status (explicit)
INSERT INTO application_status (application_id, status) VALUES (1, 'SCREEN');