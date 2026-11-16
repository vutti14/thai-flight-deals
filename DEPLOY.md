# วิธีเผยแพร่ thai-flight-deals (GitHub Pages)

เวลาในเอกสารนี้เป็นเวลาไทย (ICT, UTC+7) การ push ทุกครั้งต้องได้อนุมัติจากเจ้าของ (BOSS) ด้วยคำพูดของตัวเองก่อน

## ภาพรวม

- GitHub Pages แบบ legacy เสิร์ฟจาก branch **`gh-pages`** โฟลเดอร์ `/`
- URL: https://vutti14.github.io/thai-flight-deals/
- ตอนนี้ `main` กับ `gh-pages` ชี้ commit เดียวกัน การ push เข้า `main` อย่างเดียว **ไม่ได้** อัปเดตเว็บ

## ก่อนเผยแพร่

1. CI เขียว (syntax ของ JS/Python และเทสต์ข้อมูล `snapshots.js`)
2. รันในเครื่อง:
   ```bash
   node --check snapshots.js
   node --test tests/*.test.mjs
   python3 -m http.server 8000    # เปิดดูทุกหน้าว่าไม่พัง
   ```
3. ไม่มีข้อมูลส่วนตัวหรือคีย์ใน diff
4. BOSS อนุมัติแล้ว

## เผยแพร่

```bash
git checkout main && git pull
git push origin main:gh-pages      # ให้ gh-pages ตามทัน main (fast-forward)
```

รอ 1–2 นาที ดูสถานะที่แท็บ Actions ("pages build and deployment") แล้วเปิด URL เช็กว่าวันที่ค้นหาล่าสุดตรง

## Rollback

```bash
git revert <sha>                   # บน main สร้าง commit ย้อนกลับ
git push origin main
git push origin main:gh-pages
```

ห้ามใช้ `--force` กับ `main` หรือ `gh-pages` ถ้าจำเป็นต้องย้อนด่วนจริง ๆ ให้เจ้าของตัดสินใจเอง
