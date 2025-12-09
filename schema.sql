CREATE DATABASE IF NOT EXISTS init_db;
USE init_db;

CREATE TABLE IF NOT EXISTS departments (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL UNIQUE,
  description VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(80) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL, -- store hashed password
  role VARCHAR(20) DEFAULT 'user'
);

CREATE TABLE IF NOT EXISTS employees (
  id INT AUTO_INCREMENT PRIMARY KEY,
  first_name VARCHAR(45) NOT NULL,
  middle_name VARCHAR(45),
  last_name VARCHAR(45) NOT NULL,
  name_extension VARCHAR(5),
  birthdate DATE,
  birth_city VARCHAR(45),
  birth_province VARCHAR(45),
  birth_country VARCHAR(45),
  sex VARCHAR(7),
  civil_status VARCHAR(10),
  department_id INT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL
);