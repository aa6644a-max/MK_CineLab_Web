import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

# 신형 클라이언트 객체 생성
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

print("--- 사용 가능한 모델 목록 ---")
# 신형 라이브러리의 모델 목록 조회 방식
for m in client.models.list():
    # 텍스트 생성(generateContent)을 지원하는지 확인
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)