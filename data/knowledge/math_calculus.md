---
title: คณิตศาสตร์ — แคลคูลัส (Calculus)
tags: [knowledge, vault]
aliases: [math_calculus]
---
# คณิตศาสตร์ — แคลคูลัส (Calculus)

## ลิมิต (Limits)

### นิยาม
ลิมิตของฟังก์ชัน f(x) เมื่อ x เข้าใกล้ a คือค่า L ถ้า f(x) ใกล้ L เมื่อ x ใกล้ a

เขียนแทนด้วย: lim_(x→a) f(x) = L

### กฎการหาลิมิต
- lim_(x→a) [f(x) + g(x)] = lim f(x) + lim g(x)
- lim_(x→a) [f(x) × g(x)] = lim f(x) × lim g(x)
- lim_(x→a) [f(x) / g(x)] = lim f(x) / lim g(x) (ถ้า lim g(x) ≠ 0)
- lim_(x→a) c = c (c เป็นค่าคงที่)

### ลิมิตสำคัญ
- lim_(x→0) sin(x)/x = 1
- lim_(x→0) (1 - cos(x))/x = 0
- lim_(x→∞) (1 + 1/x)ˣ = e
- lim_(x→0) (eˣ - 1)/x = 1

### ความต่อเนื่อง (Continuity)
ฟังก์ชัน f(x) ต่อเนื่องที่ x = a เมื่อ:
1. f(a) มีค่า
2. lim_(x→a) f(x) มีค่า
3. f(a) = lim_(x→a) f(x)

## อนุพันธ์ (Derivatives)

### นิยาม
อนุพันธ์ของ f(x) คือ f'(x) = dy/dx = lim_(h→0) (f(x+h) - f(x)) / h

### กฎการหาอนุพันธ์
- **ค่าคงที่**: d/dx(c) = 0
- **กำลัง (Power Rule)**: d/dx(xⁿ) = n·xⁿ⁻¹
- **ผลคูณกับค่าคงที่**: d/dx(c·f(x)) = c·f'(x)
- **ผลบวก**: d/dx(f+g) = f' + g'
- **ผลคูณ (Product Rule)**: d/dx(f·g) = f'·g + f·g'
- **ผลหาร (Quotient Rule)**: d/dx(f/g) = (f'·g - f·g') / g²
- **ลูกโซ่ (Chain Rule)**: d/dx(f(g(x))) = f'(g(x)) · g'(x)

### อนุพันธ์ของฟังก์ชันพื้นฐาน
- d/dx(xⁿ) = n·xⁿ⁻¹
- d/dx(eˣ) = eˣ
- d/dx(ln(x)) = 1/x
- d/dx(sin(x)) = cos(x)
- d/dx(cos(x)) = -sin(x)
- d/dx(tan(x)) = sec²(x)

### การประยุกต์ใช้อนุพันธ์
- **ความชันของเส้นสัมผัส**: f'(a) คือความชันที่ x = a
- **จุดวิกฤต (Critical Point)**: f'(x) = 0 หรือไม่มีค่า
- **ค่าสูงสุด/ต่ำสุดสัมพัทธ์**: ดูการเปลี่ยนเครื่องหมายของ f' หรือใช้ f"
- **การทดสอบอนุพันธ์อันดับสอง**: f"(x) > 0 → จุดต่ำสุด, f"(x) < 0 → จุดสูงสุด

## ปริพันธ์ (Integrals)

### ปริพันธ์ไม่จำกัดเขต (Indefinite Integral)
คือการหาฟังก์ชันดั้งเดิม (Antiderivative)

∫ f(x) dx = F(x) + C โดยที่ F'(x) = f(x)

### สูตรพื้นฐาน
- ∫ xⁿ dx = xⁿ⁺¹/(n+1) + C (n ≠ -1)
- ∫ 1/x dx = ln|x| + C
- ∫ eˣ dx = eˣ + C
- ∫ sin(x) dx = -cos(x) + C
- ∫ cos(x) dx = sin(x) + C
- ∫ sec²(x) dx = tan(x) + C

### ปริพันธ์จำกัดเขต (Definite Integral)
∫ₐᵇ f(x) dx = F(b) - F(a) (ทฤษฎีบทมูลฐานของแคลคูลัส)

### การประยุกต์ใช้
- **พื้นที่ใต้กราฟ**: ∫ₐᵇ f(x) dx
- **พื้นที่ระหว่างสองกราฟ**: ∫ₐᵇ |f(x) - g(x)| dx
- **ปริมาตรของการหมุน (Volume of Revolution)**: π ∫ₐᵇ [f(x)]² dx

### เทคนิคการหาปริพันธ์
- **การแทนค่า (Substitution)**: u = g(x), du = g'(x)dx
- **การแยกส่วน (Integration by Parts)**: ∫ u dv = uv - ∫ v du
- **การแยกเศษส่วนย่อย (Partial Fractions)**: สำหรับฟังก์ชันตรรกยะ

## อนุพันธ์ย่อย (Partial Derivatives)

สำหรับฟังก์ชันหลายตัวแปร f(x, y):
∂f/∂x คืออนุพันธ์เทียบกับ x โดยให้ y คงที่
∂f/∂y คืออนุพันธ์เทียบกับ y โดยให้ x คงที่

### การประยุกต์
- **การหาค่าที่เหมาะสมที่สุด (Optimization)**: จุดที่ ∇f = 0 (gradient เป็นศูนย์)
- **สมการเชิงอนุพันธ์ (Differential Equations)**: สมการที่มีอนุพันธ์ของฟังก์ชันไม่ทราบค่า
