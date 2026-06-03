# การเขียนโปรแกรม — ขั้นตอนวิธี (Algorithms)

## การค้นหา (Searching)

### Linear Search
- ตรวจสอบทีละตัวตั้งแต่ต้นจนเจอ
- Time: O(n), Space: O(1)

### Binary Search
- ใช้กับข้อมูลที่เรียงลำดับแล้ว
- แบ่งครึ่งทีละครั้ง
- Time: O(log n), Space: O(1)

### Depth-First Search (DFS)
- สำรวจกราฟ/ต้นไม้โดยไปให้ลึกที่สุดก่อน
- ใช้ Stack (หรือ recursion)
- Time: O(V+E), Space: O(V)

### Breadth-First Search (BFS)
- สำรวจกราฟ/ต้นไม้เป็นชั้นๆ
- ใช้ Queue
- Time: O(V+E), Space: O(V)
- ใช้หา shortest path ในกราฟที่น้ำหนักเท่ากัน

## การจัดเรียง (Sorting)

### Bubble Sort
- เปรียบเทียบแล้วสลับที่ติดกันไปเรื่อยๆ
- Time: O(n²), Space: O(1)

### Selection Sort
- หาค่าที่น้อยที่สุดแล้วสลับไปไว้ด้านหน้า
- Time: O(n²), Space: O(1)

### Insertion Sort
- หยิบทีละตัวแล้วแทรกในตำแหน่งที่ถูกต้อง
- Time: O(n²) แต่ดีกับข้อมูลเกือบเรียงแล้ว
- Space: O(1)

### Merge Sort
- แบ่งครึ่ง → เรียงแต่ละส่วน → รวม
- Time: O(n log n), Space: O(n)

### Quick Sort
- เลือก pivot → แบ่งเป็นสองส่วน → เรียงแต่ละส่วน
- Time: เฉลี่ย O(n log n), แย่สุด O(n²)
- Space: O(log n)

## โครงสร้างข้อมูล (Data Structures)

### Stack (LIFO)
- push: เพิ่มข้อมูล, pop: ดึงข้อมูลบนสุดออก
- ใช้ใน undo, function call stack

### Queue (FIFO)
- enqueue: เพิ่มข้อมูลต่อท้าย, dequeue: ดึงข้อมูลหน้าสุด
- ใช้ใน BFS, print queue

### Linked List
- โหนดแต่ละตัวชี้ไปยังโหนดถัดไป
- Single: pointer ไปข้างหน้าเท่านั้น
- Double: pointer ไปทั้งหน้าและหลัง
- Insert/Delete: O(1) ที่ตำแหน่งที่รู้, Search: O(n)

### Tree
- **Binary Tree**: แต่ละโหนดมีลูกสูงสุด 2 ตัว
- **Binary Search Tree (BST)**: ลูกซ้าย < parent < ลูกขวา
- **Heap**: parent มีค่ามากกว่า/น้อยกว่าลูกเสมอ
  - Max Heap: parent > ลูก
  - Min Heap: parent < ลูก
- **Trie**: ต้นไม้สำหรับค้นหาคำ (prefix tree)

### Graph
- **Directed**: เส้นเชื่อมมีทิศทาง
- **Undirected**: เส้นเชื่อมไม่มีทิศทาง
- **Weighted**: เส้นเชื่อมมีน้ำหนัก
- **Adjacency List**: แต่ละโหนดมี list ของโหนดใกล้เคียง
- **Adjacency Matrix**: ตาราง V×V

### Hash Table (Dictionary)
- เก็บคู่ key-value
- Search/Insert/Delete โดยเฉลี่ย O(1)
- ใช้ hash function แปลง key เป็น index
- อาจเกิด collision (แก้ด้วย chaining หรือ open addressing)

## เทคนิคการออกแบบอัลกอริทึม

### Divide and Conquer
- แบ่งปัญหาเป็นส่วนย่อย → แก้แต่ละส่วน → รวมผลลัพธ์
- เช่น Merge Sort, Binary Search, Quick Sort

### Dynamic Programming (DP)
- แก้ปัญหาย่อยแล้วเก็บผลลัพธ์ไว้ใช้ใหม่
- ใช้เมื่อปัญหาย่อยซ้ำกัน (Overlapping subproblems)
- Top-down (Memoization) หรือ Bottom-up (Tabulation)
- เช่น Fibonacci, Knapsack, Shortest Path

### Greedy Algorithm
- เลือกทางที่ดีที่สุดในแต่ละขั้นตอน
- ไม่รับประกันผลลัพธ์ที่ดีที่สุดเสมอไป
- เช่น Dijkstra, Huffman Coding

### Backtracking
- ลองทุกความเป็นไปได้ ถ้าไม่ได้ผลก็ย้อนกลับ
- เช่น N-Queens, Sudoku solver

## อัลกอริทึมกราฟ (Graph Algorithms)

### Dijkstra's Algorithm
- หา shortest path จาก node หนึ่งไปยังทุก node (น้ำหนักไม่ติดลบ)
- Time: O(V²) หรือ O(E log V) ด้วย priority queue

### Bellman-Ford
- หา shortest path ที่รองรับน้ำหนักติดลบ
- Time: O(VE)

### Floyd-Warshall
- หา shortest path ระหว่างทุกคู่ node
- Time: O(V³)

### Union-Find (Disjoint Set Union)
- ใช้ตรวจสอบว่า node อยู่ใน component เดียวกัน
- Time: O(α(n)) เกือบคงที่
- ใช้ใน Kruskal's MST, ตรวจ cycle ในกราฟ
