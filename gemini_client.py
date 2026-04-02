import os
import re
from google import genai
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

class GeminiClient:
    def __init__(self):
        # API 키 로드 로직 (기존 유지)
        if "GOOGLE_API_KEY" in st.secrets:
            raw_key = st.secrets["GOOGLE_API_KEY"]
        else:
            raw_key = os.getenv("GOOGLE_API_KEY", "")

        api_key = re.sub(r'[^a-zA-Z0-9_-]', '', str(raw_key))
        
        if not api_key:
             raise ValueError("GOOGLE_API_KEY가 없습니다. 설정을 확인하세요.")

        # 클라이언트 생성
        self.client = genai.Client(api_key=api_key)
        
        # 💡 수정 포인트: 'models/' 접두사를 명시하여 경로를 확실히 지정합니다.
        self.model_name = 'models/gemini-1.5-flash' 

    def generate_post(self, prompt):
        try:
            # 콘텐츠 생성 호출
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            
            if response.text:
                return response.text
            else:
                return "에러: 제미나이가 유효한 응답을 생성하지 못했습니다."
        except Exception as e:
            return f"제미나이 API 에러 발생: {str(e)} (사용 모델: {self.model_name})"