-- schema.sql
-- MySQL 8.0+ recommended

CREATE DATABASE IF NOT EXISTS job_tracker
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;

USE job_tracker;

-- --------------------------------------------------
-- 1) company
-- --------------------------------------------------
CREATE TABLE IF NOT EXISTS company (
  company_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(150) NOT NULL,
  website VARCHAR(255) DEFAULT NULL,
  company_location VARCHAR(150) DEFAULT 'Remote',
  CONSTRAINT uq_company_name UNIQUE (name)
) ENGINE=InnoDB;

-- --------------------------------------------------
-- 2) contact
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

-- --------------------------------------------------
-- 3) job_posting
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

-- --------------------------------------------------
-- 4) application
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

-- --------------------------------------------------
-- 5) application_status
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
