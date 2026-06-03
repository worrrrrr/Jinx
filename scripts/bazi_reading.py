"""BaZi deep interpretation for 8/8/1992 16:49"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import datetime
from tools.bazi import BaZi, TIAN_GAN_ELEMENT, DI_ZHI_MAIN_ELEMENT, HIDDEN_STEMS, MONTH_TO_SEASON

dt = datetime.datetime(1992, 8, 8, 16, 49)
b = BaZi(dt)

el = {'火':'ไฟ', '水':'น้ำ', '木':'ไม้', '金':'โลหะ', '土':'ดิน'}
dm = b.day_master
dm_el = TIAN_GAN_ELEMENT.get(dm)
strength = b.element_strength

print('=== ระดับธาตุ (5 Levels of Element Strength) ===\n')
ranking = sorted(strength.items(), key=lambda x: -x[1])
for e, v in ranking:
    name = el[e]
    if v == 0:
        bar = '▱'
        label = f'❌ ขาด (0) — ไม่มีธาตุนี้เลย'
    elif v <= 1.0:
        bar = '▰▱▱▱'
        label = f'อ่อน ({v:.1f}) — มีเล็กน้อย'
    elif v <= 2.0:
        bar = '▰▰▱▱'
        label = f'ปานกลาง ({v:.1f}) — พอใช้'
    elif v <= 3.0:
        bar = '▰▰▰▱'
        label = f'ค่อนข้างแรง ({v:.1f})'
    else:
        bar = '▰▰▰▰'
        label = f'แรงมาก ({v:.1f}) — เด่น'
    print(f'  {name:4s}: {bar}  {label}')

print()

print('=== ความหมายธาตุเทียบกับ DM ' + dm + '(' + el[dm_el] + ') ===\n')

fire_water = {'fire_elements': ['木', '火'], 'water': ['水', '金', '土']}
fire_total = sum(strength[e] for e in fire_water['fire_elements'])
water_total = sum(strength[e] for e in fire_water['water'])

print(f'ธาตุที่ช่วยไฟ (木印 + 火ตัวเอง) = {fire_total:.1f}')
print(f'ธาตุที่ระบาย/ต้านไฟ (水官殺 + 金財 + 土食傷) = {water_total:.1f}')
print()

if fire_total >= water_total:
    print('🔋 Body Strong — 身强')
    print('  ไฟมีกำลังพอ ลุยได้ทุกอย่าง')
else:
    print('🔋 Body Weak — 身弱')
    print('  ไฟอ่อน เมื่อเทียบกับธาตุอื่น')

print()

# === รายละเอียดแต่ละธาตุ ===
print('--- แต่ละธาตุมีผลต่อชีวิตคุณยังไง ---\n')

# 金 (Metal) — Wealth
print(f'⚔️ โลหะ ({strength["金"]:.1f}) = 財 (Wealth)')
print(f'  ไฟถลุงโลหะ = คุณหาทรัพย์')
if strength['金'] >= 3.0:
    print(f'  โลหะ 3.5 = ดวงทรัพย์ดีมาก')
    print(f'  แต่ ไฟ(คุณ) 2.0 — manage โลหะ 3.5 ต้องออกแรงเยอะ')
    print(f'  เปรียบเหมือนมีทองกองอยู่ แต่ต้องแบกกลับบ้าน')
    print(f'  → หาเงินได้ แต่เหนื่อย ต้องบริหารดีๆ')
    print(f'  ถ้า Body Weak ยิ่งต้องระวัง 財มากไป = 负债 แทน')
elif strength['金'] >= 2.0:
    print(f'  การเงิน稳 มีรายได้ประจำ')
else:
    print(f'  ทรัพย์น้อย ต้องสะสม')

print()

# 火 (Fire) — Self
print(f'🔥 ไฟ ({strength["火"]:.1f}) = 比劫 (ตัวคุณ)')
print(f'  ตัวคุณธาตุไฟ — เป็นคนกระตือรือร้น')
if strength['火'] >= 3.0:
    print(f'  ไฟแรง = 身强, มีพลัง, ชอบเป็นผู้นำ')
elif strength['火'] >= 1.5:
    print(f'  ไฟปานกลาง = ปกติ 稳')
else:
    print(f'  ไฟอ่อน = อ่อนแอ ไม่มั่นคง')

print()

# 土 (Earth) — Output
print(f'🟤 ดิน ({strength["土"]:.1f}) = 食傷 (Output/Talent)')
print(f'  ไฟเผาดิน = ผลงาน ความสามารถ')
if strength['土'] >= 2.0:
    print(f'  ดิน 2.0 = มีความสามารถ มีผลงาน')
    print(f'  食神เด่น — มีพรสวรรค์ ศิลปะ การพูด')
else:
    print(f'  อ่อน — ความสามารถถูกจำกัด')

print()

# 水 (Water) — Authority
print(f'💧 น้ำ ({strength["水"]:.1f}) = 官殺 (Authority/Challenge)')
print(f'  น้ำดับไฟ = อุปสรรค กดดัน')
if strength['水'] <= 1.0:
    print(f'  น้ำ 1.0 = มีอุปสรรคบ้าง ไม่หนักหนา')
    print(f'  ชีวิตไม่เจอเรื่องกดดันมาก')
elif strength['水'] >= 2.5:
    print(f'  น้ำแรง = เจออุปสรรค頻繁 กดดันสูง')
print()

# 木 (Wood) — Resource
print(f'🌳 ไม้ ({strength["木"]:.1f}) = 印 (Support/Knowledge)')
print(f'  ไม้ช่วยไฟ = ปัญญา การศึกษา ผู้ใหญ่')
if strength['木'] == 0:
    print(f'  ❌ ขาดไม้ = ไม่มี印')
    print(f'  ส่งผล:')
    print(f'    • การศึกษาอาจไม่สะดวก ต้องพยายามเอง')
    print(f'    • ขาดผู้ใหญ่คอยสนับสนุน')
    print(f'    • ต้องพึ่งตัวเองสูง เก่งด้วยตัวเอง')
    print(f'  แนวทางแก้: หาความรู้เพิ่ม หาที่ปรึกษา')
    print(f'    ใส่สีเขียว ปลูกต้นไม้ อยู่ใกล้ธรรมชาติ')
elif strength['木'] < 1.0:
    print(f'  มีน้อย — ต้องพึ่งตัวเอง')
else:
    print(f'  ดี — มีผู้支持')

print()

print('=== สรุปดวงชะตา ===')
print(f'─────────────────────')
print(f'คุณเกิดวันที่ 8 สิงหาคม 2535 เวลา 16:49 น.')
print(f'')
print(f'📌 ปีนักษัตร: ลิง | สามเกลอ: ลิง-หนู | หกเกลอ: มังกร | ทะลวง: หมา')
print(f'📌 Day Master: {dm} ({el[dm_el]}) — คุณคือคนธาตุไฟ')
print(f'')
print(f'📊 จุดเด่น:')
print(f'  ✅ ดวงทรัพย์ดี (โลหะ 3.5) — มีแววการลงทุน การเงิน')
print(f'  ✅ มี食神 (ดิน 2.0) — มีพรสวรรค์ ศิลปะ/การพูด')
print(f'  ✅ มี比肩ซ้อนวัน-เวลา — บั้นปลายมีคนช่วย')
print(f'')
print(f'⚠️ จุดอ่อน:')
print(f'  ❌ ขาด印 (ไม้) — ไม่มีที่พึ่ง ต้องสู้เอง')
print(f'  ⚠️ 身弱 (ไฟอ่อนกว่าโลหะ) — ต้องระวังเรื่อง管理ทรัพย์')
print(f'')
print(f'💡 แนวทางเสริม:')
print(f'  • เติม木 (ไม้) — เรียนหนังสือ หาที่ปรึกษา ใส่สีเขียว')
print(f'  • ใช้食神 (ดิน) — ทำงานที่ใช้ความสามารถเฉพาะตัว')
print(f'  • หกเกลอมังกร — คบคนปีมังกรจะเข้ากันได้ดี')
