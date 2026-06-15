import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

target_dir = Path("Submitted_file")

if not target_dir.exists():
    raise FileNotFoundError(f"folder {target_dir} not found")

test_limit = 2
processed_count = 0

for student in target_dir.iterdir():
    if processed_count >= test_limit:
        print(f"\n✅ เทสต์ครบตามกำหนด {test_limit} คนแล้ว หยุดการทำงาน")
        break

    if student.is_dir():
        for hw in student.iterdir():
            if hw.is_dir() and hw.name == "HW 4":
                version_folders = []

                for v in hw.iterdir():
                    if v.is_dir():
                        version_folders.append(v)

                if version_folders:
                    version_folders = sorted(version_folders)
                    latest_version_path = version_folders[-1]

                    pdf_files = [
                        f
                        for f in latest_version_path.iterdir()
                        if f.is_file() and f.suffix.lower() == ".pdf"
                    ]

                    if pdf_files:
                        print(
                            f"\nstudent: {student.name} -> last version: {latest_version_path.name}"
                        )
                        target_pdf = pdf_files[0]
                        print(f"เจอไฟล์ PDF สำหรับตรวจ: {target_pdf.name}")

                        try:
                            uploaded_file = client.files.upload(file=target_pdf)

                            rubric_prompt = """
                            คุณคือผู้ช่วยสอน (TA) จงตรวจเนื้อหาในไฟล์ PDF การบ้านที่แนบมานี้
                            และสรุปผลคะแนนออกมาในรูปแบบข้อความสั้นๆ 
                            พร้อมเหตุผลในภาษาไทยให้ชัดเจน
                            """

                            response = client.models.generate_content(
                                model="gemini-2.5-flash",
                                contents=[rubric_prompt, uploaded_file],
                            )

                            print(f"--- ผลการตรวจของ {student.name} ---")
                            print(response.text)

                            client.files.delete(name=uploaded_file.name)

                            processed_count += 1

                        except Exception as e:
                            print(
                                f"เกิดข้อผิดพลาดระหว่างตรวจงานของ {student.name}: {e}"
                            )

                    else:
                        print(
                            f"⚠️ นักศึกษา {student.name} ไม่ได้ส่งไฟล์ PDF ใน {latest_version_path.name}"
                        )
