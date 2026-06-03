# การเขียนโปรแกรม — เว็บ (Web Basics)

## HTTP (Hypertext Transfer Protocol)

### HTTP Methods
- **GET**: ขอข้อมูล (อ่านอย่างเดียว, ไม่เปลี่ยนสถานะ)
- **POST**: ส่งข้อมูลใหม่ไปยัง server
- **PUT**: อัปเดตข้อมูลทั้งหมด
- **PATCH**: อัปเดตข้อมูลบางส่วน
- **DELETE**: ลบข้อมูล
- **HEAD**: เหมือน GET แต่ได้เฉพาะ header
- **OPTIONS**: ขอข้อมูล method ที่ใช้ได้

### HTTP Status Codes
**1xx (ข้อมูล)**: 100 Continue
**2xx (สำเร็จ)**: 200 OK, 201 Created, 204 No Content
**3xx (เปลี่ยนทาง)**: 301 Moved Permanently, 302 Found, 304 Not Modified
**4xx (Client Error)**: 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 429 Too Many Requests
**5xx (Server Error)**: 500 Internal Server Error, 502 Bad Gateway, 503 Service Unavailable

### HTTP Request Components
- **Method**: GET/POST/PUT/etc
- **URL**: ตำแหน่งทรัพยากร
- **Headers**: ข้อมูลเพิ่มเติม (Content-Type, Authorization, User-Agent)
- **Body**: เนื้อหาข้อมูล (สำหรับ POST, PUT)

### HTTP Response Components
- **Status Code**: รหัสผลลัพธ์
- **Headers**: Content-Type, Cache-Control, Set-Cookie
- **Body**: เนื้อหาที่ส่งกลับ

### REST API
- ใช้ HTTP method + URL ในการจัดการทรัพยากร
- Resource มักเป็น Plural เช่น /users, /products
- Stateless — แต่ละ request ต้องมีข้อมูลครบ
- Response มักเป็น JSON

## Frontend

### HTML (HyperText Markup Language)
- โครงสร้างของเว็บเพจ
- ประกอบด้วย Tags: `<div>`, `<p>`, `<a>`, `<img>`, `<h1>`-`<h6>`
- DOM (Document Object Model): โครงสร้างต้นไม้ของ HTML

### CSS (Cascading Style Sheets)
- จัดรูปแบบและตกแต่ง HTML
- Selector: `#id`, `.class`, `element`, `element.class`
- Box Model: margin → border → padding → content
- Flexbox: จัดเรียง element แบบ 1 มิติ (แถว/คอลัมน์)
- Grid: จัดเรียง element แบบ 2 มิติ

### JavaScript
- ภาษาโปรแกรมฝั่ง client (รันใน browser)
- DOM manipulation: เปลี่ยนแปลงหน้าเว็บแบบ dynamic
- Event handling: จัดการ click, submit, keyboard
- AJAX / Fetch API: ส่ง request ไป server โดยไม่โหลดหน้าใหม่
- ES6+: arrow function, promise, async/await, destructuring, module

## Backend

### Server-side Programming
- **Web Framework**: Express (Node.js), Django/Flask (Python), Spring Boot (Java), ASP.NET (C#)
- **Route**: การจับคู่ URL กับ handler function
- **Middleware**: ฟังก์ชันที่ทำงานระหว่าง request และ response
- **Session**: เก็บสถานะผู้ใช้ชั่วคราว (มักใช้ cookie + session ID)
- **Authentication**: JWT (JSON Web Token), OAuth, Session-based

### Server Types
- **Web Server**: Nginx, Apache — serve static files, reverse proxy
- **Application Server**: Express, Django, Flask — รัน business logic
- **API Server**: ส่ง JSON ให้ client

## Client-Server Communication

### Request-Response Cycle
1. Browser ส่ง HTTP request ไป server
2. Server ประมวลผล (query DB, คำนวณ)
3. Server ส่ง HTTP response กลับ
4. Browser แสดงผล

### Same-Origin Policy & CORS
- **Same-Origin Policy**: script จาก origin หนึ่ง ไม่สามารถเข้าถึง resource จากอีก origin
- **CORS (Cross-Origin Resource Sharing)**: กลไกที่ server อนุญาตให้ origin อื่นเรียกใช้ได้

## Web Security Basics

- **HTTPS**: HTTP + SSL/TLS — เข้ารหัสข้อมูลระหว่าง client-server
- **XSS (Cross-Site Scripting)**: แทรก script ไม่พึงประสงค์ → ต้อง sanitize input
- **SQL Injection**: แทรก SQL ผ่าน input → ใช้ parameterized query
- **CSRF (Cross-Site Request Forgery)**: หลอกให้ผู้ใช้กระทำโดยไม่ตั้งใจ → ใช้ CSRF token
- **Content Security Policy (CSP)**: header ควบคุม resource ที่ browser โหลด
