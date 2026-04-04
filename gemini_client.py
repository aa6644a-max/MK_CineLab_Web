import os
import re
from google import genai 
import streamlit as st
from dotenv import load_dotenv
from PIL import Image # 💡 이미지 처리를 위해 추가

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
        # gemini-2.5-flash는 멀티모달(텍스트+이미지) 분석을 완벽하게 지원합니다.
        self.model_name = 'gemini-2.5-flash' 

    # 💡 images 파라미터를 추가하여 사진 리스트를 받을 수 있게 변경했습니다.
    def generate_post(self, prompt, images=None):
        try:
            # 전달할 contents 리스트를 만듭니다. (텍스트 + 이미지 조합용)
            contents = []
            
            # 1. 프롬프트 텍스트 추가
            if prompt:
                contents.append(prompt)
            
            # 2. 이미지 파일들이 있다면 PIL Image 객체로 변환하여 리스트에 추가
            if images:
                for img_file in images:
                    img = Image.open(img_file)
                    contents.append(img)

            # 리스트에 텍스트만 있으면 텍스트만, 이미지가 섞여있으면 통째로 전송
            payload = contents if len(contents) > 1 else prompt

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=payload
            )
            
            if response.text:
                return response.text
            else:
                return "에러: 제미나이가 유효한 응답을 생성하지 못했습니다."
                
        except Exception as e:
            return f"제미나이 API 에러 발생: {str(e)}"