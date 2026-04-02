import os
import re
from google import genai
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

class GeminiClient:
    def __init__(self):
        # 1. API 키 로드 (기본 로직 유지)
        if "GOOGLE_API_KEY" in st.secrets:
            raw_key = st.secrets["GOOGLE_API_KEY"]
        else:
            raw_key = os.getenv("GOOGLE_API_KEY", "")

        api_key = re.sub(r'[^a-zA-Z0-9_-]', '', str(raw_key))
        
        if not api_key:
             raise ValueError("GOOGLE_API_KEY가 없습니다. 설정을 확인하세요.")

        # 2. 클라이언트 생성
        self.client = genai.Client(api_key=api_key)
        
        # 💡 원상 복구 및 안정화 모델 설정
        # 만약 2.5 flash 명칭이 필요하다면 아래 이름을 유지하고, 
        # 일반적인 최신 무료 모델은 'gemini-2.0-flash'를 사용합니다.
        self.model_name = 'gemini-2.0-flash' 

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
            # 에러 발생 시 원인 파악을 위해 상세 메시지 출력
            return f"제미나이 API 에러 발생: {str(e)}"