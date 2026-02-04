-- seed.sql
USE job_tracker;

-- Clean reset (safe order because of FKs)
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE application_status;
TRUNCATE TABLE application;
TRUNCATE TABLE job_posting;
TRUNCATE TABLE contact;
TRUNCATE TABLE company;
SET FOREIGN_KEY_CHECKS = 1;

-- Base date for deterministic seeding (adjust if you want)
SET @base_date = '2026-02-04';

-- 50 companies
INSERT INTO company (name, website, company_location)
WITH RECURSIVE seq(n) AS (
  SELECT 1
  UNION ALL
  SELECT n + 1 FROM seq WHERE n < 50
)
SELECT
  CONCAT('Company ', LPAD(n, 2, '0')) AS name,
  CONCAT('https://company', n, '.example.com') AS website,
  ELT((n % 10) + 1,
      'New York, NY', 'Austin, TX', 'Seattle, WA', 'San Francisco, CA', 'Boston, MA',
      'Chicago, IL', 'Atlanta, GA', 'Denver, CO', 'Remote', 'Raleigh, NC') AS company_location
FROM seq;

-- 50 contacts (one per company)
INSERT INTO contact (company_id, full_name, title, email, phone, linkedin)
WITH RECURSIVE seq(n) AS (
  SELECT 1
  UNION ALL
  SELECT n + 1 FROM seq WHERE n < 50
)
SELECT
  n AS company_id,
  CONCAT(
    ELT((n % 10)+1,'Alex','Jordan','Taylor','Morgan','Casey','Riley','Avery','Quinn','Jamie','Parker'),
    ' ',
    ELT((n % 10)+1,'Smith','Johnson','Brown','Davis','Miller','Wilson','Moore','Anderson','Thomas','Jackson')
  ) AS full_name,
  ELT((n % 5)+1, 'Recruiter', 'Hiring Manager', 'Talent Partner', 'Engineering Manager', 'HR Generalist') AS title,
  CONCAT('contact', n, '@company', n, '.example.com') AS email,
  CONCAT('555-01', LPAD(n, 2, '0')) AS phone,
  CONCAT('https://www.linkedin.com/in/contact', n) AS linkedin
FROM seq;

-- 50 job postings (one per company)
INSERT INTO job_posting (company_id, job_title, job_location, employment_type, job_url, salary, posted_date)
WITH RECURSIVE seq(n) AS (
  SELECT 1
  UNION ALL
  SELECT n + 1 FROM seq WHERE n < 50
)
SELECT
  n AS company_id,
  ELT((n % 10)+1,
      'Software Engineer', 'Data Analyst', 'Backend Engineer', 'Frontend Engineer', 'DevOps Engineer',
      'Data Scientist', 'QA Engineer', 'Product Manager', 'Mobile Developer', 'Security Engineer') AS job_title,
  ELT((n % 8)+1,
      'Remote', 'New York, NY', 'Austin, TX', 'Seattle, WA', 'San Francisco, CA', 'Boston, MA', 'Chicago, IL', 'Denver, CO') AS job_location,
  ELT((n % 3)+1, 'Full-time', 'Internship', 'Contract') AS employment_type,
  CONCAT('https://company', n, '.example.com/careers/jobs/', n) AS job_url,
  ROUND(60000 + (n * 1500), 2) AS salary,
  DATE_SUB(@base_date, INTERVAL (n * 2) DAY) AS posted_date
FROM seq;

-- 50 applications (one per job posting)
INSERT INTO application (job_id, applied_date, source, priority, resume)
WITH RECURSIVE seq(n) AS (
  SELECT 1
  UNION ALL
  SELECT n + 1 FROM seq WHERE n < 50
)
SELECT
  n AS job_id,
  DATE_SUB(@base_date, INTERVAL n DAY) AS applied_date,
  ELT((n % 5)+1, 'LinkedIn', 'Company Site', 'Referral', 'Indeed', 'Handshake') AS source,
  ((n - 1) % 5) + 1 AS priority,
  CONCAT('resume_', ELT((n % 4)+1,'v1','v2','v3','v4'), '.pdf') AS resume
FROM seq;

-- 150 application statuses (3 per application) for timeline-like data
INSERT INTO application_status (application_id, contact_id, status)
WITH RECURSIVE seq(n) AS (
  SELECT 1
  UNION ALL
  SELECT n + 1 FROM seq WHERE n < 150
)
SELECT
  FLOOR((n - 1) / 3) + 1 AS application_id,
  FLOOR((n - 1) / 3) + 1 AS contact_id,
  CASE ((n - 1) % 3) + 1
    WHEN 1 THEN 'SAVED'
    WHEN 2 THEN 'APPLIED'
    ELSE
      CASE ((FLOOR((n - 1) / 3) + 1) % 8)
        WHEN 0 THEN 'SCREEN'
        WHEN 1 THEN 'INTERVIEW'
        WHEN 2 THEN 'ASSESSMENT'
        WHEN 3 THEN 'OFFER'
        WHEN 4 THEN 'REJECTED'
        WHEN 5 THEN 'GHOSTED'
        WHEN 6 THEN 'WITHDRAWN'
        ELSE 'ACCEPTED'
      END
  END AS status
FROM seq;
