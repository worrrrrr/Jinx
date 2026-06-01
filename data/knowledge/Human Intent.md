# Intent ของมนุษย์ (Human Intent)

## Executive Summary

**Intent (เจตจำนง/ความตั้งใจ)** คือแรงขับเคลื่อนเบื้องหลังทุกการกระทำ คำพูด หรือการค้นหาของมนุษย์ ในบริบทของ [[System Architecture]] และ [[AI Interaction]] การเข้าใจ Intent ไม่ใช่แค่การอ่านข้อความ (Literal text) แต่คือการถอดรหัสเพื่อหา **"เป้าหมายที่แท้จริง" (Underlying Goal)** ที่ซ่อนอยู่ใต้พฤติกรรมนั้น

## Key Insights

- **Text $\neq$ Intent:** สิ่งที่มนุษย์พิมพ์หรือพูด มักเป็นเพียงวิธีการ (Means) ไม่ใช่เป้าหมายสูงสุด (End goal)
    
- **Context Dependency:** Intent เปลี่ยนแปลงตามบริบท (เวลา, สถานที่, อารมณ์, และประวัติการใช้งาน) ระบบที่ขาด [[Context Awareness]] จะตีความ Intent ผิดพลาด
    
- **Actionability:** การเข้าใจ Intent ที่สมบูรณ์แบบ ต้องนำไปสู่การคัดเลือก Action หรือ Response ที่มีประสิทธิภาพที่สุด (Lowest Friction)
    

## Core Concepts & Classification

ในการออกแบบระบบจำแนกเจตจำนง (Intent Classification) สามารถแบ่ง Intent หลักของมนุษย์ออกเป็น 4 ประเภท (อ้างอิงตามหลัก Search & Interaction Intent):

### 1. Informational Intent (ต้องการรู้)

- **Core:** มนุษย์ต้องการคำตอบ ความรู้ หรือคำอธิบายเพื่อลดความไม่รู้ (Uncertainty)
    
- **พฤติกรรม:** การถามคำถาม "ทำไม", "อย่างไร", "คืออะไร"
    
- **System Handling:** คืนค่าข้อมูลที่กระชับ ถูกต้อง และตรงประเด็น (Knowledge Retrieval)
    

### 2. Navigational Intent (ต้องการไป)

- **Core:** มนุษย์มีจุดหมายปลายทางที่แน่ชัดในใจอยู่แล้ว ทั้งในโลกจริงหรือโลกดิจิทัล
    
- **พฤติกรรม:** การค้นหาชื่อแบรนด์, ชื่อ URL, หรือคำสั่งทางลัดเพื่อเข้าสู่ระบบ/ฟังก์ชันเฉพาะ
    
- **System Handling:** ส่งผู้ใช้ไปยังจุดหมายโดยตรง ลดขั้นตอนการเปลี่ยนหน้า (Routing/Deep Linking)
    

### 3. Transactional Intent (ต้องการทำ/ซื้อ)

- **Core:** มนุษย์ต้องการทำธุรกรรม หรือทำภารกิจให้สำเร็จ (Action-oriented)
    
- **พฤติกรรม:** "ซื้อ...", "ดาวน์โหลด...", "สมัครสมาชิก..."
    
- **System Handling:** สร้าง Interface ที่ซับซ้อนน้อยที่สุด ปลอดภัย และจบกระบวนการได้รวดเร็ว (Conversion Optimization)
    

### 4. Commercial Investigation (ต้องการเปรียบเทียบ)

- **Core:** อยู่กึ่งกลางระหว่าง Informational และ Transactional มนุษย์รู้ว่าจะซื้อ/ทำอะไร แต่ต้องการข้อมูลสนับสนุนการตัดสินใจ
    
- **พฤติกรรม:** "รีวิว...", "เปรียบเทียบ X กับ Y", "รุ่นไหนดีที่สุด"
    
- **System Handling:** นำเสนอข้อมูลในรูปแบบ [[Data Matrix]] หรือตารางเปรียบเทียบที่เห็นภาพชัดเจน
    

## Engineering the Intent Architecture

เบื้องหลังการทำงานของ AI และระบบค้นหาในการจับ Intent ประกอบด้วย Pipeline สำคัญ:

Python

