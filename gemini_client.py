import os
import re
from google import genai
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

class GeminiClient:
    def __init__(self):
        # 1. API 키 로드 로직 (기존 유지)
        if "GOOGLE_API_KEY" in st.secrets:
            raw_key = st.secrets["GOOGLE_API_KEY"]
        else:
            raw_key = os.getenv("GOOGLE_API_KEY", "")

        api_key = re.sub(r'[^a-zA-Z0-9_-]', '', str(raw_key))
        
        if not api_key:
             raise ValueError("GOOGLE_API_KEY가 없습니다. 설정을 확인하세요.")

        # 2. 클라이언트 생성
        self.client = genai.Client(api_key=api_key)
        
        # 💡 수정 포인트: 404 에러 방지를 위해 가장 안정적인 모델명으로 변경
        # 'gemini-1.5-flash'는 현재 모든 사용자에게 가장 보편적으로 지원되는 모델입니다.
        self.model_name = 'gemini-1.5-flash' 

    def generate_post(self, prompt):
        try:
            # 💡 호출 방식 최신화
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            
            if response.text:
                return response.text
            else:
                return "에러: 제미나이가 유효한 응답을 생성하지 못했습니다."
        except Exception as e:
            # 💡 에러 메시지 강화: 어떤 모델명을 사용했는지 함께 출력하여 원인 파악을 돕습니다.
            return f"제미나이 API 에러 발생: {str(e)} (사용 모델: {self.model_name})"