# การเขียนโปรแกรม — ฐานข้อมูล (Database Basics)

## ฐานข้อมูลเชิงสัมพันธ์ (Relational Database)

### แนวคิดพื้นฐาน
- **ตาราง (Table)**: เก็บข้อมูลในรูปแบบแถวและคอลัมน์
- **แถว (Row / Record)**: ข้อมูล 1 ชุด
- **คอลัมน์ (Column / Field)**: ชนิดข้อมูล 1 ประเภท
- **คีย์หลัก (Primary Key)**: ระบุแต่ละแถวได้ไม่ซ้ำกัน
- **คีย์นอก (Foreign Key)**: อ้างอิงถึงคีย์หลักของอีกตาราง

### ความสัมพันธ์ (Relationships)
- **One-to-One (1:1)**: 1 แถวในตาราง A สัมพันธ์กับ 1 แถวในตาราง B
- **One-to-Many (1:N)**: 1 แถวในตาราง A สัมพันธ์กับหลายแถวใน B
- **Many-to-Many (N:N)**: หลายแถวใน A สัมพันธ์กับหลายแถวใน B (ต้องใช้ตารางเชื่อม)

### การ Normalize
- **1NF**: แต่ละคอลัมน์มีค่าเดียว (atomic)
- **2NF**: 1NF + ทุก non-key column ขึ้นกับ primary key ทั้งหมด
- **3NF**: 2NF + ไม่มี transitive dependency (column ที่ไม่ใช่ key ขึ้นกับ non-key column อื่น)

## SQL (Structured Query Language)

### DDL (Data Definition Language)
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE
);
ALTER TABLE users ADD COLUMN age INTEGER;
DROP TABLE users;
```

### DML (Data Manipulation Language)
```sql
-- SELECT: ค้นหาข้อมูล
SELECT * FROM users WHERE age > 18;

-- INSERT: เพิ่มข้อมูล
INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com');

-- UPDATE: แก้ไขข้อมูล
UPDATE users SET age = 25 WHERE name = 'Alice';

-- DELETE: ลบข้อมูล
DELETE FROM users WHERE id = 5;
```

### JOIN (การเชื่อมตาราง)
```sql
-- INNER JOIN: เฉพาะที่ตรงกันทั้งสองตาราง
SELECT * FROM orders
INNER JOIN customers ON orders.customer_id = customers.id;

-- LEFT JOIN: ทุกแถวจากตารางซ้าย แม้ไม่มีในตารางขวา
SELECT * FROM customers
LEFT JOIN orders ON customers.id = orders.customer_id;

-- RIGHT JOIN: ทุกแถวจากตารางขวา
-- FULL OUTER JOIN: ทุกแถวจากทั้งสองตาราง
```

### Aggregation (การรวมกลุ่ม)
```sql
SELECT COUNT(*), AVG(price), MAX(price), MIN(price)
FROM products;

SELECT category, COUNT(*) as count
FROM products
GROUP BY category
HAVING count > 5;
```

### Index
- เพิ่มความเร็วในการค้นหา
- ช้าลงตอน INSERT/UPDATE
- ประเภท: B-tree, Hash, Full-text

## NoSQL (Not Only SQL)

### Document Store (MongoDB, CouchDB)
- เก็บข้อมูลเป็น JSON/BSON document
- ไม่มี schema ตายตัว
- ใช้ _id เป็น primary key

### Key-Value Store (Redis, DynamoDB)
- เก็บคู่ key-value ง่ายๆ
- ความเร็วสูงมาก
- ใช้สำหรับ cache, session

### Column-Family Store (Cassandra, HBase)
- เก็บข้อมูลเป็นคอลัมน์แถว
- เหมาะกับข้อมูลขนาดใหญ่, write-heavy

### Graph Database (Neo4j)
- เก็บเป็น node และ edge (ความสัมพันธ์)
- เหมาะกับ social network, recommendation

## ACID vs BASE

### ACID (Relational DB)
- **Atomicity**: transaction ทำสำเร็จทั้งหมดหรือไม่ทำเลย
- **Consistency**: ข้อมูลถูกต้องตามกฎเสมอ
- **Isolation**: transaction ที่ทำพร้อมกันไม่รบกวนกัน
- **Durability**: เมื่อ commit แล้ว ข้อมูลคงอยู่ถาวร

### BASE (NoSQL)
- **Basically Available**: ระบบพร้อมใช้งานตลอด
- **Soft State**: สถานะเปลี่ยนได้ตลอด
- **Eventually Consistent**: สักพักข้อมูลจะ consistent

## กลยุทธ์การใช้งานฐานข้อมูล

### Connection Pooling
- สร้างการเชื่อมต่อ DB ไว้ล่วงหน้า
- ลด overhead จากการเปิด-ปิด connection

### Caching
- Redis/Memcached สำหรับข้อมูลที่เรียกบ่อย
- Cache-aside, Write-through, Write-behind

### Sharding
- แบ่งข้อมูลไปหลาย server ตาม key (เช่น ตาม user_id)
- Scale horizontally

### Replication
- Master-Slave: Master เขียน, Slave อ่าน
- Multi-Master: เขียนได้หลาย node

### ORM (Object-Relational Mapping)
- แมปตาราง DB ไปยัง object ใน code
- เช่น: SQLAlchemy (Python), Prisma (Node.js), Hibernate (Java)
- ข้อดี: ไม่ต้องเขียน SQL โดยตรง, ป้องกัน SQL injection
- ข้อเสีย: query ซับซ้อนอาจช้า ต้องปรับ tuning