```
def process_user_input(user_input, user_context):
    # 1. ล้างข้อมูลรบกวน (Noise Reduction)
    cleaned_text = preprocess(user_input)
    
    # 2. วิเคราะห์ความหมายลึกซึ้ง (Semantic Analysis)
    embedding = generate_embedding(cleaned_text)
    
    # 3. จับคู่เจตจำนงและบริบท (Intent & Context Matching)
    predicted_intent = intent_classifier_model(embedding)
    resolved_context = parse_context(user_context)
    
    # 4. เลือก Action ที่ตอบสนอง Intent ได้ดีที่สุด
    return execute_system_action(predicted_intent, resolved_context)
```

- **[[Natural Language Understanding (NLU)]]:** ใช้ในขั้นตอนการทำ Intent Classification และ Entity Extraction (สกัดตัวแปรที่จำเป็น)
    
- **[[Vector Embeddings]]:** แปลงข้อความของมนุษย์ให้อยู่ในรูปแบบพิกัดทางคณิตศาสตร์ เพื่อหาความใกล้เคียงทางความหมาย (Semantic Similarity) มากกว่าการจับคู่คำพ้องเสียง (Keyword Matching)
# Systemic Architecture of Human Intent: 30 Conceptual Archetypes

## Executive Summary

การจำแนก Intent ในระดับ System Architecture และ Cognitive Computing เพื่อใช้ในการทำ Matrix Mapping, Vector Space Search และ NLU Modeling โดยแบ่งออกเป็น 30 รูปแบบเชิงลึกตามมิติพฤติกรรม จิตวิทยา และโครงสร้างข้อมูล

## 1. Core Cognitive & Architectural Intents

### [[1. Explanatory Intent]] (ต้องการคำอธิบายเชิงลึก)

- **Context:** ผู้ใช้ต้องการเข้าใจกลไกการทำงานระดับ Root Cause ไม่ใช่แค่คำตอบพื้นฐาน
    
- **Key Takeaways:** ระบบต้องส่งมอบ White-paper, First-principles breakdown หรือ [[Structural Diagram]]
    
- **Core Principle:** การลด Entropy ของความไม่รู้ในระบบปิด (Epistemic Anxiety)
    

### [[2. Diagnostic Intent]] (ต้องการตรวจหาสาเหตุ)

- **Context:** มี Error หรือความผิดปกติเกิดขึ้น ผู้ใช้ต้องการระบุจุดที่พัง (Root Cause Analysis)
    
- **Key Takeaways:** ต้องการ Stack Trace, Log Analysis หรือการเปรียบเทียบอาการ (Symptoms Matching)
    
- **Core Principle:** State Verification — การตรวจสอบว่าระบบเปลี่ยนจาก State ปกติไปสู่ Fault State ได้อย่างไร
    

### [[3. Optimization Intent]] (ต้องการเพิ่มประสิทธิภาพ)

- **Context:** ระบบหรือกระบวนการทำงานได้ แต่ผู้ใช้ต้องการลด Latency, Resource หรือ Cost
    
- **Key Takeaways:** นำเสนอ Refactoring Patterns, [[Algorithmic Efficiency]] หรือการปรับจูน Parameter
    
- **Core Principle:** Pareto Efficiency — การรีดประสิทธิภาพสูงสุดภายใต้ข้อจำกัดที่มีอยู่
    

### [[4. Verification Intent]] (ต้องการความถูกต้องแม่นยำ)

- **Context:** ผู้ใช้มีสมมติฐานหรือชุดข้อมูลอยู่แล้ว แต่ต้องการระบบช่วย Cross-check เพื่อความมั่นใจ
    
- **Key Takeaways:** การเปรียบเทียบข้อมูลกับ Single Source of Truth หรือการทำ Validation Logic
    
- **Core Principle:** Deterministic Proof — มนุษย์ต้องการลดความเสี่ยงจากการตัดสินใจผิดพลาด (Risk Mitigation)
    

### [[5. Synthesis Intent]] (ต้องการสรุปและเชื่อมโยง)

- **Context:** มีข้อมูลดิบจำนวนมาก (Unstructured Data) ต้องการบีบอัดให้เหลือเฉพาะแก่น
    
- **Key Takeaways:** การทำ Abstractive Summarization, [[Knowledge Graph]] หรือ Mind Mapping
    
- **Core Principle:** Information Compression — การลด Payload ของข้อมูลเพื่อให้สมองประมวลผลได้ทันที
    

## 2. Dynamic Operational Intents

### [[6. Automation Intent]] (ต้องการส่งต่อให้ระบบทำแทน)

- **Context:** งานซ้ำซ้อนที่มีรูปแบบชัดเจน ผู้ใช้ต้องการเปลี่ยน Manual Task ให้เป็น [[Cron Job]] หรือ Script
    
