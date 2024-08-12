CREATE DATABASE IF NOT EXISTS cs353hw4db;
USE cs353hw4db;

-- Create User table
CREATE TABLE IF NOT EXISTS User (
  id INT AUTO_INCREMENT PRIMARY KEY,
  password VARCHAR(255) NOT NULL,
  username VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL
);

-- Create TaskType table
CREATE TABLE IF NOT EXISTS TaskType (
  type VARCHAR(255) PRIMARY KEY
);

-- Create Task table
CREATE TABLE IF NOT EXISTS Task (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  description TEXT NOT NULL,
  status VARCHAR(255) NOT NULL,
  deadline DATETIME NOT NULL,
  creation_time DATETIME NOT NULL,
  done_time DATETIME,
  user_id INT NOT NULL,
  task_type VARCHAR(255) NOT NULL,
  FOREIGN KEY (user_id) REFERENCES User(id),
  FOREIGN KEY (task_type) REFERENCES TaskType(type)
);


INSERT INTO User (id, password, username, email)
VALUES
  (1, 'pass123', 'user1', 'user1@example.com'),
  (2, 'password', 'user2', 'user2@example.com');

INSERT INTO TaskType (type)
VALUES
  ('Health'),
  ('Job'),
  ('Lifestyle'),
  ('Family'),
  ('Hobbies');

INSERT INTO Task (id, title, description, status, deadline, creation_time, done_time, user_id, task_type)
VALUES
  (1, 'Go for a walk', 'Walk for at least 30 mins', 'Done', '2023-03-20 17:00:00', '2023-03-15 10:00:00', '2023-03-20 10:00:00', 1, 'Health'),
  (2, 'Clean the house', 'Clean the whole house', 'Done', '2023-03-18 12:00:00', '2023-03-14 09:00:00', '2023-03-18 17:00:00', 1, 'Lifestyle'),
  (3, 'Submit report', 'Submit quarterly report', 'Todo', '2023-04-12 17:00:00', '2023-03-21 13:00:00', null, 1, 'Job'),
  (4, 'Call Mom', 'Call Mom and wish her', 'Todo', '2023-04-06 11:00:00', '2023-03-23 12:00:00', null, 1, 'Family'),
  (5, 'Gym workout', 'Do weight training for an hour', 'Done', '2023-03-19 14:00:00', '2023-03-12 10:00:00', '2023-03-19 11:00:00', 1, 'Health'),
  (6, 'Play guitar', 'Learn new song for an hour', 'Todo', '2023-04-05 20:00:00', '2023-03-20 14:00:00', null, 2, 'Hobbies'),
  (7, 'Book flights', 'Book flights for summer vacation', 'Done', '2023-03-16 09:00:00', '2023-03-13 13:00:00', '2023-03-16 11:00:00', 2, 'Lifestyle'),
  (8, 'Write a blog post', 'Write about recent project', 'Todo', '2023-04-11 17:00:00', '2023-03-22 09:00:00', null, 2, 'Job'),
  (9, 'Grocery shopping', 'Buy groceries for the week', 'Todo', '2023-04-05 18:00:00', '2023-03-31 10:00:00', null, 2, 'Family'),
  (10, 'Painting', 'Paint a landscape for 2 hours', 'Done', '2023-03-23 15:00:00', '2023-03-18 14:00:00', '2023-03-23 16:00:00', 2, 'Hobbies');
