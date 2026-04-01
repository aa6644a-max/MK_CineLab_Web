import os
import re
import google.generativeai as genai
import streamlit as st  # 💡 파일 맨 꼭대기에 추가합니다!
from dotenv import load_dotenv

load_dotenv()

class GeminiClient:
    def __init__(self):
        # 💡 정지당한 옛날 키는 지우고, Streamlit 금고(secrets)에서 새 키를 꺼내옵니다!
        raw_key = st.secrets.get("GOOGLE_API_KEY", "")
        api_key = re.sub(r'[^a-zA-Z0-9_-]', '', str(raw_key))
        
        if not api_key:
             raise ValueError("GOOGLE_API_KEY가 없습니다. Streamlit Secrets 설정을 확인하세요.")

        genai.configure(api_key=api_key)
        self.model_name = 'models/gemini-2.5-flash' 
        self.model = genai.GenerativeModel(self.model_name)

    def generate_post(self, prompt):
        try:
            response = self.model.generate_content(prompt)
            if response.text:
                return response.text
            else:
                return "에러: 제미나이가 유효한 응답을 생성하지 못했습니다."
        except Exception as e:
            return f"제미나이 API 에러 발생: {str(e)}"