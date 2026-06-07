-- Create Database
CREATE DATABASE IF NOT EXISTS employee_system;
USE employee_system;

-- =====================================
-- Employee Table
-- =====================================
CREATE TABLE employee (
    emp_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    age INT NOT NULL,
    department INT NOT NULL,
    education INT NOT NULL,
    jobrole INT NOT NULL,
    experience INT NOT NULL,
    income INT NOT NULL,
    trainings INT NOT NULL,
    worklife INT NOT NULL,
    satisfaction INT NOT NULL,
    overtime INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================
-- Evaluations Table
-- =====================================
CREATE TABLE evaluations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    emp_id INT NOT NULL,
    work_quality INT NOT NULL,
    productivity INT NOT NULL,
    attendance FLOAT NOT NULL,
    teamwork INT NOT NULL,
    communication INT NOT NULL,
    task_completion INT NOT NULL,
    problem_solving INT NOT NULL,
    initiative INT NOT NULL,
    adaptability INT NOT NULL,
    deadline INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (emp_id)
        REFERENCES employee(emp_id)
        ON DELETE CASCADE
);

-- =====================================
-- HR Analysis Table
-- =====================================
CREATE TABLE hr_analysis (
    hr_id INT AUTO_INCREMENT PRIMARY KEY,
    emp_id INT NOT NULL,
    performance_score FLOAT NOT NULL,
    performance_level VARCHAR(20) NOT NULL,
    ml_prediction INT,
    email_sent BOOLEAN DEFAULT FALSE,
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (emp_id)
        REFERENCES employee(emp_id)
        ON DELETE CASCADE
);

-- =====================================
-- Email Log Table
-- =====================================
CREATE TABLE email_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    emp_id INT NOT NULL,
    email VARCHAR(100) NOT NULL,
    subject VARCHAR(200) NOT NULL,
    status TEXT NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (emp_id)
        REFERENCES employee(emp_id)
        ON DELETE CASCADE
);

-- =====================================
-- Users Table
-- =====================================
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================
-- Default Admin User
-- =====================================
INSERT INTO users (username, password_hash)
VALUES (
    'admin',
    'scrypt:32768:8:1$examplehashedpassword'
);

-- generate_password_hash('admin123')