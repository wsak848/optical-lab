# Optical Communication Laboratory

ห้องทดลองจำลองการสื่อสารทางแสงสำหรับการเรียนรู้ด้วย Streamlit

## Lab 1: ความถี่และความยาวคลื่นของแสง

ปรับความยาวคลื่นตั้งแต่ 400 ถึง 1700 nm เพื่อดูความถี่ที่คำนวณจาก `f = c / λ` และการเปลี่ยนระยะห่างของคลื่นในภาพจำลอง ค่าความเร็วแสงที่ใช้คือ `3.0 × 10^8 m/s` เริ่มต้นที่ 1310 nm และมีปุ่มเลือก 850, 1310 และ 1550 nm

ความยาวคลื่นอ้างอิงสุญญากาศ เมื่อแสงเข้าสู่ใยแก้ว ความเร็วและความยาวคลื่นเปลี่ยนตามดัชนีหักเห แต่ความถี่คงเดิม ภาพคลื่นเป็นภาพนิ่งเชิงแนวคิด: แนวนอนคือระยะทางสัมพัทธ์ แนวตั้งคือแอมพลิจูดมาตรฐาน ไม่ใช่กำลังแสงหรือระยะทางการแพร่จริง และสีเส้นไม่ใช่สีแสง

ผู้สอน: Sakda Wongadyarin

## เริ่มใช้งาน

แนะนำ Python 3.13 (ทดสอบด้วย Python 3.13.2) และ virtual environment แยกสำหรับโครงการ
คำสั่งสำหรับ Windows PowerShell โดยเรียก Python ใน environment โดยตรง ไม่จำเป็นต้อง activate:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

เปิด URL ที่ Streamlit แสดงใน terminal (โดยทั่วไปคือ http://localhost:8501) กด Ctrl+C เพื่อหยุด
Dependencies หลักมีเพียง Streamlit, NumPy และ Matplotlib โดยกำหนดช่วงเวอร์ชันที่เข้ากันได้ใน `requirements.txt`

## ทดสอบ

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```
