CREATE DATABASE lazy_db;
\connect lazy_db;

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  username TEXT UNIQUE NOT NULL,
  email TEXT UNIQUE NOT NULL,
  hashed_password TEXT NOT NULL,
  full_name TEXT,
  disabled BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT now()
);