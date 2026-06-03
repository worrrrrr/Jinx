# JavaScript — ภาษาโปรแกรมฝั่งไคลเอนต์และเซิร์ฟเวอร์

## ชนิดข้อมูลพื้นฐาน (Primitive Types)
- **String**: `"hello"`, `'world'`, `` `template` ``
- **Number**: `42`, `3.14` (เลขจำนวนเต็มและทศนิยมใช้ Number เหมือนกัน)
- **Boolean**: `true`, `false`
- **null**: ค่าว่างโดยตั้งใจ
- **undefined**: ตัวแปรที่ยังไม่ได้กำหนดค่า
- **Symbol**: ค่าที่ไม่ซ้ำกัน
- **BigInt**: `9007199254740991n`

## ตัวแปร (Variables)
```javascript
var old = "อย่าใช้";        // function scope — ไม่แนะนำ
let name = "Jinx";         // block scope — เปลี่ยนค่าได้
const PI = 3.14159;        // block scope — เปลี่ยนค่าไม่ได้
```

## ฟังก์ชัน (Functions)
```javascript
// Function declaration
function add(a, b) { return a + b; }

// Arrow function (ES6+)
const multiply = (a, b) => a * b;

// Default parameters
const greet = (name = "โลก") => `สวัสดี ${name}`;

// Rest + Spread
const sum = (...nums) => nums.reduce((a, b) => a + b, 0);
const arr = [1, 2, 3];
const copy = [...arr, 4, 5];
```

## Object + Array Destructuring
```javascript
const user = { name: "Jinx", age: 3 };
const { name, age } = user;  // destructure object

const colors = ["แดง", "เขียว", "น้ำเงิน"];
const [first, second] = colors;  // destructure array
```

## Promise + Async/Await
```javascript
// Promise
fetch("/api/data")
  .then(res => res.json())
  .then(data => console.log(data))
  .catch(err => console.error(err));

// Async/Await (ES2017)
async function getData() {
  try {
    const res = await fetch("/api/data");
    const data = await res.json();
    return data;
  } catch (err) {
    console.error("Error:", err);
  }
}
```

## ES6+ Modules
```javascript
// math.js
export const add = (a, b) => a + b;
export default class Calculator { /* ... */ }

// main.js
import Calculator, { add } from "./math.js";
```

## Common Array Methods
```javascript
const nums = [1, 2, 3, 4, 5];
nums.map(x => x * 2);           // [2, 4, 6, 8, 10]
nums.filter(x => x > 2);        // [3, 4, 5]
nums.reduce((a, b) => a + b);   // 15
nums.find(x => x === 3);        // 3
nums.some(x => x > 4);          // true
nums.every(x => x > 0);         // true
```

## Node.js พื้นฐาน
```javascript
const fs = require("fs");
const path = require("path");

// อ่านไฟล์
const data = fs.readFileSync("file.txt", "utf-8");

// อ่านแบบ async
fs.readFile("file.txt", "utf-8", (err, data) => {
  if (err) throw err;
  console.log(data);
});

// สร้าง HTTP server
const http = require("http");
http.createServer((req, res) => {
  res.writeHead(200, { "Content-Type": "text/plain" });
  res.end("Hello World");
}).listen(3000);
```

## เครื่องมือที่ใช้บ่อย
- **npm** / **yarn** / **bun**: จัดการ dependencies
- **Vite**: bundler สมัยใหม่ (เร็วกว่า webpack)
- **ESLint**: ตรวจสอบคุณภาพโค้ด
- **Prettier**: จัดรูปแบบโค้ดอัตโนมัติ
- **Jest** / **Vitest**: testing framework
