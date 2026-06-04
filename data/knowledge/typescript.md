---
title: [[typescript]] — [[javascript]] + ระบบชนิดข้อมูล (Types)
tags: [knowledge, vault]
aliases: [typescript]
---
# [[typescript]] — [[javascript]] + ระบบชนิดข้อมูล (Types)

[[typescript]] เป็น superset ของ [[javascript]] ที่เพิ่มระบบ type ช่วยให้จับบั๊กได้ตั้งแต่ตอนเขียนโค้ด

## ติดตั้งและใช้งาน
```bash
npm install -g typescript
tsc --init          # สร้าง tsconfig.json
npx tsc             # compile .ts → .js
```

## ชนิดพื้นฐาน (Primitive Types)
```typescript
let name: string = "Jinx";
let age: number = 3;
let isActive: boolean = true;
let data: null = null;
let id: undefined = undefined;
let anything: any = "อะไรก็ได้";       // ไม่แนะนำ—เสียประโยชน์จาก type
let unknown: unknown = "ต้องตรวจสอบก่อนใช้";  // ปลอดภัยกว่า any
```

## Array และ Tuple
```typescript
let nums: number[] = [1, 2, 3];
let names: Array<string> = ["a", "b"];
let tuple: [string, number] = ["Jinx", 3];  // fixed length + type
```

## Interface และ Type Alias
```typescript
interface User {
  id: number;
  name: string;
  email?: string;        // optional
  readonly createdAt: Date;  // แก้ไขไม่ได้หลังจากกำหนด
}

type Point = {
  x: number;
  y: number;
};

type Status = "active" | "inactive" | "pending";  // union type
```

## Function Types
```typescript
function add(a: number, b: number): number {
  return a + b;
}

// Arrow function
const multiply = (a: number, b: number): number => a * b;

// Optional + default parameters
function greet(name: string, title?: string): string {
  return `${title || "สวัสดี"} ${name}`;
}

// Overloads
function process(x: number): number;
function process(x: string): string;
function process(x: any): any {
  return typeof x === "number" ? x * 2 : x.toUpperCase();
}
```

## Generics
```typescript
function identity<T>(arg: T): T {
  return arg;
}

const num = identity<number>(42);   // type = number
const str = identity("hello");       // type = string (infer)

interface ApiResponse<T> {
  status: number;
  data: T;
  message: string;
}

type UserResponse = ApiResponse<{ id: number; name: string }>;
```

## Utility Types (built-in)
```typescript
interface User { id: number; name: string; email: string; }

type PartialUser = Partial<User>;     // ทุก field เป็น optional
type RequiredUser = Required<User>;   // ทุก field จำเป็น
type JustName = Pick<User, "name">;   // เลือกเฉพาะ field
type NoEmail = Omit<User, "email">;   // ยกเว้น field
type ReadonlyUser = Readonly<User>;   // readonly ทั้งหมด

const record: Record<string, number> = { a: 1, b: 2 };
```

## Enum
```typescript
enum Direction {
  Up = "UP",
  Down = "DOWN",
  Left = "LEFT",
  Right = "RIGHT",
}

const dir: Direction = Direction.Up;
```

## Class + Decorators (experimental)
```typescript
class Animal {
  constructor(public name: string) {}  // auto-create this.name

  speak(): string {
    return "...";
  }
}

class Dog extends Animal {
  speak(): string {
    return "เห่า!";
  }
}
```

## Type Narrowing
```typescript
function format(value: string | number): string {
  if (typeof value === "number") {
    return value.toFixed(2);       // TS รู้ว่า value เป็น number
  }
  return value.trim();             // TS รู้ว่า value เป็น string
}
```

## tsconfig.json สำคัญ
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "strict": true,
    "outDir": "./dist",
    "rootDir": "./src",
    "esModuleInterop": true
  }
}
```
