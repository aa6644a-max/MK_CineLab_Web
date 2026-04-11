import os
import re
import time
from google import genai 
import streamlit as st
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

class GeminiClient:
    def __init__(self):
        # 1. API 키 불러오기
        if "GOOGLE_API_KEY" in st.secrets:
            raw_key = st.secrets["GOOGLE_API_KEY"]
        else:
            raw_key = os.getenv("GOOGLE_API_KEY", "")

        api_key = re.sub(r'[^a-zA-Z0-9_-]', '', str(raw_key))
        
        if not api_key:
             raise ValueError("GOOGLE_API_KEY가 없습니다. 설정을 확인하세요.")

        self.client = genai.Client(api_key=api_key)
        
        # 💡 모델명을 3.1 Flash-Lite로 변경했습니다.
        # 503 에러에 강하고 비용이 매우 저렴한 모델입니다.
        self.model_name = 'gemini-3.1-flash-lite-preview'

    def generate_post(self, prompt, images=None, max_retries=3):
        contents = []
        if prompt:
            contents.append(prompt)
        if images:
            for img_file in images:
                try:
                    img = Image.open(img_file)
                    contents.append(img)
                except Exception as img_err:
                    print(f"이미지 로드 에러: {img_err}")

        payload = contents if len(contents) > 1 else prompt

        for attempt in range(max_retries):
            try:
                # API 호출
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=payload
                )
                
                if response.text:
                    return response.text
                else:
                    return "에러: 제미나이가 유효한 응답을 생성하지 못했습니다."
                    
            except Exception as e:
                error_msg = str(e)
                # 503 과부하 에러(UNAVAILABLE) 감지 시 점진적 재시도
                if any(err in error_msg for err in ["503", "UNAVAILABLE", "high demand"]):
                    if attempt < max_retries - 1:
                        # 재시도 횟수에 따라 대기 시간을 5초, 10초로 늘립니다.
                        wait_time = (attempt + 1) * 5
                        print(f"서버 혼잡. {wait_time}초 후 {attempt + 2}번째 재시도...")
                        time.sleep(wait_time)
                        continue
                
                return f"제미나이 API 에러 발생: {error_msg}"