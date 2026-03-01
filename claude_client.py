# claude_client.py
import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

class ClaudeClient:
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        # 'latest' 대신 구체적인 모델 버전을 명시하여 404 에러를 방지합니다.
        # 대부분의 티어에서 즉시 사용 가능한 하이쿠 모델입니다. [cite: 99, 117]
        self.model = "claude-3-haiku-20240307" 

    def generate_post(self, prompt):
        try:
            # max_tokens는 가이드대로 4000으로 설정합니다. [cite: 108]
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000, 
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            return f"에러 발생: {str(e)}"