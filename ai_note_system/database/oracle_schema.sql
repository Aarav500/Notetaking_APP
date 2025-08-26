/*
Oracle Database Schema for AI Note System
This schema is designed for Oracle ATP or Oracle MySQL HeatWave.
It includes tables for users, notes, flashcards, and files.
*/

-- Users table for authentication and user management
CREATE TABLE users (
  id VARCHAR2(36) PRIMARY KEY,
  email VARCHAR2(255) UNIQUE NOT NULL,
  password_hash VARCHAR2(255) NOT NULL,
  name VARCHAR2(100),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_login TIMESTAMP
);

-- Notes table for storing user notes
CREATE TABLE user_notes (
  id VARCHAR2(36) PRIMARY KEY,
  user_id VARCHAR2(36) NOT NULL,
  title VARCHAR2(255),
  content CLOB,
  summary CLOB,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Flashcards table for storing flashcards related to notes
CREATE TABLE flashcards (
  id VARCHAR2(36) PRIMARY KEY,
  note_id VARCHAR2(36),
  question CLOB,
  answer CLOB,
  type VARCHAR2(50),
  created_at TIMESTAMP,
  FOREIGN KEY (note_id) REFERENCES user_notes(id)
);

-- AI Outputs table for storing AI-generated content
CREATE TABLE ai_outputs (
  id VARCHAR2(36) PRIMARY KEY,
  user_id VARCHAR2(36),
  input_reference VARCHAR2(255),
  output_type VARCHAR2(50), -- summary, flashcard, quiz
  output_data CLOB,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Files table for storing user files
CREATE TABLE user_files (
  id VARCHAR2(36) PRIMARY KEY,
  user_id VARCHAR2(36),
  filename VARCHAR2(255),
  file_url VARCHAR2(255), -- OCI Object Storage pre-signed URL
  type VARCHAR2(50),
  created_at TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Study Planner table for storing study plans
CREATE TABLE study_plans (
  id VARCHAR2(36) PRIMARY KEY,
  user_id VARCHAR2(36),
  topic VARCHAR2(255),
  deadline TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Study Plan Time Blocks table for storing time blocks within study plans
CREATE TABLE study_plan_blocks (
  id VARCHAR2(36) PRIMARY KEY,
  plan_id VARCHAR2(36),
  start_time TIMESTAMP,
  end_time TIMESTAMP,
  title VARCHAR2(255),
  description CLOB,
  weight NUMBER(3,2) DEFAULT 1.0,
  completed NUMBER(1) DEFAULT 0,
  FOREIGN KEY (plan_id) REFERENCES study_plans(id)
);

-- Study Plan Goals table for storing goals within study plans
CREATE TABLE study_plan_goals (
  id VARCHAR2(36) PRIMARY KEY,
  plan_id VARCHAR2(36),
  title VARCHAR2(255),
  description CLOB,
  deadline TIMESTAMP,
  priority NUMBER(1) DEFAULT 1,
  completed NUMBER(1) DEFAULT 0,
  FOREIGN KEY (plan_id) REFERENCES study_plans(id)
);

-- User Activity table for tracking user activity
CREATE TABLE user_activity (
  id VARCHAR2(36) PRIMARY KEY,
  user_id VARCHAR2(36),
  type VARCHAR2(50),
  value VARCHAR2(255),
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Additional tables can be added later:
-- - flowcharts
-- - projects
-- - ai_insights
-- - quiz_results