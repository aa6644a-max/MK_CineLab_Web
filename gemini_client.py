import os
import google.generativeai as genai
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class GeminiClient:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
             raise ValueError("GOOGLE_API_KEY를 .env 파일에서 찾을 수 없습니다.")

        genai.configure(api_key=api_key)
        
        # 2026년 기준, MK님의 계정에서 가장 안정적으로 작동하는 최신 모델입니다.
        # 'gemini-2.0'의 404 문제를 해결하기 위해 '2.5-flash'로 경로를 지정합니다.
        self.model_name = 'models/gemini-2.5-flash' 
        self.model = genai.GenerativeModel(self.model_name)

    def generate_post(self, prompt):
        try:
            # MK CINELAB의 분석적인 톤앤매너를 유지하며 글쓰기를 수행합니다.
            response = self.model.generate_content(prompt)
            
            if response.text:
                return response.text
            else:
                return "에러: 제미나이가 유효한 응답을 생성하지 못했습니다."
                
        except Exception as e:
            # 상세 에러 메시지를 반환하여 실시간 대응이 가능하게 합니다.
            return f"제미나이 API 에러 발생: {str(e)}"