- **Key Takeaways:** การสกัด Logic ออกมาเป็น YAML/JSON Config หรือ Pipeline Definition
    
- **Core Principle:** Cognitive Load Offloading — การลดภาระสมองไปให้ Machine Pipeline
    

### [[7. Predictive Intent]] (ต้องการคาดการณ์อนาคต)

- **Context:** ต้องการรู้แนวโน้ม (Trend) หรือผลลัพธ์ที่จะเกิดขึ้นจากข้อมูลในอดีต
    
- **Key Takeaways:** การใช้ [[Time-Series Forecasting]], Probability Distribution หรือ Simulation
    
- **Core Principle:** Deterministic Chaos Reduction — การสร้างฉากทัศน์เพื่อเตรียมพร้อมรับความไม่แน่นอน
    

### [[8. Comparative Intent]] (ต้องการเปรียบเทียบมิติ)

- **Context:** อยู่ในสภาวะตัดสินใจเลือกสิ่งที่ดีที่สุดจากตัวเลือกที่มี Attribute ใกล้เคียงกัน
    
- **Key Takeaways:** [[Data Matrix]], Trade-off Analysis, Pros & Cons Table
    
- **Core Principle:** Multi-Criteria Decision Making (MCDM)
    

### [[9. Generative Intent]] (ต้องการสร้างสิ่งใหม่จากศูนย์)

- **Context:** ผู้ใช้มีแนวคิดคร่าวๆ (Prompt/Seed) แต่ต้องการ Asset หรือ Code ที่สมบูรณ์
    
- **Key Takeaways:** Output ที่เป็น Structural Text, Code Base, หรือ Object-Oriented Blueprint
    
- **Core Principle:** Latent Space Sampling — การดึงข้อมูลจากโมเดลความน่าจะเป็นมาสร้างเป็นผลลัพธ์ใหม่
    

### [[10. Exploratory Intent]] (ต้องการสำรวจความเป็นไปได้)

- **Context:** ไม่มีจุดหมายชัดเจน ค้นหาแบบกระจัดกระจายเพื่อสร้าง Boundary ของความรู้
    
- **Key Takeaways:** ระบบต้องนำเสนอ Semantic Recommendation หรือ [[Vector Proximity]] Topics
    
- **Core Principle:** Serendipity & Associative Memory — การเชื่อมโยงโหนดความรู้ที่อยู่ใกล้เคียงในสมอง
    

## 3. High-Friction & Behavioral Intents

### [[11. Validation-Seeking Intent]] (ต้องการแรงสนับสนุนทางอารมณ์/ตรรกะ)

- **Context:** ผู้ใช้รู้คำตอบอยู่แล้ว แต่ต้องการ Confirmation Bias หรือหลักฐานทางสถิติมาซัพพอร์ต
    
- **Key Takeaways:** ข้อมูลเชิงประจักษ์, Case Studies, Social Proof
    
- **Core Principle:** Cognitive Dissonance Reduction — การลดความขัดแย้งในใจเมื่อต้องตัดสินใจเสี่ยง
    

### [[12. Troubleshooting Intent]] (ต้องการแก้ปัญหาเฉพาะหน้า)

- **Context:** ระบบล่มหรือเกิดปัญหาคอขวดที่ต้องแก้ทันที (High Urgency)
    
- **Key Takeaways:** Step-by-Step Recovery Guide, Quick-fix Commands
    
- **Core Principle:** Mean Time to Repair (MTTR) Minimization
    

### [[13. Architectural Design Intent]] (ต้องการวางโครงสร้างระยะยาว)

- **Context:** กำลังเริ่มต้นโปรเจกต์ใหญ่ ต้องการพิมพ์เขียวที่ขยายระบบได้ (Scalability)
    
- **Key Takeaways:** [[Design Patterns]], System Topologies, Component Dependency Maps
    
- **Core Principle:** Future-Proofing & Decoupling
    

### [[14. Compliance Intent]] (ต้องการความถูกต้องตามกฎเกณฑ์)

- **Context:** ต้องการตรวจสอบว่าสิ่งที่ทำขัดต่อกฎหมาย มาตรฐาน (ISO, GDPR) หรือ Security Policy หรือไม่
    
- **Key Takeaways:** Checklists, Audit Logs Requirement, Policy Constraints
    
- **Core Principle:** Boundary Condition Enforcement — การทำงานอยู่ภายในกรอบที่ปลอดภัย
    

