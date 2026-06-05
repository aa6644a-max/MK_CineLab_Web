import os
import re
import base64
import time
import io
import streamlit as st
from anthropic import Anthropic
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

class ClaudeClient:
    def __init__(self):
        if "ANTHROPIC_API_KEY" in st.secrets:
            raw_key = st.secrets["ANTHROPIC_API_KEY"]
        else:
            raw_key = os.getenv("ANTHROPIC_API_KEY", "")

        api_key = re.sub(r'[^a-zA-Z0-9_-]', '', str(raw_key))

        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY가 없습니다. 설정을 확인하세요.")

        self.client = Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-6"

    def generate_post(self, prompt, images=None, max_retries=3):
        content = []

        if images:
            for img_file in images:
                try:
                    if hasattr(img_file, 'seek'):
                        img_file.seek(0)
                    img_bytes = img_file.read()
                    if hasattr(img_file, 'seek'):
                        img_file.seek(0)

                    # 1024px 이하로 리사이즈 (API 413 방지)
                    try:
                        pil_img = Image.open(io.BytesIO(img_bytes))
                        max_dim = 1024
                        if max(pil_img.size) > max_dim:
                            pil_img.thumbnail((max_dim, max_dim), Image.LANCZOS)
                        buf = io.BytesIO()
                        fmt = "JPEG" if pil_img.mode not in ("RGBA", "P") else "PNG"
                        pil_img.save(buf, format=fmt, quality=85)
                        img_bytes = buf.getvalue()
                        media_type = "image/jpeg" if fmt == "JPEG" else "image/png"
                    except Exception:
                        media_type = getattr(img_file, 'type', None)
                        if not media_type:
                            name = getattr(img_file, 'name', '').lower()
                            media_type = 'image/png' if name.endswith('.png') else 'image/jpeg'

                    b64 = base64.standard_b64encode(img_bytes).decode('utf-8')
                    content.append({
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": b64
                        }
                    })
                except Exception as img_err:
                    print(f"이미지 로드 에러: {img_err}")

        if prompt:
            content.append({"type": "text", "text": prompt})

        for attempt in range(max_retries):
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=8192,
                    messages=[{"role": "user", "content": content}]
                )
                text = response.content[0].text
                # 클로드가 응답을 마크다운 코드블록으로 감싸는 경우 제거
                text = re.sub(r'^```html?\s*\n?', '', text.strip())
                text = re.sub(r'\n?```\s*$', '', text.strip())
                return text
            except Exception as e:
                error_msg = str(e)
                if any(err in error_msg for err in ["529", "overloaded", "rate_limit", "429"]):
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 5
                        print(f"서버 혼잡. {wait_time}초 후 {attempt + 2}번째 재시도...")
                        time.sleep(wait_time)
                        continue
                return f"클로드 API 에러 발생: {error_msg}"
