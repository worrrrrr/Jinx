---
title: การเขียนโปรแกรม — ระบบปฏิบัติการและเครือข่าย (OS & Networking)
tags: [knowledge, vault]
aliases: [os_networking]
---
# การเขียนโปรแกรม — ระบบปฏิบัติการและเครือข่าย (OS & Networking)

## ระบบปฏิบัติการ (Operating System)

### หน้าที่หลัก
1. **Process Management**: จัดการโปรแกรมที่กำลังทำงาน
2. **Memory Management**: จัดสรรและจัดการหน่วยความจำ
3. **File System**: จัดการไฟล์และไดเรกทอรี
4. **Device Management**: จัดการอุปกรณ์ I/O
5. **Security & Access Control**: ควบคุมสิทธิ์การเข้าถึง

### Process vs Thread
- **Process**: โปรแกรมที่กำลังทำงาน มีหน่วยความจำของตัวเอง
  - การสื่อสารระหว่าง process (IPC): pipe, socket, shared memory
- **Thread**: หน่วยย่อยใน process แชร์หน่วยความจำร่วมกัน
  - เบากว่า process, สลับ context เร็วกว่า

### Process States
New → Ready → Running → Waiting → Terminated

### Scheduling [[algorithms]]
- **FCFS (First Come First Serve)**: มาตามลำดับ
- **SJF (Shortest Job First)**: งานสั้นมาก่อน
- **Round Robin**: วนรอบให้เวลางานละเท่าๆ กัน
- **Priority Scheduling**: งานสำคัญมาก่อน

### Memory Management
- **Paging**: แบ่งหน่วยความจำเป็นหน้า (page) ขนาดเท่ากัน
- **Virtual Memory**: ใช้พื้นที่ disk เสริม RAM (swap)
- **Fragmentation**: Internal (ใน page) และ External (ระหว่าง partition)
- **TLB (Translation Lookaside Buffer)**: cache สำหรับแปลง virtual → physical address

### File System
- **Directory Structure**: tree, DAG (มี link)
- **Permissions**: อ่าน (r), เขียน (w), execute (x) สำหรับ user/group/other
- **inode (Unix)**: เก็บ metadata ของไฟล์ (ยกเว้นชื่อ)
- **常见的FS**: ext4, NTFS, FAT32, APFS

### Deadlock
สี่เงื่อนไขที่ทำให้เกิด deadlock:
1. Mutual Exclusion
2. Hold and Wait
3. No Preemption
4. Circular Wait

## เครือข่ายคอมพิวเตอร์ (Computer Networking)

### OSI Model (7 Layers)
| Layer | หน้าที่ | ตัวอย่าง |
|-------|--------|---------|
| 7 Application | บริการเครือข่ายสำหรับ app | HTTP, FTP, SMTP |
| 6 Presentation | แปลงข้อมูล, เข้ารหัส | TLS/SSL |
| 5 Session | จัดการ session การสื่อสาร | |
| 4 Transport | ส่งข้อมูลแบบ end-to-end | TCP, UDP |
| 3 Network | เส้นทางและการส่งต่อ | IP, ICMP |
| 2 Data Link | ส่งข้อมูลในเครือข่ายเดียวกัน | Ethernet, Wi-Fi |
| 1 Physical | ส่ง bits ผ่านสาย/คลื่น | |

### TCP/IP Model (4 Layers)
- **Application**: HTTP, DNS, SSH
- **Transport**: TCP, UDP
- **Internet**: IP (IPv4, IPv6), ICMP
- **Link**: Ethernet, Wi-Fi

### TCP (Transmission Control Protocol)
- **Connection-oriented**: ต้องสร้าง connection ก่อน
- **Three-way handshake**: SYN → SYN-ACK → ACK
- **เชื่อถือได้**: มีการรับคำตอบ (ACK), ส่งซ้ำเมื่อหาย
- **Flow control**: รับได้เท่าไหร่ (Window size)
- **Congestion control**: ลดความเร็วเมื่อ network แออัด

### UDP (User Datagram Protocol)
- **Connectionless**: ส่งเลย ไม่ต้องสร้าง connection
- **ไม่เชื่อถือได้**: ไม่มีการรับประกันว่าไปถึง
- **เร็วกว่า TCP**: ใช้กับ video streaming, DNS, gaming

### IP Address
- **IPv4**: 32 bits (192.168.1.1) มี 4.3 พันล้านที่อยู่
- **IPv6**: 128 bits (2001:db8::1) แก้ปัญหา IPv4 หมด
- **Public IP**: ใช้บน internet
- **Private IP**: ใช้ใน LAN (10.x.x.x, 172.16-31.x.x, 192.168.x.x)
- **Subnet Mask**: บอกส่วน network vs host

### DNS (Domain [[name]] System)
- แปลง domain [[name]] (google.com) → IP address
- **Hierarchical**: . → .com → google.com → www.google.com
- Record types: A (IPv4), AAAA (IPv6), CNAME (alias), MX (mail), NS (nameserver)

### Ports ที่พบบ่อย
- 80: HTTP
- 443: HTTPS
- 22: SSH
- 21: FTP
- 25: SMTP
- 53: DNS
- 3306: MySQL
- 5432: PostgreSQL
- 6379: Redis
- 27017: MongoDB

### Load Balancer
- กระจาย traffic ไปหลาย server
- **Round Robin**: สลับทีละตัว
- **Least Connections**: ส่งไปตัวที่รับน้อยที่สุด
- **IP Hash**: ใช้ client IP เพื่อให้ session อยู่ที่เดิม

### Proxy
- **Forward Proxy**: proxy แทน client ไปขอข้อมูล
- **Reverse Proxy**: proxy รับ request แล้วส่งต่อให้ server หลังบ้าน (เช่น Nginx)
