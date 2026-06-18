CREATE DATABASE student_db;
USE student_db;
CREATE TABLE students (
    roll_no INT PRIMARY KEY,
    name VARCHAR(30) NOT NULL,
    age INT CHECK (age > 0),
    marks FLOAT CHECK (marks >= 0 AND marks <= 100),
    class_section VARCHAR(10)
);
SHOW TABLES;
DESC students;
SELECT * FROM student_db.students;