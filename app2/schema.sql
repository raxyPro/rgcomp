-- schema.sql
-- This file defines the database schema for the chat, task, and user authentication applications.

-- Drop existing tables if they exist to allow for clean re-initialization
DROP TABLE IF EXISTS chat_messages;
DROP TABLE IF EXISTS tasks;
DROP TABLE IF EXISTS users;

-- Create the users table for authentication
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL, -- Username must be unique
    password TEXT NOT NULL         -- Password stored in plaintext (for demonstration)
);

-- Create the chat_messages table
-- Stores individual chat messages with sender, message content, and a timestamp.
CREATE TABLE chat_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT, -- Unique identifier for each message
    sender TEXT NOT NULL,                -- The name of the sender
    message TEXT NOT NULL,               -- The content of the message
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- The time the message was sent (defaults to current time)
);

-- Create the tasks table
-- Stores tasks with their text description, completion status, and associated user.
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT, -- Unique identifier for each task
    user_id INTEGER NOT NULL,             -- The ID of the user who owns this task
    text TEXT NOT NULL,                   -- The description of the task
    completed BOOLEAN NOT NULL DEFAULT 0,  -- 0 for incomplete, 1 for complete (defaults to incomplete)
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE -- Ensures tasks are deleted if user is deleted
);
