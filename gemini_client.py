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
        # 1. 웹 금고(secrets) 확인 후 없으면 로컬(.env) 확인
        if "GOOGLE_API_KEY" in st.secrets:
            raw_key = st.secrets["GOOGLE_API_KEY"]
        else:
            raw_key = os.getenv("GOOGLE_API_KEY", "")

        api_key = re.sub(r'[^a-zA-Z0-9_-]', '', str(raw_key))
        
        if not api_key:
             raise ValueError("GOOGLE_API_KEY가 없습니다. 설정을 확인하세요.")

        self.client = genai.Client(api_key=api_key)
        
        # 💡 모델을 Gemini 3.1 Flash-Lite로 변경했습니다.
        # 이 모델은 503 에러에 더 강하며 가성비가 뛰어납니다.
        self.model_name = 'gemini-3.1-flash-lite' 

    def generate_post(self, prompt, images=None, max_retries=3):
        """
        포스팅을 생성합니다. 503 에러 발생 시 최대 max_retries만큼 재시도합니다.
        """
        contents = []
        
        # 1. 프롬프트 텍스트 추가
        if prompt:
            contents.append(prompt)
        
        # 2. 이미지 파일 처리
        if images:
            for img_file in images:
                try:
                    img = Image.open(img_file)
                    contents.append(img)
                except Exception as img_err:
                    print(f"이미지 로드 에러: {img_err}")

        # 페이로드 설정
        payload = contents if len(contents) > 1 else prompt

        # 🔄 재시도 로직 시작
        for attempt in range(max_retries):
            try:
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
                
                # 503 서버 과부하 에러 감지 시 재시도
                if any(err in error_msg for err in ["503", "UNAVAILABLE", "high demand"]):
                    if attempt < max_retries - 1:
                        # 재시도 횟수가 늘어날수록 대기 시간을 조금씩 늘리면 더 효과적입니다.
                        wait_time = (attempt + 1) * 5 
                        print(f"서버 혼잡(503). {wait_time}초 후 {attempt + 2}번째 재시도...")
                        time.sleep(wait_time)
                        continue
                
                # 최종 실패 시 에러 메시지 반환
                return f"제미나이 API 에러 발생: {error_msg}"