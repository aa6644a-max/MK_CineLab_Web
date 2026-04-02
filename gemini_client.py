import os
import re
from google import genai # 최신 라이브러리로 변경
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

class GeminiClient:
    def __init__(self):
        # 1. 웹 금고(secrets) 확인 후 없으면 로컬(.env) 확인
        if "GOOGLE_API_KEY" in st.secrets:
            raw_key = st.secrets["GOOGLE_API_KEY"]
        else:
            raw_key = os.getenv("GOOGLE_API_KEY", "")

        # API 키에서 불필요한 공백이나 특수문자 제거
        api_key = re.sub(r'[^a-zA-Z0-9_-]', '', str(raw_key))
        
        if not api_key:
             raise ValueError("GOOGLE_API_KEY가 없습니다. 설정을 확인하세요.")

        # 2026년 기준 최신 구글 genai 클라이언트 생성 방식 적용
        self.client = genai.Client(api_key=api_key)
        # 현재 안정적으로 지원되는 최신 모델명으로 설정
        self.model_name = 'gemini-2.0-flash' 

    def generate_post(self, prompt):
        try:
            # 최신 SDK의 콘텐츠 생성 메서드 호출 방식 적용
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            
            if response.text:
                return response.text
            else:
                return "에러: 제미나이가 유효한 응답을 생성하지 못했습니다."
        except Exception as e:
            return f"제미나이 API 에러 발생: {str(e)}"