### [[15. Legacy Migration Intent]] (ต้องการเปลี่ยนผ่านระบบ)

- **Context:** มีระบบเก่า (Legacy) ต้องการย้ายไประบบใหม่โดยไม่ให้เกิด Data Loss หรือ Downtime
    
- **Key Takeaways:** Data Mapping, Interoperability Layer, [[BFF Pattern (Backend For Frontend)]]
    
- **Core Principle:** Backward Compatibility & Risk Isolation
    

## 4. Advanced Interaction & Edge Intents

### [[16. Refinement Intent]] (ต้องการขัดเกลาสิ่งที่มีอยู่)

- **Context:** ผลลัพธ์แรกดีแล้ว แต่ต้องการเพิ่มความสมบูรณ์แบบ (Polishing)
    
- **Key Takeaways:** Iterative Prompts, Fine-Tuning Parameters, Micro-adjustments
    
- **Core Principle:** Gradient Descent Optimization — การค่อยๆ ปรับลด Error เข้าใกล้จุดที่สมบูรณ์ที่สุด
    

### [[17. Counterfactual Intent]] (ต้องการจำลองสถานการณ์สมมติ)

- **Context:** การตั้งคำถามประเภท "What-if" เพื่อทดสอบ Stress Test ของระบบหรือแนวคิด
    
- **Key Takeaways:** Scenario Simulation, Chaos Engineering Principles, Parameter Variation
    
- **Core Principle:** Boundary Testing — การผลักดันระบบไปสู่จุด Edge Case เพื่อดูพฤติกรรม
    

### [[18. Interoperability Intent]] (ต้องการเชื่อมต่อระบบเข้าด้วยกัน)

- **Context:** ผู้ใช้ต้องการให้ระบบ A คุยกับระบบ B ได้อย่างไร้รอยต่อ
    
- **Key Takeaways:** [[API Gateways]], Webhooks, Data Serialization Formats (JSON/Protobuf)
    
- **Core Principle:** Protocol Consensus — การสร้างภาษากลางเพื่อให้ระบบต่างค่ายทำงานร่วมกันได้
    

### [[19. Cost-Optimization Intent]] (ต้องการลดค่าใช้จ่ายสูงสุด)

- **Context:** ระบบทำงานได้ดี แต่งบประมาณเกินกำหนด (Financial Friction)
    
- **Key Takeaways:** Resource Allocation, Serverless Architectures, Cost-Benefit Matrices
    
- **Core Principle:** Resource Efficiency Maximization
    

### [[20. Abstract-to-Concrete Intent]] (ต้องการเปลี่ยนนามธรรมเป็นรูปธรรม)

- **Context:** มีไอเดียในหัว (Concept) แต่เขียนเป็นโค้ดหรือระบบไม่ถูก
    
- **Key Takeaways:** Pseudo-code, Implementation Roadmaps, [[Boilerplate Code]]
    
- **Core Principle:** Compilation — การแปลงภาษาระดับสูงของมนุษย์ให้เป็น Low-level Execution
    

## 5. Security, Data, & Lifecycle Intents

### [[21. Security Hardening Intent]] (ต้องการปิดช่องโหว่)

- **Context:** ระบบเสี่ยงต่อการถูกโจมตี ต้องการเพิ่มเกราะป้องกัน (Cybersecurity)
    
- **Key Takeaways:** Threat Modeling, Cryptography Standards, IAM Policies
    
- **Core Principle:** Zero Trust Architecture
    

### [[22. Data Rehydration Intent]] (ต้องการกู้คืนโครงสร้างข้อมูล)

- **Context:** มีข้อมูลดิบที่กระจัดกระจาย หรือต้องการดึงข้อมูลเก่าจาก Cold Storage มาใช้งานใหม่
    
- **Key Takeaways:** ETL Pipelines, [[Schema Infiltration]], Indexing Strategies
    
- **Core Principle:** State Recovery
    

### [[23. Reverse Engineering Intent]] (ต้องการถอดรหัสหาระบบคิด)

- **Context:** เห็นผลลัพธ์ปลายทาง แต่ต้องการแกะรอยกลับไปหา Source Code หรือวิธีคิดต้นฉบับ
    
- **Key Takeaways:** Decompilation Logic, Pattern Recognition, Black-box Testing
    
- **Core Principle:** Inverse Function Mapping
    

### [[24. Performance Benchmarking Intent]] (ต้องการวัดมูลค่าเชิงตัวเลข)

