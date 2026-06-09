class HTMLFormatter:

    TYPE_LABEL = {
        "리뷰":   "MK LINK REVIEW",
        "프리뷰": "MK LINK PREVIEW",
        "리스트": "MK LINK CURATION",
        "큐레이션": "MK LINK CURATION",
        "정주행": "MK LINK BINGE",
        "사진":   "MK LINK DAILY",
        "일상":   "MK LINK DAILY",
        "daily":  "MK LINK DAILY",
        "로컬소식": "MK LINK LOCAL",
    }

    def wrap_in_table(self, title, content, post_type=""):
        label = self.TYPE_LABEL.get(post_type, "MK LINK")
        html = f"""
        <div style="max-width: 800px; margin: 0 auto; font-family: 'NanumSquare', sans-serif; line-height: 1.8; color: #333; text-align: center;">

            <div style="padding: 40px 20px; border-bottom: 2px solid #222; margin-bottom: 30px;">
                <span style="font-size: 13px; color: #777; letter-spacing: 3px; font-weight: bold;">{label}</span>
                <h1 style="margin: 15px 0 0 0; color: #111; font-size: 26px; word-break: keep-all;">{title}</h1>
            </div>

            <div style="text-align: left; padding: 0 15px;">
                {content}
            </div>

            <div style="background-color: #f4f6f8; padding: 25px; border-radius: 12px; text-align: center; margin-top: 50px;">
                <p style="margin: 0; font-size: 15px; color: #333; font-weight: bold;">🔗 MK LINK의 다른 이야기가 궁금하다면?</p>
                <p style="margin: 10px 0 0 0; font-size: 13px; color: #0066cc; text-decoration: underline; cursor: pointer;">
                    [이곳에 이전 포스팅 링크를 삽입하세요]
                </p>
            </div>
        </div>
        """
        return html
