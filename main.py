import os
import shutil
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel

class HomeworkResult(BaseModel):
    student_name: str
    score: float
    max_score: float

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("Environment variable GOOGLE_API_KEY not found!")

client = genai.Client(api_key=api_key)

target_dir = Path("Submitted_file")

if not target_dir.exists():
    raise FileNotFoundError(f"Folder {target_dir} not found!")

test_limit = 3
processed_count = 0

for student in target_dir.iterdir():
    if processed_count >= test_limit:
        print(f"\nProcessed limit of {test_limit} students reached. Stopping.")
        break

    if student.is_dir():
        for hw in student.iterdir():
            if processed_count >= test_limit:
                break

            if hw.is_dir() and hw.name == "HW 4":
                version_folders = [v for v in hw.iterdir() if v.is_dir()]

                if version_folders:
                    version_folders = sorted(version_folders)
                    latest_version_path = version_folders[-1]

                    pdf_files = [
                        f for f in latest_version_path.iterdir()
                        if f.is_file() and f.suffix.lower() == ".pdf"
                    ]

                    if pdf_files:
                        target_pdf = pdf_files[0]
                        print(f"\nGrading homework for: {student.name}")
                        print(f"Original file: {target_pdf.name}")

                        temp_pdf_path = "temp_upload.pdf"
                        shutil.copy(target_pdf, temp_pdf_path)

                        try:
                            uploaded_file = client.files.upload(file=temp_pdf_path)
                            
                            rubric_prompt = """
                            You are a Teaching Assistant (TA). Grade the attached homework PDF file.
                            Extract the student's name from the document and evaluate their answers to calculate the total score out of 60.
                            Provide the output strictly matching the requested JSON schema.
                            """
                            
                            response = client.models.generate_content(
                                model='gemini-2.5-flash',
                                contents=[rubric_prompt, uploaded_file],
                                config=types.GenerateContentConfig(
                                    response_mime_type="application/json",
                                    response_schema=HomeworkResult,
                                ),
                            )
                            
                            print(f"--- Grading Result ---")
                            print(response.text)
                            
                            client.files.delete(name=uploaded_file.name)
                            
                        except Exception as e:
                            print(f"Error processing {student.name}: {e}")
                            
                        finally:
                            if os.path.exists(temp_pdf_path):
                                os.remove(temp_pdf_path)
                                
                        processed_count += 1

                    else:
                        print(f"\nStudent {student.name} did not submit a PDF file in {latest_version_path.name}")