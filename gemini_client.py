import os
import re
import time  # 💡 대기 시간을 위해 time 모듈 추가
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
        # gemini-2.5-flash는 멀티모달(텍스트+이미지) 분석을 완벽하게 지원합니다.
        self.model_name = 'gemini-2.5-flash' 

    # 💡 max_retries=3 파라미터를 추가하여 최대 3번까지 재시도하도록 설정
    def generate_post(self, prompt, images=None, max_retries=3):
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

        # 💡 에러 발생 시 자동으로 다시 시도하는 반복문 추가
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
                
                # 에러 메시지에 503이나 UNAVAILABLE이 포함되어 있으면 (서버 과부하)
                if "503" in error_msg or "UNAVAILABLE" in error_msg or "high demand" in error_msg.lower():
                    if attempt < max_retries - 1: # 마지막 시도가 아니라면 대기 후 재시도
                        print(f"서버 과부하 발생(503). 5초 후 {attempt + 2}번째 재시도를 합니다...")
                        time.sleep(5)  # 5초 동안 대기
                        continue # 반복문의 처음으로 돌아가서 다시 요청
                
                # 503 에러가 아니거나, 3번 다 실패했다면 에러 메시지 반환
                return f"제미나이 API 에러 발생: {error_msg}"