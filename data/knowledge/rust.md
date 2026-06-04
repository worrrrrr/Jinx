---
title: [[rust]] — ภาษาโปรแกรมระบบ ปลอดภัยและเร็ว
tags: [knowledge, vault]
aliases: [rust]
---
# [[rust]] — ภาษาโปรแกรมระบบ ปลอดภัยและเร็ว

[[rust]] เน้นความปลอดภัยของหน่วยความจำ (memory safety) โดยไม่ต้องใช้ garbage collector

## ติดตั้ง
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
rustc --version
cargo --version
```

## โปรเจกต์แรก
```bash
cargo new hello-jinx
cd hello-jinx
cargo run
```

## ตัวแปรและชนิดข้อมูล
```rust
let x: i32 = 42;           // จำนวนเต็ม 32 บิต
let y: f64 = 3.14;         // ทศนิยม 64 บิต
let is_true: bool = true;  // boolean
let letter: char = 'ก';    // Unicode 4 bytes

// Immutable ตามค่าเริ่มต้น
let mut count = 0;         // ใช้ mut เพื่อแก้ค่าได้
count += 1;

// Shadowing
let name = "Jinx";
let name = name.len();     // ประกาศซ้ำได้ เปลี่ยน type ได้
```

## String
```rust
let s1: &str = "string slice";  // immutable, fixed size
let s2: String = String::from("owned string");  // heap, growable
let slice = &s2[0..5];          // slice
```

## Ownership — หัวใจของ [[rust]]
```rust
// กฎ 3 ข้อ:
// 1. ค่าแต่ละค่ามี owner หนึ่งเดียว
// 2. ยืมได้หลายครั้ง (&T) หรือ ยืมแบบเปลี่ยนค่าได้ครั้งเดียว (&mut T)
// 3. owner หาย = ค่าถูกลบ (drop)

let s = String::from("hello");
let t = s;               // move: s ใช้ไม่ได้อีกต่อไป (ถูกย้ายไป t)

let a = String::from("hello");
let b = &a;              // borrow: a ยังใช้ได้
println!("{} {}", a, b);

let mut x = String::from("hello");
let y = &mut x;          // borrow แบบเปลี่ยนค่าได้
y.push_str(" world");    // ตอนนี้ y เท่านั้นที่เข้าถึง x ได้
```

## ฟังก์ชัน
```rust
fn add(a: i32, b: i32) -> i32 {
    a + b  // expression — ไม่ต้อง return
}

fn greet(name: &str) -> String {
    format!("สวัสดี {}", name)
}
```

## Struct + Method
```rust
struct User {
    name: String,
    age: u8,
}

impl User {
    fn new(name: &str, age: u8) -> Self {
        Self { name: name.to_string(), age }
    }

    fn is_adult(&self) -> bool {
        self.age >= 18
    }
}

let user = User::new("Jinx", 3);
println!("{}", user.is_adult());  // false
```

## Enum + Pattern Matching
```rust
enum Status {
    Active,
    Inactive,
    Pending { reason: String },
}

fn describe(status: Status) -> &'static str {
    match status {
        Status::Active => "กำลังทำงาน",
        Status::Inactive => "หยุดทำงาน",
        Status::Pending { reason: _ } => "รอการยืนยัน",
    }
}

// Option — ไม่มี null
fn find_user(id: u32) -> Option<String> {
    if id == 1 { Some("Jinx".to_string()) } else { None }
}

// Result — error handling
fn divide(a: f64, b: f64) -> Result<f64, String> {
    if b == 0.0 { Err("หารด้วยศูนย์".into()) } else { Ok(a / b) }
}
```

## Error Handling
```rust
// unwrap — ใช้เฉพาะตอนมั่นใจ 100%
let x = "42".parse::<i32>().unwrap();

// ? operator — ส่ง error ต่อ
fn read_file(path: &str) -> Result<String, std::io::Error> {
    std::fs::read_to_string(path)
}
```

## Generics + Traits
```rust
trait Speak {
    fn speak(&self) -> String;
}

struct Dog;
impl Speak for Dog {
    fn speak(&self) -> String { "เห่า!".into() }
}

// Generic function
fn make_sound<T: Speak>(thing: T) -> String {
    thing.speak()
}
```

## เครื่องมือเด่น
- **Cargo**: build system + package manager
- **rustfmt**: formatter (cargo fmt)
- **clippy**: linter (cargo clippy)
- **cargo test**: unit + integration tests
- **cargo doc**: สร้างเอกสารจาก doc comments (///)
