import os
import re
from google import genai  # 라이브러리 임포트 방식 변경
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

        api_key = re.sub(r'[^a-zA-Z0-9_-]', '', str(raw_key))
        
        if not api_key:
             raise ValueError("GOOGLE_API_KEY가 없습니다. 설정을 확인하세요.")

        # [변경포인트 1] 새로운 Client 객체 생성 방식 적용
        self.client = genai.Client(api_key=api_key)
        # [변경포인트 2] 신규 라이브러리에서는 모델명에서 'models/'를 떼는 것이 표준입니다.
        self.model_name = 'gemini-2.5-flash' 

    def generate_post(self, prompt):
        try:
            # [변경포인트 3] 메서드 호출 구조가 client.models.generate_content로 변경됨
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            if response.text:
                return response.text
            else:
                return "에러: 제미나이가 유효한 응답을 생성하지 못했습니다."
        except Exception as e:
            # 에러 메시지가 구체적으로 나오도록 유지합니다.
            return f"제미나이 API 에러 발생: {str(e)}"