- **Context:** ต้องการตัวเลขที่พิสูจน์ได้ทางวิทยาศาสตร์เพื่อเอาไปเสนอบอร์ดหรือทีมบริหาร
    
- **Key Takeaways:** Telemetry Data, Throughput/IOPS Metrics, Statistical Variance
    
- **Core Principle:** Empirical Quantification
    

### [[25. Dependency Resolution Intent]] (ต้องการแก้ปัญหาความขัดแย้งของระบบ)

- **Context:** เกิดปัญหา Package Conflict หรือแนวคิดสองอย่างขัดแย้งกันเองจนระบบเดินต่อไม่ได้
    
- **Key Takeaways:** Directed Acyclic Graph (DAG) Analysis, Version Locking, Mediation Logic
    
- **Core Principle:** Topological Sorting
    

## 6. Strategic & Epistemic Intents

### [[26. Paradigm Shift Intent]] (ต้องการเปลี่ยนวิธีคิดระบบ)

- **Context:** โครงสร้างเดิมมาถึงทางตัน (Monolith) ต้องการเปลี่ยนสถาปัตยกรรมใหม่ทั้งหมด (Microservices)
    
- **Key Takeaways:** Strangulation Pattern, Domain-Driven Design (DDD)
    
- **Core Principle:** First-Principles Refactoring
    

### [[27. Conceptual Sandboxing Intent]] (ต้องการพื้นที่ทดลองที่ปลอดภัย)

- **Context:** ต้องการทดสอบไอเดียแผลงๆ โดยไม่ให้กระทบกับระบบ Production หรือ State หลัก
    
- **Key Takeaways:** Virtualization, Containerization (Docker), Mock Environments
    
- **Core Principle:** Blast Radius Isolation
    

### [[28. Taxonomy Construction Intent]] (ต้องการจัดหมวดหมู่ระบบ)

- **Context:** ข้อมูลหรือระบบมีความไร้ระเบียบ (Entropy สูง) ต้องการสร้าง Tag, Category หรือ Hierarchy
    
- **Key Takeaways:** Ontology Design, Metadata Schemas, Hierarchical Trees
    
- **Core Principle:** Categorical Imperative — มนุษย์จัดการความซับซ้อนด้วยการแบ่งกลุ่ม
    

### [[29. Telemetry & Observability Intent]] (ต้องการตาสับปะรดมองเห็นระบบ)

- **Context:** ระบบซับซ้อนเกินกว่าจะเดาอาการได้ ต้องการวางระบบ Monitoring ลึกถึงกระดูก
    
- **Key Takeaways:** Distributed Tracing, Metrics/Logs/Traces (Melt Framework), Grafana Dashboards
    
- **Core Principle:** Internal State Inference from Outputs
    

### [[30. End-of-Life (EOL) Intent]] (ต้องการทำลายหรือปลดระวาง)

- **Context:** ต้องการลบข้อมูล ปิดระบบ หรือยกเลิกโปรเจกต์อย่างปลอดภัย ไม่ให้เหลือเศษซากข้อมูลหลุดร่วง
    
- **Key Takeaways:** Data Shredding, Graceful Shutdown Protocols, Resource Deallocation
    
- **Core Principle:** Entropic Cleanliness — การคืน Resource กลับสู่ระบบส่วนกลางอย่างสมบูรณ์
    

## Implementation Template for NLU Systems

เมื่อสถาปนิกต้องการนำ 30 Intents นี้ไปใช้ในระบบ [[Intent Classifier]] สามารถใช้ JSON Schema นี้เป็นพิมพ์เขียวในการทำ Named Entity Recognition (NER) และ Intent Mapping:

JSON

```
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "IntentClassificationPayload",
  "type": "object",
  "properties": {
    "utterance": { "type": "string" },
    "predicted_intent": { 
      "type": "string", 
      "enum": ["exploratory", "diagnostic", "optimization", "counterfactual", "paradigm_shift"] 
    },
    "confidence_score": { "type": "number", "minimum": 0.0, "maximum": 1.0 },
    "context_vector": {
      "type": "array",
      "items": { "type": "number" },
      "minItems": 1536
    },
    "extracted_entities": {
      "type": "object",
      "properties": {
        "domain": { "type": "string" },
        "urgency_level": { "type": "string", "enum": ["low", "medium", "high", "critical"] }
      }
    }
  },
  "required": ["utterance", "predicted_intent", "confidence_score"]
}
```