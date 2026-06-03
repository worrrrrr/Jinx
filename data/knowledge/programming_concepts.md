# การเขียนโปรแกรม — แนวคิดพื้นฐาน (Programming Concepts)

## ตัวแปรและชนิดข้อมูล (Variables & Data Types)

### ชนิดข้อมูลพื้นฐาน
- **Integer (จำนวนเต็ม)**: 1, -5, 1000
- **Float (ทศนิยม)**: 3.14, -0.001, 2.0
- **String (ข้อความ)**: "hello", 'Python'
- **Boolean (ตรรกะ)**: True, False
- **None/Null**: ค่าว่าง

### โครงสร้างข้อมูลพื้นฐาน
- **Array / List**: ลำดับของข้อมูล [1, 2, 3]
- **Dictionary / Map / Object**: คู่คีย์-ค่า {"name": "Jinx"}
- **Set**: เซตที่ไม่มีสมาชิกซ้ำ {1, 2, 3}
- **Tuple**: ลำดับที่แก้ไขไม่ได้ (1, 2, 3)

## ตัวดำเนินการ (Operators)

- **เลขคณิต (Arithmetic)**: +, -, *, /, %, ** (ยกกำลัง)
- **เปรียบเทียบ (Comparison)**: ==, !=, <, >, <=, >=
- **ตรรกะ (Logical)**: and, or, not
- **กำหนดค่า (Assignment)**: =, +=, -=, *=, /=

## โครงสร้างควบคุม (Control Flow)

### เงื่อนไข (Conditionals)
```
if condition:
    # ทำเมื่อ condition เป็น True
elif other_condition:
    # ทำเมื่อ other_condition เป็น True
else:
    # ทำเมื่อไม่มีเงื่อนไขใดเป็น True
```

### ลูป (Loops)
```
# For loop — วนตามจำนวนที่กำหนด
for item in collection:
    # ทำกับแต่ละ item

# While loop — วนจนกว่า condition เป็น False
while condition:
    # ทำซ้ำไปเรื่อยๆ
```

## ฟังก์ชัน (Functions)

### การนิยามฟังก์ชัน
```
def function_name(parameter1, parameter2):
    # กระทำบางอย่าง
    return result
```

### แนวคิดสำคัญ
- **Parameter**: ตัวแปรที่ส่งเข้าไปในฟังก์ชัน
- **Return value**: ค่าที่ฟังก์ชันส่งกลับ
- **Side effect**: การเปลี่ยนแปลงสถานะภายนอกฟังก์ชัน
- **Scope**: ขอบเขตการเข้าถึงตัวแปร (global, local)
- **Recursion**: ฟังก์ชันเรียกตัวเอง

## การเขียนโปรแกรมเชิงวัตถุ (OOP)

### แนวคิดหลัก
1. **Class**: แม่แบบสำหรับสร้างวัตถุ
2. **Object**: อินสแตนซ์ของ class
3. **Encapsulation**: ซ่อนรายละเอียดภายใน เปิดเผยเฉพาะ interface
4. **Inheritance**: สืบทอดคุณสมบัติจาก class แม่
5. **Polymorphism**: วัตถุต่างชนิดกันตอบสนองต่อ method เดียวกันต่างกัน

### ตัวอย่าง
```
class Animal:
    def __init__(self, name):
        self.name = name
    def speak(self):
        pass  # ซับคลาสต้อง implement เอง

class Dog(Animal):
    def speak(self):
        return "เห่า!"
```

## การจัดการข้อผิดพลาด (Error Handling)

```
try:
    # โค้ดที่อาจเกิดข้อผิดพลาด
except SomeException as e:
    # จัดการเมื่อเกิดข้อผิดพลาด
finally:
    # ทำงานไม่ว่ากรณีใด
```

### ชนิดของ error ทั่วไป
- **SyntaxError**: ไวยากรณ์ไม่ถูกต้อง
- **TypeError**: ชนิดข้อมูลไม่ตรง
- **IndexError**: เกินขอบเขตของ list
- **KeyError**: ไม่มีคีย์ใน dict
- **ValueError**: ค่าไม่ถูกต้อง
- **FileNotFoundError**: ไม่พบไฟล์

## กระบวนทัศน์การเขียนโปรแกรม (Paradigms)

### Procedural Programming
เขียนเป็นลำดับขั้นตอน ใช้ฟังก์ชันในการจัดระเบียบ

### Object-Oriented Programming (OOP)
จัดกลุ่มข้อมูลและพฤติกรรมเป็นวัตถุ เน้นการสืบทอดและห่อหุ้ม

### Functional Programming
เน้นการคำนวณด้วยฟังก์ชัน หลีกเลี่ยง side effect
- First-class functions, Pure functions, Immutability
- Map, Filter, Reduce

### หลักการออกแบบ (Design Principles)
- **DRY (Don't Repeat Yourself)**: ไม่เขียนโค้ดซ้ำซ้อน
- **KISS (Keep It Simple, Stupid)**: ทำให้เรียบง่าย
- **SOLID**: 5 หลักการออกแบบ OOP
  - S: Single Responsibility
  - O: Open/Closed
  - L: Liskov Substitution
  - I: Interface Segregation
  - D: Dependency Inversion

## Complexity (Big O Notation)

### Time Complexity
บอกว่าอัลกอริทึมใช้เวลาเพิ่มขึ้นเท่าไหร่เมื่อ input ใหญ่ขึ้น
- **O(1)**: คงที่ (Constant) — เช่น เข้าถึง array index
- **O(log n)**: ลอการิทึม — เช่น Binary Search
- **O(n)**: เชิงเส้น (Linear) — เช่น วนลูป array
- **O(n log n)**: — เช่น Merge Sort
- **O(n²)**: กำลังสอง — เช่น Nested loop
- **O(2ⁿ)**: เอกซ์โพเนนเชียล — เช่น Recursive Fibonacci
