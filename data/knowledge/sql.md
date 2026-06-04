---
title: [[sql]] Query — ภาษา查询จัดการฐานข้อมูลเชิงสัมพันธ์
tags: [knowledge, vault]
aliases: [sql]
---
# [[sql]] Query — ภาษา查询จัดการฐานข้อมูลเชิงสัมพันธ์

## ประเภทของคำสั่ง [[sql]]
- **DDL** (Data Definition): CREATE, ALTER, DROP — จัดโครงสร้าง
- **DML** (Data Manipulation): SELECT, INSERT, UPDATE, DELETE — จัดการข้อมูล
- **DCL** (Data Control): GRANT, REVOKE — สิทธิ์การเข้าถึง
- **TCL** (Transaction Control): BEGIN, COMMIT, ROLLBACK

## CREATE TABLE
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    age INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    body TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

## INSERT
```sql
INSERT INTO users (email, name, age)
VALUES ('jinx@example.com', 'Jinx', 3);

-- insert หลายแถว
INSERT INTO users (email, name, age) VALUES
    ('a@a.com', 'Alice', 25),
    ('b@b.com', 'Bob', 30);
```

## SELECT — การ查询
```sql
-- พื้นฐาน
SELECT * FROM users;
SELECT name, age FROM users;

-- WHERE — กรองข้อมูล
SELECT * FROM users WHERE age >= 18;
SELECT * FROM users WHERE name LIKE 'J%';
SELECT * FROM users WHERE email IN ('a@a.com', 'b@b.com');
SELECT * FROM users WHERE age BETWEEN 20 AND 40;

-- ORDER BY — เรียงลำดับ
SELECT * FROM users ORDER BY age DESC;

-- LIMIT + OFFSET — แบ่งหน้า
SELECT * FROM users LIMIT 10 OFFSET 20;

-- DISTINCT — ไม่ซ้ำ
SELECT DISTINCT age FROM users;

-- COUNT, AVG, SUM, MAX, MIN — ฟังก์ชันรวม
SELECT COUNT(*) FROM users;
SELECT AVG(age) FROM users;
SELECT MAX(age), MIN(age) FROM users;

-- GROUP BY + HAVING
SELECT age, COUNT(*) FROM users
GROUP BY age
HAVING COUNT(*) > 1;
```

## JOIN — เชื่อมตาราง
```sql
-- INNER JOIN — เฉพาะที่มีข้อมูลทั้งสองตาราง
SELECT users.name, posts.title
FROM users
INNER JOIN posts ON users.id = posts.user_id;

-- LEFT JOIN — เอาทุกแถวจากตารางซ้าย
SELECT users.name, posts.title
FROM users
LEFT JOIN posts ON users.id = posts.user_id;

-- Multiple JOINs
SELECT u.name, p.title, c.body
FROM users u
JOIN posts p ON u.id = p.user_id
JOIN comments c ON p.id = c.post_id;
```

## UPDATE + DELETE
```sql
UPDATE users SET age = 4 WHERE name = 'Jinx';

DELETE FROM users WHERE age < 18;

-- DELETE ทั้งหมด (เร็ว แต่ไม่สามารถ ROLLBACK ในบาง DB)
TRUNCATE TABLE users;
```

## INDEX — ทำให้查询เร็ว
```sql
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_posts_user_id ON posts(user_id);

-- Composite index — หลายคอลัมน์
CREATE INDEX idx_users_name_age ON users(name, age);
```

## Transactions
```sql
BEGIN TRANSACTION;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;
-- หรือ ROLLBACK ถ้ามี error
```

## Subqueries
```sql
SELECT * FROM users WHERE id IN (
    SELECT user_id FROM posts GROUP BY user_id HAVING COUNT(*) > 5
);

-- correlated subquery
SELECT name, (
    SELECT COUNT(*) FROM posts WHERE posts.user_id = users.id
) AS post_count FROM users;
```

## [[common]] [[sql]] Functions
```sql
-- String
UPPER(name), LOWER(name), LENGTH(name), TRIM(name)
SUBSTR(name, 1, 3)               -- ตัด string
REPLACE(name, 'J', 'K')          -- แทนที่
CONCAT(first, ' ', last)          -- ต่อ string (|| ใน SQLite)

-- Date/Time
DATE('now'), TIME('now'), DATETIME('now')
STRFTIME('%Y-%m-%d', 'now')      -- รูปแบบตามต้องการ
JULIANDAY('2024-01-01') - JULIANDAY('2023-01-01')  -- ต่างกันกี่วัน

-- Numeric
ROUND(3.14159, 2)                -- 3.14
ABS(-5), RANDOM()
```

## 3 รูปแบบ Normalization (NF)
1. **1NF**: ทุกคอลัมน์มีค่าเดียว atomic
2. **2NF**: 1NF + ทุก non-key column ขึ้นกับ primary key ทั้งหมด
3. **3NF**: 2NF + ไม่มี transitive dependency (column ที่ขึ้นกับ column อื่นที่ไม่ใช่ key)
