class HTMLFormatter:
    def wrap_in_table(self, title, content):
        # 지침 162, 163: 나눔스퀘어 폰트 강제 적용 및 중앙 정렬 구조
        html = f"""
        <div style="max-width: 800px; margin: 0 auto; font-family: 'NanumSquare', sans-serif; line-height: 1.8; color: #333; text-align: center;">
            
            <div style="padding: 40px 20px; border-bottom: 2px solid #222; margin-bottom: 30px;">
                <span style="font-size: 13px; color: #777; letter-spacing: 3px; font-weight: bold;">MK CINELAB PREVIEW</span>
                <h1 style="margin: 15px 0 0 0; color: #111; font-size: 26px; word-break: keep-all;">{title}</h1>
            </div>

            <div style="text-align: left; padding: 0 15px;">
                {content}
            </div>
            
            <div style="background-color: #f4f6f8; padding: 25px; border-radius: 12px; text-align: center; margin-top: 50px;">
                <p style="margin: 0; font-size: 15px; color: #333; font-weight: bold;">🎬 MK CINELAB의 다른 영화 이야기가 궁금하다면?</p>
                <p style="margin: 10px 0 0 0; font-size: 13px; color: #0066cc; text-decoration: underline; cursor: pointer;">
                    [이곳에 이전 포스팅 링크를 삽입하세요]
                </p>
            </div>
        </div>
        """
        return html