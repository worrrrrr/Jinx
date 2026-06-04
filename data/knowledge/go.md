---
title: [[go]] (Golang) — ภาษาเรียบง่าย เร็ว เหมาะกับ backend และระบบ分布式
tags: [knowledge, vault]
aliases: [go]
---
# [[go]] (Golang) — ภาษาเรียบง่าย เร็ว เหมาะกับ backend และระบบ分布式

## ติดตั้งและเริ่มต้น
```bash
# ติดตั้ง: https://go.dev/dl/
go version
go mod init hello-jinx
go run main.go
```

## ตัวแปรและชนิดข้อมูล
```go
package main

import "fmt"

func main() {
    // ประกาศตัวแปร
    var name string = "Jinx"
    var age int = 3
    var score float64 = 95.5
    isActive := true  // short declaration (type inference)

    // Constants
    const PI = 3.14159

    // Zero values: string="", int=0, bool=false, pointer=nil
    var s string     // ""
    var n int        // 0
}
```

## ชนิดข้อมูลพื้นฐาน
```go
bool       // true/false
string     // UTF-8, immutable

int, int8, int16, int32, int64
uint, uint8, uint16, uint32, uint64
float32, float64
complex64, complex128

byte = uint8        // alias
rune = int32        // Unicode code point
```

## Control Flow
```go
// if
if score >= 80 {
    fmt.Println("เยี่ยม!")
} else if score >= 50 {
    fmt.Println("ผ่าน")
} else {
    fmt.Println("ไม่ผ่าน")
}

// for — Go มีแค่ for ไม่มี while
for i := 0; i < 5; i++ {
    fmt.Println(i)
}

// while-style
count := 0
for count < 5 {
    count++
}

// infinite loop
for {
    break
}

// range
nums := []int{10, 20, 30}
for i, v := range nums {
    fmt.Printf("index=%d value=%d\n", i, v)
}
```

## Arrays + Slices
```go
// Array — fixed size
var arr [3]int = [3]int{1, 2, 3}

// Slice — dynamic size (ใช้บ่อยกว่า)
var slice []int = []int{1, 2, 3}
slice = append(slice, 4, 5)
sub := slice[1:3]  // [2, 3]
```

## Maps
```go
user := map[string]int{
    "jinx": 3,
    "bob":  42,
}
age, exists := user["jinx"]  // age=3, exists=true
delete(user, "bob")
```

## Functions
```go
// Multiple return values
func divide(a, b float64) (float64, error) {
    if b == 0 {
        return 0, fmt.Errorf("cannot divide by zero")
    }
    return a / b, nil
}

// Named return values
func split(sum int) (x, y int) {
    x = sum * 4 / 9
    y = sum - x
    return  // naked return
}

// Variadic
func sum(nums ...int) int {
    total := 0
    for _, n := range nums {
        total += n
    }
    return total
}
```

## Struct + Methods
```go
type User struct {
    Name string
    Age  int
}

// Method — value receiver
func (u User) Greet() string {
    return fmt.Sprintf("สวัสดี %s", u.Name)
}

// Method — pointer receiver (แก้ค่าได้)
func (u *User) Birthday() {
    u.Age++
}

user := User{Name: "Jinx", Age: 3}
fmt.Println(user.Greet())
user.Birthday()
```

## Interfaces
```go
type Speaker interface {
    Speak() string
}

type Dog struct{}
func (d Dog) Speak() string { return "เห่า!" }

type Cat struct{}
func (c Cat) Speak() string { return "เหมียว!" }

func makeSound(s Speaker) {
    fmt.Println(s.Speak())
}
// Go ใช้ structural typing — ไม่ต้องประกาศ implements อย่างชัดเจน
```

## Goroutines + Channels (Concurrency)
```go
// goroutine — เริ่มด้วย go
go func() {
    fmt.Println("ทำงานพร้อมกัน!")
}()

// channel — ส่งข้อมูลระหว่าง goroutine
ch := make(chan string)
go func() {
    ch <- "hello from goroutine"
}()
msg := <-ch
fmt.Println(msg)  // "hello from goroutine"
```

## Error Handling
```go
// Go ไม่มี try/catch ใช้ error เป็นค่ากลับ
f, err := os.Open("file.txt")
if err != nil {
    log.Fatal(err)
}
defer f.Close()  // รันตอนฟังก์ชันจบ

// Custom error
type NotFoundError struct{ Name string }
func (e *NotFoundError) Error() string {
    return fmt.Sprintf("not found: %s", e.Name)
}
```

## Package Layout
```
project/
├── go.mod
├── main.go
├── handler/
│   └── user.go       // package handler
└── model/
    └── user.go       // package model
```
