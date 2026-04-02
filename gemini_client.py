# gemini_client.py 전체를 이 내용으로 덮어쓰세요.
import os
import re
from google import genai
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

class GeminiClient:
    def __init__(self):
        # API 키 로드
        if "GOOGLE_API_KEY" in st.secrets:
            raw_key = st.secrets["GOOGLE_API_KEY"]
        else:
            raw_key = os.getenv("GOOGLE_API_KEY", "")

        api_key = re.sub(r'[^a-zA-Z0-9_-]', '', str(raw_key))
        
        if not api_key:
             raise ValueError("GOOGLE_API_KEY가 없습니다.")

        # 클라이언트 생성
        self.client = genai.Client(api_key=api_key)
        
        # 💡 [핵심 수정] 원래 가장 잘 작동하는 표준 모델명입니다.
        self.model_name = 'gemini-1.5-flash' 

    def generate_post(self, prompt):
        try:
            # 2026년 기준 최신 호출 방식입니다.
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            
            if response and response.text:
                return response.text
            else:
                return "에러: 제미나이가 응답을 생성하지 못했습니다."
        except Exception as e:
            return f"제미나이 API 에러 발생: {str(e)}"